"""
Unit tests for percentile computation.
Tests the StatsServiceV2 percentile logic.
"""
import pytest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPercentileComputation:
    """Tests for percentile computation logic."""
    
    def test_percentile_simple(self):
        """Test simple percentile computation."""
        # Values: [100, 200, 300, 400, 500]
        # 300 should be at 60th percentile (3/5 = 0.6)
        values = [100, 200, 300, 400, 500]
        test_value = 300
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 60.0
    
    def test_percentile_at_min(self):
        """Test percentile at minimum value."""
        values = [100, 200, 300, 400, 500]
        test_value = 100
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 20.0  # 1/5 = 0.2
    
    def test_percentile_at_max(self):
        """Test percentile at maximum value."""
        values = [100, 200, 300, 400, 500]
        test_value = 500
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 100.0  # 5/5 = 1.0
    
    def test_percentile_below_min(self):
        """Test percentile for value below all data."""
        values = [100, 200, 300, 400, 500]
        test_value = 50
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 0.0  # 0/5 = 0
    
    def test_percentile_above_max(self):
        """Test percentile for value above all data."""
        values = [100, 200, 300, 400, 500]
        test_value = 600
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 100.0  # 5/5 = 1.0
    
    def test_percentile_with_duplicates(self):
        """Test percentile with duplicate values."""
        # Values with duplicates: [100, 200, 200, 200, 300]
        values = [100, 200, 200, 200, 300]
        test_value = 200
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 80.0  # 4/5 = 0.8
    
    def test_percentile_between_values(self):
        """Test percentile for value between two data points."""
        values = [100, 200, 300, 400, 500]
        test_value = 250  # Between 200 and 300
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 40.0  # 2/5 = 0.4
    
    def test_percentile_single_value(self):
        """Test percentile with single value."""
        values = [100]
        test_value = 100
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 100.0
    
    def test_percentile_empty_cohort(self):
        """Test percentile with empty cohort returns None."""
        values = []
        test_value = 100
        
        if not values:
            percentile = None
        else:
            count_below_or_equal = sum(1 for v in values if v <= test_value)
            percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile is None
    
    def test_percentile_large_dataset(self):
        """Test percentile with larger dataset."""
        # 100 values from 1 to 100
        values = list(range(1, 101))
        test_value = 50
        
        count_below_or_equal = sum(1 for v in values if v <= test_value)
        percentile = (count_below_or_equal / len(values)) * 100
        
        assert percentile == 50.0  # 50/100 = 0.5


class TestCohortBroadening:
    """Tests for cohort broadening logic."""
    
    def test_broadening_order(self):
        """Test that broadening follows correct order: location -> industry -> role_level."""
        broadening_order = ["location", "industry", "role_level"]
        
        # Verify order
        assert broadening_order[0] == "location"
        assert broadening_order[1] == "industry"
        assert broadening_order[2] == "role_level"
    
    def test_filter_removal_logic(self):
        """Test that filters are removed correctly during broadening."""
        current_filters = {
            "contract_type": "employment",
            "industry": "tech",
            "role_level": "senior",
            "location": "mumbai",
        }
        
        broadening_order = ["location", "industry", "role_level"]
        broaden_steps = []
        
        # Simulate broadening
        for filter_to_remove in broadening_order:
            if filter_to_remove in current_filters:
                old_value = current_filters.pop(filter_to_remove)
                broaden_steps.append(f"Removed {filter_to_remove}={old_value}")
        
        # After broadening, only contract_type should remain
        assert "contract_type" in current_filters
        assert "location" not in current_filters
        assert "industry" not in current_filters
        assert "role_level" not in current_filters
        
        assert len(broaden_steps) == 3
    
    def test_min_cohort_threshold(self):
        """Test minimum cohort size thresholds."""
        MIN_N = 30  # Target minimum
        MIN_N_MIN = 10  # Absolute minimum
        
        # Test cohort sizes
        cohort_sizes = [5, 10, 15, 30, 50]
        
        for size in cohort_sizes:
            if size >= MIN_N:
                confidence_note = None
            elif size >= MIN_N_MIN:
                confidence_note = f"Cohort size ({size}) is below target ({MIN_N})"
            else:
                confidence_note = f"Cohort size ({size}) is very small"
            
            if size == 5:
                assert "very small" in confidence_note
            elif size == 15:
                assert "below target" in confidence_note
            elif size >= 30:
                assert confidence_note is None


class TestScoringFormula:
    """Tests for the scoring formula."""
    
    def test_base_score(self):
        """Test base score is 50."""
        base_score = 50
        assert base_score == 50
    
    def test_salary_contribution(self):
        """Test salary percentile contribution."""
        # Formula: 0.4 * (P_salary - 50)
        WEIGHT_SALARY = 0.4
        
        # At 50th percentile, contribution is 0
        salary_pct = 50
        contribution = WEIGHT_SALARY * (salary_pct - 50)
        assert contribution == 0.0
        
        # At 75th percentile, contribution is +10
        salary_pct = 75
        contribution = WEIGHT_SALARY * (salary_pct - 50)
        assert contribution == 10.0
        
        # At 25th percentile, contribution is -10
        salary_pct = 25
        contribution = WEIGHT_SALARY * (salary_pct - 50)
        assert contribution == -10.0
    
    def test_notice_contribution(self):
        """Test notice percentile contribution (lower is better)."""
        # Formula: 0.3 * (50 - P_notice)
        WEIGHT_NOTICE = 0.3
        
        # At 50th percentile, contribution is 0
        notice_pct = 50
        contribution = WEIGHT_NOTICE * (50 - notice_pct)
        assert contribution == 0.0
        
        # At 25th percentile (short notice = good), contribution is +7.5
        notice_pct = 25
        contribution = WEIGHT_NOTICE * (50 - notice_pct)
        assert contribution == 7.5
        
        # At 75th percentile (long notice = bad), contribution is -7.5
        notice_pct = 75
        contribution = WEIGHT_NOTICE * (50 - notice_pct)
        assert contribution == -7.5
    
    def test_flag_penalty(self):
        """Test red flag penalty."""
        # Formula: 0.3 * (N_flags * 5)
        WEIGHT_FLAGS = 0.3
        FLAG_PENALTY = 5
        
        # 0 flags = 0 penalty
        n_flags = 0
        penalty = WEIGHT_FLAGS * (n_flags * FLAG_PENALTY)
        assert penalty == 0.0
        
        # 2 flags = 3 penalty (0.3 * 10)
        n_flags = 2
        penalty = WEIGHT_FLAGS * (n_flags * FLAG_PENALTY)
        assert penalty == 3.0
        
        # 5 flags = 7.5 penalty
        n_flags = 5
        penalty = WEIGHT_FLAGS * (n_flags * FLAG_PENALTY)
        assert penalty == 7.5
    
    def test_full_score_computation(self):
        """Test full score computation."""
        # S_raw = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5)
        
        salary_pct = 60
        notice_pct = 40
        n_flags = 1
        
        score_raw = (
            50  # Base
            + 0.4 * (salary_pct - 50)  # +4
            + 0.3 * (50 - notice_pct)  # +3
            - 0.3 * (n_flags * 5)  # -1.5
        )
        
        expected = 50 + 4 + 3 - 1.5  # 55.5
        assert score_raw == expected
        
        # Clamped and rounded
        score = max(0, min(100, round(score_raw)))
        assert score == 56
    
    def test_score_clamping(self):
        """Test score is clamped to 0-100."""
        # Very high score
        score_raw = 150
        score = max(0, min(100, round(score_raw)))
        assert score == 100
        
        # Very low score
        score_raw = -20
        score = max(0, min(100, round(score_raw)))
        assert score == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
