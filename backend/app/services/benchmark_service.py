from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from ..config import settings
from ..logging_config import get_logger
from ..models.schemas import BenchmarkResult


log = get_logger("service.benchmark")


class BenchmarkService:
    """
    Deterministic percentile computation from local market datasets.
    
    Supports both:
    - `backend/data/market_data.json` (single file)
    - `backend/data/market_data/**/*.json` (directory of JSON arrays/records)
    """

    # Minimal alias mapping to normalize role names
    ROLE_ALIASES = {
        "sde": "Software Engineer",
        "software developer": "Software Engineer",
        "developer": "Software Engineer",
        "backend engineer": "Backend Developer",
        "frontend engineer": "Frontend Developer",
        "fullstack engineer": "Fullstack Developer",
        "data scientist": "Data Scientist",
        "ml engineer": "Machine Learning Engineer",
    }

    # Role category normalization for market datasets that use `role_category`
    ROLE_CATEGORY_ALIASES = {
        "sde": "sde",
        "sde-1": "sde",
        "sde-2": "sde",
        "sde1": "sde",
        "sde2": "sde",
        "software engineer": "sde",
        "software development engineer": "sde",
        "developer": "sde",
        "backend": "sde",
        "frontend": "sde",
        "fullstack": "sde",
        "full stack": "sde",
        "junior": "sde",
        "entry": "sde",
        "fresher": "sde",
        "analyst": "analyst",
        "data analyst": "analyst",
        "business analyst": "analyst",
        "operations": "operations",
        "marketing": "marketing",
        "finance": "finance",
        "hr": "hr",
        "human resources": "hr",
    }

    def __init__(self) -> None:
        self._df = self._load_market_data()

    def _load_market_data(self) -> pd.DataFrame:
        """
        Loads and aggregates all JSON files from market_data_dir and market_data_path.
        """
        all_dfs = []
        
        # 1. Try legacy single file
        if hasattr(settings, "market_data_path") and settings.market_data_path.exists():
            try:
                df = pd.read_json(settings.market_data_path)
                if not df.empty:
                    df["_source_file"] = str(settings.market_data_path.name)
                    all_dfs.append(df)
                    log.info(f"Loaded market data from {settings.market_data_path}")
            except Exception as e:
                log.error(f"Error loading {settings.market_data_path}: {e}")

        # 2. Try directory (recursive)
        if settings.market_data_dir.exists() and settings.market_data_dir.is_dir():
            for json_file in settings.market_data_dir.rglob("*.json"):
                try:
                    df = pd.read_json(json_file)
                    if not df.empty:
                        df["_source_file"] = str(json_file.name)
                        all_dfs.append(df)
                        log.info(f"Loaded market data from {json_file}")
                except Exception as e:
                    log.error(f"Error loading {json_file}: {e}")

        if not all_dfs:
            log.warning("No market data found, benchmarking disabled")
            return pd.DataFrame()

        try:
            full_df = pd.concat(all_dfs, ignore_index=True)
            # Normalize common string columns to avoid .str crashes later
            for col in ["company_type", "role", "location", "city", "industry", "category"]:
                if col in full_df.columns:
                    full_df[col] = full_df[col].astype(str).fillna("")

            # Ensure salary column is numeric across all common candidates
            for col in ["salary_inr", "ctc_inr", "annual_ctc", "salary", "salary_annual"]:
                if col in full_df.columns:
                    full_df[col] = pd.to_numeric(full_df[col], errors="coerce")
            # Ensure notice column is numeric if present
            for col in ["notice_period_days", "notice_days", "notice_period"]:
                if col in full_df.columns:
                    full_df[col] = pd.to_numeric(full_df[col], errors="coerce")

            # Unify salary into `salary_inr` if only `salary_annual` exists.
            if "salary_inr" not in full_df.columns and "salary_annual" in full_df.columns:
                full_df["salary_inr"] = full_df["salary_annual"]
            elif "salary_annual" in full_df.columns:
                # keep both, but prefer salary_inr downstream
                full_df["salary_inr"] = full_df.get("salary_inr", full_df["salary_annual"])

            # Infer `company_type` from filename for datasets that don't include it.
            if "company_type" not in full_df.columns:
                full_df["company_type"] = ""
            if "_source_file" in full_df.columns:
                full_df["company_type"] = full_df["company_type"].fillna("").astype(str)
                missing_ct = full_df["company_type"].str.strip().eq("")
                if missing_ct.any():
                    full_df.loc[missing_ct, "company_type"] = full_df.loc[missing_ct, "_source_file"].apply(
                        self._infer_company_type_from_source
                    )

            # Normalize experience into [yoe_min, yoe_max] when only ranges exist (e.g., "0-2")
            if "experience_level" in full_df.columns and "yoe" not in full_df.columns:
                exp = full_df["experience_level"].astype(str).fillna("")
                mins: List[float | None] = []
                maxs: List[float | None] = []
                for s in exp.tolist():
                    lo, hi = self._parse_experience_range(s)
                    mins.append(lo)
                    maxs.append(hi)
                full_df["yoe_min"] = pd.to_numeric(pd.Series(mins), errors="coerce")
                full_df["yoe_max"] = pd.to_numeric(pd.Series(maxs), errors="coerce")

            # Normalize role_category if present
            if "role_category" in full_df.columns:
                full_df["role_category"] = full_df["role_category"].fillna("").astype(str).str.lower().str.strip()
            
            log.info(f"Market dataset initialized with {len(full_df)} records.")
            return full_df
        except Exception as exc:
            log.error(f"Failed to merge market data: {exc}")
            return pd.DataFrame()

    @staticmethod
    def _infer_company_type_from_source(source_file: str) -> str:
        s = (source_file or "").lower()
        for ct in ("product", "service", "startup"):
            if ct in s:
                return ct
        return ""

    @staticmethod
    def _parse_experience_range(s: str) -> tuple[float | None, float | None]:
        """
        Accepts strings like: "0-2", "2 - 5", "5-10", "3", "3+", "fresher"
        Returns (min, max) in years.
        """
        t = (s or "").strip().lower()
        if not t:
            return None, None
        if "fresh" in t:
            return 0.0, 1.0
        m = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", t)
        if m:
            return float(m.group(1)), float(m.group(2))
        m = re.search(r"(\d+(?:\.\d+)?)\s*\+", t)
        if m:
            return float(m.group(1)), float(m.group(1)) + 3.0
        m = re.search(r"(\d+(?:\.\d+)?)", t)
        if m:
            v = float(m.group(1))
            return v, v
        return None, None

    def _normalize_role_category(self, role: str) -> Optional[str]:
        r = (role or "").lower().strip()
        if not r:
            return None
        return self.ROLE_CATEGORY_ALIASES.get(r, None)

    def compare_salary(
        self, 
        ctc_inr: float, 
        role: str, 
        yoe: float, 
        company_type: str,
        location: Optional[str] = None,
        industry: Optional[str] = None
    ) -> BenchmarkResult:
        """
        4-step cohort broadening logic as per Vision:
        1. Filter by: industry, role_level, location, salary.
        2. If N < 30: Remove location.
        3. If N < 30: Broaden role_level (+/- 2 years).
        4. If N < 30: Broaden industry.
        5. Fall back to national (all roles in category).
        """
        if self._df.empty:
            log.warning("Benchmark: Market data DataFrame is empty")
            return self._empty_result("Market data unavailable")
        
        log.info(f"Benchmark: Starting comparison for ctc={ctc_inr}, role={role}, yoe={yoe}, company_type={company_type}, location={location}")
        log.info(f"Benchmark: Total market records available: {len(self._df)}")

        norm_role = self.ROLE_ALIASES.get((role or "").lower().strip(), (role or "").strip())
        sal_col = self._find_col(["salary_inr", "ctc_inr", "annual_ctc", "salary", "salary_annual"])
        loc_col = self._find_col(["location", "city"])
        ind_col = self._find_col(["industry", "category"])
        
        log.info(f"Benchmark: Found columns - salary={sal_col}, location={loc_col}, industry={ind_col}")

        if not sal_col:
            log.error("Benchmark: No salary column found in market data")
            return self._empty_result(
                "Market data missing salary column (expected one of salary_inr/salary_annual/ctc_inr/annual_ctc/salary)",
                filters={"role": norm_role, "company_type": company_type},
                steps=["benchmark_disabled_missing_salary_column"],
            )
        
        # Keep this backward-compatible with the frontend (`filters_used.company_type`, etc.)
        filters_used = {
            "role": norm_role,
            "company_type": company_type,
        }
        broaden_steps = []

        curr_df = self._df

        # Step 0: Role filter (prefer role_category if present)
        role_cat = self._normalize_role_category(role)
        if role_cat and "role_category" in curr_df.columns:
            role_mask = curr_df["role_category"].fillna("").astype(str).str.lower().str.strip() == role_cat
            if int(role_mask.sum()) >= 5:
                curr_df = curr_df[role_mask]
                filters_used["role_category"] = role_cat
            else:
                broaden_steps.append("role_category_insufficient_fallback_to_role_text")
        if "role_category" not in filters_used and "role" in curr_df.columns and norm_role:
            # Fuzzy-ish match for roles like "SDE-1", "Software Development Engineer", etc.
            role_text = curr_df["role"].fillna("").astype(str).str.lower()
            tokens = [t for t in re.split(r"[^a-z0-9]+", norm_role.lower()) if t]
            if tokens:
                role_mask = role_text.apply(lambda x: all(t in x for t in tokens))
                if int(role_mask.sum()) >= 5:
                    curr_df = curr_df[role_mask]
                    filters_used["role_text_tokens"] = tokens
                else:
                    return self._empty_result(
                        f"Insufficient market data for role: '{role}'",
                        filters=filters_used,
                        steps=broaden_steps + ["role_not_found_in_market_data"]
                    )
            else:
                return self._empty_result(
                    f"Invalid role name: '{role}'",
                    filters=filters_used,
                    steps=broaden_steps + ["invalid_role_name"]
                )
        
        # At this point, curr_df SHOULD be filtered by role. 
        # If it's still the full dataset (neither category nor text matched but didn't return), that's an error.
        if "role_category" not in filters_used and "role_text_tokens" not in filters_used:
             return self._empty_result(
                f"Could not identify role cohort for '{role}'",
                filters=filters_used,
                steps=broaden_steps + ["no_role_match"]
            )

        # Step 1: Company type filter (skip if dataset doesn't support it)
        if company_type and "company_type" in curr_df.columns:
            ct_mask = curr_df["company_type"].fillna("").astype(str).str.lower().str.strip() == company_type.lower()
            if int(ct_mask.sum()) >= 5:
                curr_df = curr_df[ct_mask]
                filters_used["company_type"] = company_type
            else:
                broaden_steps.append("removed_company_type_constraint")

        # Step 1: Location Filter (Relax if N < 30)
        if location and loc_col:
            loc_mask = curr_df[loc_col].fillna("").astype(str).str.lower().str.strip() == location.lower()
            if int(loc_mask.sum()) >= 5:
                curr_df = curr_df[loc_mask]
                filters_used["location"] = location
            else:
                broaden_steps.append("removed_location_constraint")

        # Step 2: Experience filter
        # Prefer explicit numeric years column if available; else use yoe_min/yoe_max derived from ranges.
        exp_num_col = self._find_col(["yoe", "experience_years", "experience"])
        if exp_num_col and exp_num_col in curr_df.columns:
            exp_mask = (curr_df[exp_num_col] >= yoe - 1) & (curr_df[exp_num_col] <= yoe + 1)
            if int(exp_mask.sum()) >= 5:
                curr_df = curr_df[exp_mask]
                filters_used["yoe_window"] = f"{yoe-1:.1f}..{yoe+1:.1f}"
            else:
                broaden_steps.append("removed_experience_constraint")
        elif "yoe_min" in curr_df.columns and "yoe_max" in curr_df.columns:
            exp_mask = (curr_df["yoe_min"].isna() | (curr_df["yoe_min"] <= yoe)) & (curr_df["yoe_max"].isna() | (curr_df["yoe_max"] >= yoe))
            if int(exp_mask.sum()) >= 5:
                curr_df = curr_df[exp_mask]
                filters_used["yoe_in_range"] = True
            else:
                broaden_steps.append("removed_experience_constraint")

        # Step 3: Industry Filter (Relax if N < 30)
        if industry and ind_col:
            ind_mask = curr_df[ind_col].fillna("").astype(str).str.lower() == industry.lower()
            if int(ind_mask.sum()) >= 5:
                curr_df = curr_df[ind_mask]
                filters_used["industry"] = industry
            else:
                broaden_steps.append("broadened_industry_category")

        if curr_df.empty or len(curr_df) < 5:
            return self._empty_result(
                f"Insufficient cohort after filters for role='{role}'",
                filters=filters_used,
                steps=broaden_steps + ["insufficient_after_filters"],
            )

        salaries = curr_df[sal_col].dropna().to_numpy()
        cohort_size = int(salaries.size)
        
        if cohort_size == 0:
            log.warning("Benchmark: No salary data found in filtered cohort")
            return self._empty_result("No salary data found in cohort", filters_used, broaden_steps)

        percentile = float((salaries <= ctc_inr).sum() / cohort_size * 100.0)
        
        log.info(f"Benchmark: Computed percentile={percentile:.1f}% from cohort of {cohort_size} records")
        log.info(f"Benchmark: Market stats - mean={np.mean(salaries):.0f}, median={np.median(salaries):.0f}, p25={np.percentile(salaries, 25):.0f}, p75={np.percentile(salaries, 75):.0f}")
        
        return BenchmarkResult(
            percentile_salary=percentile,
            cohort_size=cohort_size,
            filters_used=filters_used,
            broaden_steps=broaden_steps,
            market_mean=float(np.mean(salaries)),
            market_median=float(np.median(salaries)),
            market_p25=float(np.percentile(salaries, 25)),
            market_p75=float(np.percentile(salaries, 75))
        )

    def _find_col(self, candidates: List[str]) -> Optional[str]:
        for c in candidates:
            if c in self._df.columns:
                return c
        return None

    def compute_notice_percentile(
        self,
        notice_days: int,
        company_type: str
    ) -> Optional[float]:
        """
        Compute percentile for notice period.
        Lower notice = lower percentile = BETTER for candidate.
        """
        if self._df.empty:
            return None
            
        notice_col = self._find_col(["notice_period_days", "notice_days", "notice_period"])
        if not notice_col:
            return None
            
        # Filter by company type (if possible)
        if "company_type" in self._df.columns:
            cohort = self._df[self._df["company_type"].fillna("").astype(str).str.lower() == company_type.lower()]
        else:
            cohort = self._df
        
        if len(cohort) < 5:
            cohort = self._df  # Use all data if cohort too small
            
        notices = cohort[notice_col].dropna().to_numpy()
        if notices.size == 0:
            return None
            
        # Percentile: what % of contracts have notice <= yours
        percentile = float((notices <= notice_days).sum() / notices.size * 100.0)
        return percentile

    def get_notice_stats(self, company_type: str) -> Dict[str, float]:
        """
        Get notice period statistics for context.
        """
        if self._df.empty:
            return {}
            
        notice_col = self._find_col(["notice_period_days", "notice_days", "notice_period"])
        if not notice_col:
            return {}
            
        if "company_type" in self._df.columns:
            cohort = self._df[self._df["company_type"].fillna("").astype(str).str.lower() == company_type.lower()]
        else:
            cohort = self._df
        if len(cohort) < 5:
            cohort = self._df
            
        notices = cohort[notice_col].dropna().to_numpy()
        if notices.size == 0:
            return {}
            
        return {
            "mean": float(np.mean(notices)),
            "median": float(np.median(notices)),
            "p25": float(np.percentile(notices, 25)),
            "p75": float(np.percentile(notices, 75))
        }

    def get_industry_standards(self, industry: str) -> Dict[str, Any]:
        """
        Load industry standards from market_intelligence directory.
        """
        standards_path = settings.market_intel_dir / "industry_standards.json"
        if not standards_path.exists():
            # Fallback hardcoded defaults if file missing
            default = {
                "tech": {"notice_days": 60, "probation_months": 6, "non_compete_months": 12},
                "finance": {"notice_days": 90, "probation_months": 6, "non_compete_months": 24},
            }
            return default.get(industry.lower(), {})
            
        try:
            standards = json.loads(standards_path.read_text())
            return standards.get(industry.lower(), {})
        except Exception as e:
            log.error(f"Error loading industry standards: {e}")
            return {}

    def _empty_result(self, warning: str, filters: Optional[dict] = None, steps: Optional[list] = None) -> BenchmarkResult:
        filters = filters or {}
        steps = steps or []
        return BenchmarkResult(
            percentile_salary=None,
            percentile_notice=None,
            cohort_size=0,
            filters_used=filters,
            broaden_steps=steps,
            market_mean=0,
            market_median=0,
            market_p25=0,
            market_p75=0,
            warning=warning
        )

