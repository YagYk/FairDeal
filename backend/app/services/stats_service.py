"""
Statistics service for computing market statistics and percentiles.
Analyzes the contract database to provide comparative insights.
"""
from typing import Dict, List, Any, Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import ContractAnalysis
from app.db.chroma_client import ChromaClient
import json
from pathlib import Path
from app.config import settings


class StatsService:
    """
    Service for computing market statistics and percentiles.
    
    Computes:
    - Percentiles for numeric fields (salary, notice_period_days)
    - Frequency statistics for categorical fields
    - Market averages and medians
    """
    
    def __init__(self):
        self.chroma_client = ChromaClient()
    
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
        Compute percentile ranking for a numeric value.
        
        Args:
            value: The value to rank
            field_name: Field name (e.g., 'salary', 'notice_period_days')
            contract_type: Optional filter by contract type
            industry: Optional filter by industry
            role: Optional filter by role
            location: Optional filter by location
            
        Returns:
            Percentile (0-100) where 0 is lowest, 100 is highest
        """
        logger.info(f"Computing percentile for {field_name}={value}")
        
        # Get all contracts from processed metadata
        all_values = self._get_field_values(
            field_name=field_name,
            contract_type=contract_type,
            industry=industry,
            role=role,
            location=location,
        )
        
        if not all_values:
            logger.warning(f"No data found for {field_name}, returning 50th percentile")
            return 50.0
        
        # Filter out None/0 values (missing data)
        valid_values = [v for v in all_values if v is not None and v > 0]
        
        if not valid_values:
            return 50.0
        
        # Sort values
        sorted_values = sorted(valid_values)
        
        # Count how many values are less than or equal to the input value
        count_below = sum(1 for v in sorted_values if v <= value)
        
        # Compute percentile
        percentile = (count_below / len(sorted_values)) * 100
        
        logger.info(f"Percentile for {field_name}={value}: {percentile:.1f}%")
        return round(percentile, 1)
    
    def _extract_value(self, item: Any) -> Any:
        """Helper to extract value from either raw format or ExtractedField dict."""
        if isinstance(item, dict):
            # Try to find 'value' key, otherwise assumed to be not a value-object
            if "value" in item:
                return item.get("value")
            # If it's a dict but has no 'value' key, it might be a nested object or error
            # For stats purposes, we can't usage a dict as a number, so return None
            return None
        return item

    def compute_frequency(
        self,
        clause_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
    ) -> float:
        """
        Compute frequency percentage for a categorical clause.
        
        Args:
            clause_name: Name of clause (e.g., 'non_compete', 'termination_clauses')
            contract_type: Optional filter
            industry: Optional filter
            location: Optional filter
            
        Returns:
            Frequency percentage (0-100)
        """
        logger.info(f"Computing frequency for clause: {clause_name}")
        
        # Get all contracts
        all_contracts = self._get_all_contracts_metadata(
            contract_type=contract_type,
            industry=industry,
            location=location,
        )
        
        if not all_contracts:
            return 0.0
        
        # Count contracts with this clause
        count_with_clause = 0
        for contract in all_contracts:
            metadata = contract.get("metadata", {})
            
            non_compete_val = self._extract_value(metadata.get("non_compete"))
            clause_val = self._extract_value(metadata.get(clause_name))

            if clause_name == "non_compete":
                if non_compete_val:
                    count_with_clause += 1
            elif clause_name in metadata:
                if clause_val:
                    count_with_clause += 1
        
        frequency = (count_with_clause / len(all_contracts)) * 100
        logger.info(f"Frequency for {clause_name}: {frequency:.1f}%")
        return round(frequency, 1)
    
    def get_market_statistics(
        self,
        field_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive market statistics for a field.
        
        Returns:
            Dictionary with mean, median, min, max, IQR, percentiles
        """
        all_values = self._get_field_values(
            field_name=field_name,
            contract_type=contract_type,
            industry=industry,
            role=role,
            location=location,
        )
        
        valid_values = [v for v in all_values if v is not None and v > 0]
        
        if not valid_values:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "p25": 0,
                "p75": 0,
                "iqr": 0,
            }
        
        sorted_values = sorted(valid_values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "mean": round(sum(sorted_values) / n, 2),
            "median": sorted_values[n // 2] if n > 0 else 0,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p25": sorted_values[n // 4] if n >= 4 else sorted_values[0],
            "p75": sorted_values[3 * n // 4] if n >= 4 else sorted_values[-1],
            "iqr": sorted_values[3 * n // 4] - sorted_values[n // 4] if n >= 4 else 0,
        }
    
    def _get_field_values(
        self,
        field_name: str,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[float]:
        """Get all values for a field from processed contracts."""
        all_contracts = self._get_all_contracts_metadata(
            contract_type=contract_type,
            industry=industry,
            role=role,
            location=location,
        )
        
        values = []
        for contract in all_contracts:
            metadata = contract.get("metadata", {})
            raw_val = metadata.get(field_name)
            value = self._extract_value(raw_val)
            
            if value is not None:
                if isinstance(value, (int, float)):
                     values.append(float(value))
                elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                     values.append(float(value))
                # Explicitly ignore dicts or other types that slip through

        
        return values
    
    def _get_all_contracts_metadata(
        self,
        contract_type: Optional[str] = None,
        industry: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Load all processed contract metadata from disk.
        
        This reads from the processed_contracts_path directory.
        """
        processed_dir = settings.get_processed_contracts_path()
        
        if not processed_dir.exists():
            logger.warning(f"Processed contracts directory not found: {processed_dir}")
            return []
        
        contracts = []
        for metadata_file in processed_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    contract_data = json.load(f)
                
                # Apply filters
                metadata = contract_data.get("metadata", {})
                
                m_type = self._extract_value(metadata.get("contract_type"))
                m_industry = self._extract_value(metadata.get("industry"))
                m_role = self._extract_value(metadata.get("role"))
                m_location = self._extract_value(metadata.get("location"))
                
                if contract_type and m_type != contract_type:
                    continue
                if industry and m_industry != industry:
                    continue
                if role and m_role != role:
                    continue
                if location and m_location != location:
                    continue
                
                contracts.append(contract_data)
            except Exception as e:
                logger.error(f"Error loading {metadata_file}: {e}")
        
        return contracts

