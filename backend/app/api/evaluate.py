"""
Evaluation API — runs validation metrics and returns IEEE-paper-ready results.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from ..evaluation.evaluator import FairDealEvaluator, report_to_dict
from ..logging_config import get_logger

router = APIRouter(tags=["evaluate"])
log = get_logger("api.evaluate")

_cached_report: dict | None = None


@router.post("/run")
async def run_evaluation():
    """Run the full validation suite and return structured results."""
    global _cached_report
    log.info("Starting full evaluation suite…")

    evaluator = FairDealEvaluator()
    report = evaluator.run_full_evaluation()
    result = report_to_dict(report)
    _cached_report = result

    log.info(
        f"Evaluation complete: pass_rate={report.scoring_pass_rate}%, "
        f"ordering={report.known_ordering_accuracy}%, "
        f"determinism={report.determinism_score}%"
    )
    return ORJSONResponse(result)


@router.get("/results")
async def get_evaluation_results():
    """Return the most recently computed evaluation results (cached)."""
    if _cached_report is None:
        evaluator = FairDealEvaluator()
        report = evaluator.run_full_evaluation()
        result = report_to_dict(report)
        return ORJSONResponse(result)
    return ORJSONResponse(_cached_report)
