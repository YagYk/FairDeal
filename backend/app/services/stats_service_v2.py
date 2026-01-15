"""
Refactored Statistics Service with proper cohort broadening logic.
Computes percentiles and market statistics from the knowledge base.

Cohort Selection Logic:
1. Start with strict filters: contract_type + role_level + industry + location
2. If cohort_size < MIN_N (30), broaden in order: location → industry → role_level
3. Always keep contract_type filter
4. Return cohort_size and filters_used + broaden_steps
"""
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger
from pathlib import Path
import json
import numpy as np

from app.config import settings
from app.models.schemas import CohortInfo, PercentileInfo


class StatsServiceV2:
    """
    Statistics service for computing market statistics and percentiles.
    Implements proper cohort broadening for robust comparisons.
    """
    
    # Minimum cohort sizes
    MIN_N = 30  # Target minimum cohort size
    MIN_N_MIN = 10  # Absolute minimum (show warning below this)
    
    # Broadening order (from most specific to least)
    BROADENING_ORDER = ["location", "industry", "role_level"]
    
    def __init__(self):
        """Initialize the stats service."""
        self._contracts_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_loaded = False
    
    def _load_contracts(self) -> List[Dict[str, Any]]:
        """Load all processed contract metadata from disk."""
        if self._cache_loaded:
            return self._contracts_cache or []
        
        processed_dir = settings.get_processed_contracts_path()
        
        if not processed_dir.exists():
            logger.warning(f"Processed contracts directory not found: {processed_dir}")
            self._contracts_cache = []
            self._cache_loaded = True
            return []
        
        contracts = []
        for metadata_file in processed_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    contract_data = json.load(f)
                contracts.append(contract_data)
            except Exception as e:
                logger.error(f"Error loading {metadata_file}: {e}")
        
        logger.info(f"Loaded {len(contracts)} contracts from processed directory")
        self._contracts_cache = contracts
        self._cache_loaded = True
        return contracts
    
    def invalidate_cache(self):
        """Invalidate the contracts cache (call after ingestion)."""
        self._contracts_cache = None
        self._cache_loaded = False
    
    def _extract_value(self, item: Any) -> Any:
        """Helper to extract value from ExtractedField dict or raw value."""
        if isinstance(item, dict):
            if "value" in item:
                return item.get("value")
            return None
        return item
    
    def compute_percentile_with_cohort(
        self,
        value: float,
        field_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role_level: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Tuple[PercentileInfo, CohortInfo]:
        """
        Compute percentile with proper cohort selection and broadening.
        
        Args:
            value: The value to rank
            field_name: Field name (e.g., 'salary_in_inr', 'notice_period_days')
            contract_type: Contract type filter
            industry: Industry filter
            role_level: Role level filter
            location: Location filter
            
        Returns:
            Tuple of (PercentileInfo, CohortInfo)
        """
        logger.info(f"Computing percentile for {field_name}={value}")
        
        all_contracts = self._load_contracts()
        
        if not all_contracts:
            return (
                PercentileInfo(value=None, field_value=value, cohort_size=0),
                CohortInfo(filters_used={}, cohort_size=0, confidence_note="No contracts in knowledge base")
            )
        
        # Build initial filters
        filters = {}
        if contract_type:
            filters["contract_type"] = contract_type
        if industry:
            filters["industry"] = industry
        if role_level:
            filters["role_level"] = role_level
        if location:
            filters["location"] = location
        
        # Try to find cohort with broadening
        cohort_values, used_filters, broaden_steps = self._find_cohort_with_broadening(
            all_contracts=all_contracts,
            field_name=field_name,
            initial_filters=filters,
        )
        
        cohort_size = len(cohort_values)
        
        # Build confidence note
        confidence_note = None
        if cohort_size < self.MIN_N_MIN:
            confidence_note = f"Cohort size ({cohort_size}) is very small. Results may not be reliable."
        elif cohort_size < self.MIN_N:
            confidence_note = f"Cohort size ({cohort_size}) is below target ({self.MIN_N}). Results are indicative."
        
        # Compute percentile
        if cohort_size == 0:
            percentile = None
            value_range = None
        else:
            sorted_values = sorted(cohort_values)
            count_below = sum(1 for v in sorted_values if v <= value)
            percentile = (count_below / len(sorted_values)) * 100
            value_range = f"{min(sorted_values):,.0f} - {max(sorted_values):,.0f}"
        
        # Build results
        percentile_info = PercentileInfo(
            value=round(percentile, 1) if percentile is not None else None,
            field_value=value,
            cohort_size=cohort_size,
            comparable_values_range=value_range,
        )
        
        cohort_info = CohortInfo(
            filters_used=used_filters,
            cohort_size=cohort_size,
            broaden_steps=broaden_steps,
            min_n=self.MIN_N,
            confidence_note=confidence_note,
        )
        
        logger.info(f"Percentile for {field_name}={value}: {percentile_info.value}% (cohort: {cohort_size})")
        
        return percentile_info, cohort_info
    
    def _find_cohort_with_broadening(
        self,
        all_contracts: List[Dict[str, Any]],
        field_name: str,
        initial_filters: Dict[str, str],
    ) -> Tuple[List[float], Dict[str, str], List[str]]:
        """
        Find a cohort of sufficient size, broadening filters if needed.
        
        Returns:
            Tuple of (field_values, used_filters, broaden_steps)
        """
        current_filters = initial_filters.copy()
        broaden_steps = []
        
        # Try with current filters
        values = self._get_field_values_filtered(all_contracts, field_name, current_filters)
        
        # Broaden if needed
        for filter_to_remove in self.BROADENING_ORDER:
            if len(values) >= self.MIN_N:
                break
            
            if filter_to_remove in current_filters:
                old_value = current_filters.pop(filter_to_remove)
                broaden_steps.append(f"Removed {filter_to_remove}={old_value}")
                values = self._get_field_values_filtered(all_contracts, field_name, current_filters)
                logger.debug(f"Broadened: removed {filter_to_remove}, cohort now {len(values)}")
        
        # If still too small and we have contract_type, try without it too
        # But contract_type is supposed to always be kept... let's keep at least some filter
        # If everything is removed and still small, just use what we have
        
        return values, current_filters, broaden_steps
    
    def _get_field_values_filtered(
        self,
        all_contracts: List[Dict[str, Any]],
        field_name: str,
        filters: Dict[str, str],
    ) -> List[float]:
        """Get all values for a field matching the filters."""
        values = []
        
        # Map API field names to metadata field names
        field_mapping = {
            "salary_in_inr": ["salary_in_inr", "salary"],
            "salary": ["salary_in_inr", "salary"],
            "notice_period_days": ["notice_period_days"],
        }
        
        possible_fields = field_mapping.get(field_name, [field_name])
        
        for contract_data in all_contracts:
            metadata = contract_data.get("metadata", {})
            
            # Check filters
            if not self._matches_filters(metadata, filters):
                continue
            
            # Extract field value
            value = None
            for possible_field in possible_fields:
                raw_val = metadata.get(possible_field)
                value = self._extract_value(raw_val)
                if value is not None:
                    break
            
            # Validate and add
            if value is not None:
                try:
                    float_val = float(value)
                    if float_val > 0:  # Filter out zeros and negatives
                        values.append(float_val)
                except (ValueError, TypeError):
                    continue
        
        return values
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, str]) -> bool:
        """Check if metadata matches all filters."""
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue
            
            # Map filter keys to metadata keys
            if filter_key == "role_level":
                meta_keys = ["role_level", "role"]
            else:
                meta_keys = [filter_key]
            
            meta_value = None
            for meta_key in meta_keys:
                raw_val = metadata.get(meta_key)
                meta_value = self._extract_value(raw_val)
                if meta_value:
                    break
            
            if not meta_value:
                continue  # Missing value in metadata - might still match
            
            # Case-insensitive comparison
            if str(meta_value).lower() != str(filter_value).lower():
                return False
        
        return True
    
    def get_market_statistics(
        self,
        field_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role_level: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive market statistics for a field.
        
        Returns:
            Dictionary with count, mean, median, min, max, p25, p75, iqr
        """
        all_contracts = self._load_contracts()
        
        filters = {}
        if contract_type:
            filters["contract_type"] = contract_type
        if industry:
            filters["industry"] = industry
        if role_level:
            filters["role_level"] = role_level
        if location:
            filters["location"] = location
        
        values = self._get_field_values_filtered(all_contracts, field_name, filters)
        
        if not values:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "p25": 0,
                "p75": 0,
                "iqr": 0,
                "filters_used": filters,
            }
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        arr = np.array(sorted_values)
        
        return {
            "count": n,
            "mean": round(float(np.mean(arr)), 2),
            "median": round(float(np.median(arr)), 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
            "p25": round(float(np.percentile(arr, 25)), 2),
            "p75": round(float(np.percentile(arr, 75)), 2),
            "iqr": round(float(np.percentile(arr, 75) - np.percentile(arr, 25)), 2),
            "filters_used": filters,
        }
    
    def get_cohort_counts(self) -> Dict[str, int]:
        """Get counts for all possible cohorts."""
        all_contracts = self._load_contracts()
        
        counts = {
            "total": len(all_contracts),
        }
        
        # Count by contract type
        type_counts: Dict[str, int] = {}
        industry_counts: Dict[str, int] = {}
        role_counts: Dict[str, int] = {}
        
        for contract in all_contracts:
            metadata = contract.get("metadata", {})
            
            ct = self._extract_value(metadata.get("contract_type")) or "unknown"
            type_counts[ct] = type_counts.get(ct, 0) + 1
            
            ind = self._extract_value(metadata.get("industry")) or "unknown"
            industry_counts[ind] = industry_counts.get(ind, 0) + 1
            
            role = self._extract_value(metadata.get("role_level")) or self._extract_value(metadata.get("role")) or "unknown"
            role_counts[role] = role_counts.get(role, 0) + 1
        
        counts["by_type"] = type_counts
        counts["by_industry"] = industry_counts
        counts["by_role"] = role_counts
        
        return counts
    
    def compute_percentile(
        self,
        value: float,
        field_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
    ) -> float:
        """
        Compute percentile ranking for a numeric value (legacy interface).
        
        Args:
            value: The value to rank
            field_name: Field name
            contract_type: Optional filter
            industry: Optional filter
            role: Optional filter (treated as role_level)
            location: Optional filter
            
        Returns:
            Percentile (0-100) where 0 is lowest, 100 is highest
        """
        percentile_info, _ = self.compute_percentile_with_cohort(
            value=value,
            field_name=field_name,
            contract_type=contract_type,
            industry=industry,
            role_level=role,
            location=location,
        )
        
        return percentile_info.value if percentile_info.value is not None else 50.0
