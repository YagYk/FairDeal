"""
FAIRDEAL Validation Metrics Engine

Systematic validation of the psychological scoring engine with:
- Per-test-case scoring validation
- Score distribution statistics
- Inter-category discrimination tests
- Feature-score correlation analysis
- Known ordering compliance
- Determinism verification
"""

from __future__ import annotations

import math
import time
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from ..services.psychological_scoring import PsychologicalScoringEngine
from .ground_truth import SCORING_TEST_CASES, KNOWN_ORDERINGS

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ═══════════════════════════════════════════════════════════════════
# RESULT DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScoringTestResult:
    id: str
    name: str
    category: str
    company: str
    ctc_inr: int
    expected_range: List[float]
    actual_score: float
    grade: str
    passed: bool
    badges: List[str]
    risk_factors: List[str]
    breakdown: Dict[str, Any]
    confidence: float


@dataclass
class ScoreDistribution:
    mean: float
    median: float
    std_dev: float
    min_score: float
    max_score: float
    q1: float
    q3: float
    iqr: float
    skewness: float
    kurtosis: float
    range_span: float


@dataclass
class CategoryComparison:
    category_a: str
    category_b: str
    mean_a: float
    mean_b: float
    std_a: float
    std_b: float
    n_a: int
    n_b: int
    t_statistic: float
    p_value_approx: float
    significant: bool
    effect_size: float


@dataclass
class CorrelationResult:
    feature: str
    pearson_r: float
    direction: str
    strength: str


@dataclass
class EvaluationReport:
    timestamp: str
    engine_version: str
    total_test_cases: int
    evaluation_time_ms: float

    scoring_pass_rate: float
    scoring_results: List[ScoringTestResult]

    score_distribution: ScoreDistribution
    grade_distribution: Dict[str, int]
    category_means: Dict[str, float]

    category_comparisons: List[CategoryComparison]
    feature_correlations: List[CorrelationResult]

    known_ordering_total: int
    known_ordering_correct: int
    known_ordering_accuracy: float

    determinism_runs: int
    determinism_score: float

    component_stats: Dict[str, Dict[str, float]]


# ═══════════════════════════════════════════════════════════════════
# EVALUATOR ENGINE
# ═══════════════════════════════════════════════════════════════════

class FairDealEvaluator:
    """Systematic validation engine for the FAIRDEAL scoring system."""

    def __init__(self):
        self.scorer = PsychologicalScoringEngine()

    def run_full_evaluation(self) -> EvaluationReport:
        t_start = time.perf_counter()

        results = self._run_scoring_tests()
        scores = [r.actual_score for r in results]

        distribution = self._compute_distribution(scores)
        grade_dist = self._compute_grade_distribution(results)
        category_means = self._compute_category_means(results)
        comparisons = self._compute_category_comparisons(results)
        correlations = self._compute_correlations()
        ordering_correct, ordering_total = self._validate_orderings(results)
        determinism = self._test_determinism()
        component_stats = self._compute_component_stats(results)

        pass_count = sum(1 for r in results if r.passed)
        t_elapsed = (time.perf_counter() - t_start) * 1000

        return EvaluationReport(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            engine_version=self.scorer.version,
            total_test_cases=len(results),
            evaluation_time_ms=round(t_elapsed, 2),
            scoring_pass_rate=round(pass_count / len(results) * 100, 2),
            scoring_results=results,
            score_distribution=distribution,
            grade_distribution=grade_dist,
            category_means=category_means,
            category_comparisons=comparisons,
            feature_correlations=correlations,
            known_ordering_total=ordering_total,
            known_ordering_correct=ordering_correct,
            known_ordering_accuracy=round(ordering_correct / ordering_total * 100, 2) if ordering_total else 0,
            determinism_runs=3,
            determinism_score=determinism,
            component_stats=component_stats,
        )

    # ─── Scoring Tests ──────────────────────────────────────────

    def _run_scoring_tests(self) -> List[ScoringTestResult]:
        results = []
        for tc in SCORING_TEST_CASES:
            psych = self.scorer.compute_score(**tc["inputs"])
            lo, hi = tc["expected_score_range"]
            results.append(ScoringTestResult(
                id=tc["id"],
                name=tc["name"],
                category=tc["category"],
                company=tc["company"],
                ctc_inr=tc["ctc_inr"],
                expected_range=tc["expected_score_range"],
                actual_score=psych.score,
                grade=psych.grade,
                passed=lo <= psych.score <= hi,
                badges=psych.badges,
                risk_factors=psych.risk_factors,
                breakdown=psych.breakdown,
                confidence=psych.confidence,
            ))
        return results

    # ─── Distribution Analysis ───────────────────────────────────

    def _compute_distribution(self, scores: List[float]) -> ScoreDistribution:
        if HAS_NUMPY:
            arr = np.array(scores, dtype=float)
            mean = float(np.mean(arr))
            median = float(np.median(arr))
            std = float(np.std(arr, ddof=1))
            q1 = float(np.percentile(arr, 25))
            q3 = float(np.percentile(arr, 75))
        else:
            sorted_s = sorted(scores)
            n = len(sorted_s)
            mean = sum(sorted_s) / n
            median = sorted_s[n // 2] if n % 2 else (sorted_s[n // 2 - 1] + sorted_s[n // 2]) / 2
            variance = sum((x - mean) ** 2 for x in sorted_s) / (n - 1) if n > 1 else 0
            std = math.sqrt(variance)
            q1 = sorted_s[n // 4]
            q3 = sorted_s[3 * n // 4]

        skew = self._skewness(scores, mean, std)
        kurt = self._kurtosis(scores, mean, std)

        return ScoreDistribution(
            mean=round(mean, 2),
            median=round(median, 2),
            std_dev=round(std, 2),
            min_score=min(scores),
            max_score=max(scores),
            q1=round(q1, 2),
            q3=round(q3, 2),
            iqr=round(q3 - q1, 2),
            skewness=round(skew, 3),
            kurtosis=round(kurt, 3),
            range_span=max(scores) - min(scores),
        )

    @staticmethod
    def _skewness(data: List[float], mean: float, std: float) -> float:
        if std == 0 or len(data) < 3:
            return 0.0
        n = len(data)
        return (n / ((n - 1) * (n - 2))) * sum(((x - mean) / std) ** 3 for x in data)

    @staticmethod
    def _kurtosis(data: List[float], mean: float, std: float) -> float:
        if std == 0 or len(data) < 4:
            return 0.0
        n = len(data)
        k4 = sum(((x - mean) / std) ** 4 for x in data) / n
        return k4 - 3.0

    # ─── Grade Distribution ──────────────────────────────────────

    @staticmethod
    def _compute_grade_distribution(results: List[ScoringTestResult]) -> Dict[str, int]:
        grades = ["CRITICAL", "POOR", "BELOW AVERAGE", "AVERAGE", "FAIR", "GOOD", "EXCELLENT", "EXCEPTIONAL"]
        dist = Counter(r.grade for r in results)
        return {g: dist.get(g, 0) for g in grades}

    # ─── Category Means ──────────────────────────────────────────

    @staticmethod
    def _compute_category_means(results: List[ScoringTestResult]) -> Dict[str, float]:
        cat_scores: Dict[str, List[float]] = {}
        for r in results:
            cat_scores.setdefault(r.category, []).append(r.actual_score)
        return {cat: round(sum(s) / len(s), 2) for cat, s in cat_scores.items()}

    # ─── Category Comparisons (Welch's t-test) ───────────────────

    def _compute_category_comparisons(self, results: List[ScoringTestResult]) -> List[CategoryComparison]:
        cat_scores: Dict[str, List[float]] = {}
        for r in results:
            cat_scores.setdefault(r.category, []).append(r.actual_score)

        pairs = [
            ("product", "service"),
            ("startup", "service"),
            ("product", "consulting"),
        ]
        comparisons = []
        for a, b in pairs:
            if a not in cat_scores or b not in cat_scores:
                continue
            sa, sb = cat_scores[a], cat_scores[b]
            if len(sa) < 2 or len(sb) < 2:
                continue
            t_stat, p_approx, effect = self._welch_t_test(sa, sb)
            comparisons.append(CategoryComparison(
                category_a=a, category_b=b,
                mean_a=round(sum(sa) / len(sa), 2),
                mean_b=round(sum(sb) / len(sb), 2),
                std_a=round(self._std(sa), 2),
                std_b=round(self._std(sb), 2),
                n_a=len(sa), n_b=len(sb),
                t_statistic=round(t_stat, 3),
                p_value_approx=round(p_approx, 6),
                significant=p_approx < 0.05,
                effect_size=round(effect, 3),
            ))
        return comparisons

    @staticmethod
    def _std(data: List[float]) -> float:
        n = len(data)
        if n < 2:
            return 0.0
        mean = sum(data) / n
        return math.sqrt(sum((x - mean) ** 2 for x in data) / (n - 1))

    @staticmethod
    def _welch_t_test(a: List[float], b: List[float]) -> Tuple[float, float, float]:
        n1, n2 = len(a), len(b)
        m1, m2 = sum(a) / n1, sum(b) / n2
        v1 = sum((x - m1) ** 2 for x in a) / (n1 - 1) if n1 > 1 else 0
        v2 = sum((x - m2) ** 2 for x in b) / (n2 - 1) if n2 > 1 else 0
        se = math.sqrt(v1 / n1 + v2 / n2) if (v1 / n1 + v2 / n2) > 0 else 1e-9
        t_stat = (m1 - m2) / se

        # Welch-Satterthwaite degrees of freedom
        num = (v1 / n1 + v2 / n2) ** 2
        denom = (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1) if (n1 > 1 and n2 > 1) else 1
        df = num / denom if denom > 0 else 1

        # Approximate p-value using a simple sigmoid on |t|/sqrt(df)
        z = abs(t_stat) / math.sqrt(max(df, 1))
        p_approx = 2 * (1 / (1 + math.exp(1.7 * z * math.sqrt(max(df, 1)) / math.sqrt(2))))
        p_approx = min(1.0, max(0.0, p_approx))

        # Cohen's d
        pooled_std = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)) if (n1 + n2 > 2) else 1
        d = abs(m1 - m2) / pooled_std if pooled_std > 0 else 0

        return t_stat, p_approx, d

    # ─── Feature Correlations ────────────────────────────────────

    def _compute_correlations(self) -> List[CorrelationResult]:
        features = {
            "salary_percentile": [],
            "notice_percentile": [],
            "benefits_count": [],
            "non_compete_months": [],
        }
        scores = []

        for tc in SCORING_TEST_CASES:
            inp = tc["inputs"]
            psych = self.scorer.compute_score(**inp)
            scores.append(psych.score)
            features["salary_percentile"].append(inp["salary_percentile"])
            features["notice_percentile"].append(inp["notice_percentile"])
            features["benefits_count"].append(inp["benefits_count"])
            features["non_compete_months"].append(inp["non_compete_months"])

        results = []
        for feat_name, feat_vals in features.items():
            r = self._pearson_r(feat_vals, scores)
            direction = "positive" if r > 0 else "negative"
            if abs(r) >= 0.7:
                strength = "strong"
            elif abs(r) >= 0.4:
                strength = "moderate"
            else:
                strength = "weak"
            results.append(CorrelationResult(
                feature=feat_name,
                pearson_r=round(r, 4),
                direction=direction,
                strength=strength,
            ))
        return results

    @staticmethod
    def _pearson_r(x: List[float], y: List[float]) -> float:
        n = len(x)
        if n < 3:
            return 0.0
        mx, my = sum(x) / n, sum(y) / n
        cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)
        sx = math.sqrt(sum((xi - mx) ** 2 for xi in x) / (n - 1))
        sy = math.sqrt(sum((yi - my) ** 2 for yi in y) / (n - 1))
        if sx == 0 or sy == 0:
            return 0.0
        return cov / (sx * sy)

    # ─── Known Orderings ─────────────────────────────────────────

    @staticmethod
    def _validate_orderings(results: List[ScoringTestResult]) -> Tuple[int, int]:
        score_map = {r.id: r.actual_score for r in results}
        correct = 0
        total = len(KNOWN_ORDERINGS)
        for higher_id, lower_id in KNOWN_ORDERINGS:
            if higher_id in score_map and lower_id in score_map:
                if score_map[higher_id] > score_map[lower_id]:
                    correct += 1
        return correct, total

    # ─── Determinism ─────────────────────────────────────────────

    def _test_determinism(self, runs: int = 3) -> float:
        all_scores: List[List[float]] = []
        for _ in range(runs):
            run_scores = []
            for tc in SCORING_TEST_CASES:
                psych = self.scorer.compute_score(**tc["inputs"])
                run_scores.append(psych.score)
            all_scores.append(run_scores)

        matches = 0
        total = 0
        for i in range(len(all_scores[0])):
            ref = all_scores[0][i]
            for run in all_scores[1:]:
                total += 1
                if run[i] == ref:
                    matches += 1
        return round(matches / total * 100, 2) if total else 100.0

    # ─── Component Statistics ────────────────────────────────────

    @staticmethod
    def _compute_component_stats(results: List[ScoringTestResult]) -> Dict[str, Dict[str, float]]:
        components = ["salary", "notice", "benefits", "clauses", "legal"]
        stats: Dict[str, Dict[str, float]] = {}
        for comp in components:
            values = [r.breakdown[comp]["score"] for r in results if comp in r.breakdown]
            if not values:
                continue
            n = len(values)
            mean = sum(values) / n
            std = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0
            stats[comp] = {
                "mean": round(mean, 2),
                "std": round(std, 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }
        return stats


def report_to_dict(report: EvaluationReport) -> Dict[str, Any]:
    """Convert an EvaluationReport to a JSON-serializable dictionary."""
    d = asdict(report)
    return d
