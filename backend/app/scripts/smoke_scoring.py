from __future__ import annotations

"""
Quick local smoke test for parsing -> extraction -> benchmarking -> red-flags -> scoring.

Run (from repo root, with venv active):
  python -m backend.app.scripts.smoke_scoring
"""

from backend.app.services.benchmark_service import BenchmarkService
from backend.app.services.parser_service import ParserService
from backend.app.services.red_flag_service import RedFlagService
from backend.app.services.rule_extraction_service import RuleExtractionService
from backend.app.services.scoring_service import ScoringService


def main() -> None:
    sample_contract_text = """
    OFFER LETTER

    Designation: Software Development Engineer
    Total CTC: INR 12,00,000 per annum

    Notice Period: 60 days
    Non-compete: for a period of 6 months following termination.

    Benefits include Health Insurance, Provident Fund (PF), and Paid Leave.
    """

    parser = ParserService()
    parsed = parser.parse(sample_contract_text.encode("utf-8"), filename="sample.txt")

    extractor = RuleExtractionService()
    extraction = extractor.extract(parsed)

    salary = extraction.ctc_inr.value if extraction.ctc_inr else None
    notice_days = extraction.notice_period_days.value if extraction.notice_period_days else None

    benchmarker = BenchmarkService()
    benchmark = None
    notice_percentile = None

    if salary:
        benchmark = benchmarker.compare_salary(
            ctc_inr=float(salary),
            role="sde",
            yoe=1,
            company_type="product",
            location=None,
            industry="tech",
        )

    if notice_days:
        notice_percentile = benchmarker.compute_notice_percentile(
            notice_days=int(notice_days),
            company_type="product",
        )

    red_flag_service = RedFlagService()
    red_flags, favorable_terms = red_flag_service.analyze(
        extraction=extraction,
        benchmark=benchmark,
        benefits_count=extraction.benefits_count,
        industry="tech",
        company_type="product",
        notice_percentile=notice_percentile,
    )

    scorer = ScoringService()
    scoring = scorer.compute_scores(
        extraction=extraction,
        benchmark=benchmark,
        red_flags=red_flags,
        favorable_terms=favorable_terms,
        notice_percentile=notice_percentile,
    )

    print("\n=== Extraction ===")
    print("CTC:", extraction.ctc_inr.model_dump() if extraction.ctc_inr else None)
    print("Notice:", extraction.notice_period_days.model_dump() if extraction.notice_period_days else None)
    print("Non-compete:", extraction.non_compete_months.model_dump() if extraction.non_compete_months else None)
    print("Benefits:", extraction.benefits, "count:", extraction.benefits_count)

    print("\n=== Benchmark ===")
    if benchmark:
        print("Percentile salary:", benchmark.percentile_salary, "Cohort size:", benchmark.cohort_size)
        print("Filters:", benchmark.filters_used)
        print("Broaden steps:", benchmark.broaden_steps)
        print("Warning:", benchmark.warning)
        print("Median:", benchmark.market_median, "P25:", benchmark.market_p25, "P75:", benchmark.market_p75)
    else:
        print("No benchmark available")

    print("\nNotice percentile:", notice_percentile)

    print("\n=== Red flags / favorable terms ===")
    print("Red flags:", [f"{r.id}({r.impact_score})" for r in red_flags])
    print("Favorable:", [f"{t.id}(+{t.impact_score})" for t in favorable_terms])

    print("\n=== Scoring ===")
    print("Overall:", scoring.overall_score, "Grade:", scoring.grade, "Confidence:", scoring.score_confidence)
    print("Formula:", scoring.score_formula)
    print("Breakdown:")
    for item in scoring.breakdown:
        print("-", item.factor, item.points, item.reason)


if __name__ == "__main__":
    main()

