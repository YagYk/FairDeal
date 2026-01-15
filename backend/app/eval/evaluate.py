"""
Evaluation Script for Contract Extraction Accuracy.

Gold set format (gold/annotations.jsonl):
{"file": "path/to/contract.pdf", "salary_in_inr": 1500000, "notice_period_days": 60, "non_compete": true}

Usage:
  python -m app.eval.evaluate --gold gold/annotations.jsonl
  python -m app.eval.evaluate --gold gold/annotations.jsonl --verbose

Computes:
- Salary exact match within ±5%
- Notice period exact match
- Non-compete precision/recall/F1
- Reports confusion examples
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.services.fast_extraction_service import FastExtractionService
from app.models.schemas import EvaluationResult


@dataclass
class ExtractionResult:
    """Result of extraction for comparison."""
    file: str
    extracted_salary: Optional[int] = None
    gold_salary: Optional[int] = None
    salary_match: bool = False
    salary_within_5pct: bool = False
    
    extracted_notice: Optional[int] = None
    gold_notice: Optional[int] = None
    notice_match: bool = False
    
    extracted_non_compete: Optional[bool] = None
    gold_non_compete: Optional[bool] = None
    non_compete_match: bool = False


@dataclass
class EvaluationMetrics:
    """Aggregated evaluation metrics."""
    total_samples: int = 0
    
    # Salary metrics
    salary_samples: int = 0
    salary_exact_matches: int = 0
    salary_within_5pct_matches: int = 0
    
    # Notice metrics
    notice_samples: int = 0
    notice_exact_matches: int = 0
    
    # Non-compete metrics
    non_compete_samples: int = 0
    non_compete_tp: int = 0  # True positive
    non_compete_fp: int = 0  # False positive
    non_compete_tn: int = 0  # True negative
    non_compete_fn: int = 0  # False negative
    
    # Results
    results: List[ExtractionResult] = field(default_factory=list)
    confusion_examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def compute_metrics(self) -> EvaluationResult:
        """Compute final metrics."""
        # Salary
        salary_exact_pct = (self.salary_exact_matches / self.salary_samples * 100) if self.salary_samples > 0 else 0.0
        salary_5pct = (self.salary_within_5pct_matches / self.salary_samples * 100) if self.salary_samples > 0 else 0.0
        
        # Notice
        notice_exact_pct = (self.notice_exact_matches / self.notice_samples * 100) if self.notice_samples > 0 else 0.0
        
        # Non-compete precision/recall/F1
        precision = self.non_compete_tp / (self.non_compete_tp + self.non_compete_fp) if (self.non_compete_tp + self.non_compete_fp) > 0 else 0.0
        recall = self.non_compete_tp / (self.non_compete_tp + self.non_compete_fn) if (self.non_compete_tp + self.non_compete_fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return EvaluationResult(
            total_samples=self.total_samples,
            salary_exact_match_pct=round(salary_exact_pct, 2),
            salary_within_5pct=round(salary_5pct, 2),
            notice_exact_match=round(notice_exact_pct, 2),
            non_compete_precision=round(precision, 4),
            non_compete_recall=round(recall, 4),
            non_compete_f1=round(f1, 4),
            confusion_examples=self.confusion_examples[:10],  # Top 10 examples
        )


class Evaluator:
    """Evaluator for extraction accuracy."""
    
    SALARY_TOLERANCE = 0.05  # 5% tolerance for salary match
    
    def __init__(self, gold_path: Path, verbose: bool = False):
        """
        Initialize evaluator.
        
        Args:
            gold_path: Path to gold annotations JSONL file
            verbose: Enable verbose logging
        """
        self.gold_path = gold_path
        self.verbose = verbose
        
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.fast_extraction = FastExtractionService()
        
        self.metrics = EvaluationMetrics()
    
    def load_gold_annotations(self) -> List[Dict[str, Any]]:
        """Load gold annotations from JSONL file."""
        annotations = []
        
        if not self.gold_path.exists():
            raise FileNotFoundError(f"Gold annotations file not found: {self.gold_path}")
        
        with open(self.gold_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        annotations.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON line: {e}")
        
        logger.info(f"Loaded {len(annotations)} gold annotations")
        return annotations
    
    def extract_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a file."""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            text = self.pdf_parser.extract_text(file_path)
        elif suffix in [".docx", ".doc"]:
            text = self.docx_parser.extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        metadata = self.fast_extraction.extract_metadata(text)
        
        # Extract values
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            if isinstance(field, dict):
                return field.get('value')
            return field
        
        return {
            "salary_in_inr": get_val(metadata.salary),
            "notice_period_days": get_val(metadata.notice_period_days),
            "non_compete": get_val(metadata.non_compete),
        }
    
    def compare_salary(self, extracted: Optional[int], gold: Optional[int]) -> Tuple[bool, bool]:
        """
        Compare salary values.
        
        Returns:
            Tuple of (exact_match, within_5pct)
        """
        if gold is None:
            return (True, True) if extracted is None else (False, False)
        
        if extracted is None:
            return (False, False)
        
        exact = extracted == gold
        
        # Within 5% tolerance
        tolerance = gold * self.SALARY_TOLERANCE
        within_5pct = abs(extracted - gold) <= tolerance
        
        return (exact, within_5pct)
    
    def compare_notice(self, extracted: Optional[int], gold: Optional[int]) -> bool:
        """Compare notice period values."""
        if gold is None:
            return extracted is None
        
        return extracted == gold
    
    def compare_non_compete(self, extracted: Optional[bool], gold: Optional[bool]) -> Tuple[bool, str]:
        """
        Compare non-compete values.
        
        Returns:
            Tuple of (match, classification: tp/fp/tn/fn)
        """
        # Normalize to bool
        extracted = bool(extracted) if extracted is not None else False
        gold = bool(gold) if gold is not None else False
        
        if gold and extracted:
            return (True, "tp")  # True positive
        elif gold and not extracted:
            return (False, "fn")  # False negative
        elif not gold and extracted:
            return (False, "fp")  # False positive
        else:
            return (True, "tn")  # True negative
    
    def evaluate_single(self, annotation: Dict[str, Any]) -> ExtractionResult:
        """Evaluate a single annotation."""
        file_path = Path(annotation["file"])
        
        if not file_path.exists():
            # Try relative to gold file
            file_path = self.gold_path.parent / annotation["file"]
        
        if not file_path.exists():
            logger.warning(f"File not found: {annotation['file']}")
            return None
        
        # Extract
        try:
            extracted = self.extract_from_file(file_path)
        except Exception as e:
            logger.error(f"Extraction failed for {file_path}: {e}")
            return None
        
        # Compare
        result = ExtractionResult(file=str(file_path))
        
        # Salary
        gold_salary = annotation.get("salary_in_inr")
        extracted_salary = extracted.get("salary_in_inr")
        
        result.gold_salary = gold_salary
        result.extracted_salary = extracted_salary
        
        if gold_salary is not None:
            exact, within_5 = self.compare_salary(extracted_salary, gold_salary)
            result.salary_match = exact
            result.salary_within_5pct = within_5
            
            self.metrics.salary_samples += 1
            if exact:
                self.metrics.salary_exact_matches += 1
            if within_5:
                self.metrics.salary_within_5pct_matches += 1
            
            if not within_5:
                self.metrics.confusion_examples.append({
                    "file": str(file_path),
                    "field": "salary",
                    "gold": gold_salary,
                    "extracted": extracted_salary,
                    "error_pct": abs(extracted_salary - gold_salary) / gold_salary * 100 if extracted_salary and gold_salary else None,
                })
        
        # Notice
        gold_notice = annotation.get("notice_period_days")
        extracted_notice = extracted.get("notice_period_days")
        
        result.gold_notice = gold_notice
        result.extracted_notice = extracted_notice
        
        if gold_notice is not None:
            result.notice_match = self.compare_notice(extracted_notice, gold_notice)
            
            self.metrics.notice_samples += 1
            if result.notice_match:
                self.metrics.notice_exact_matches += 1
            else:
                self.metrics.confusion_examples.append({
                    "file": str(file_path),
                    "field": "notice_period",
                    "gold": gold_notice,
                    "extracted": extracted_notice,
                })
        
        # Non-compete
        gold_nc = annotation.get("non_compete")
        extracted_nc = extracted.get("non_compete")
        
        result.gold_non_compete = gold_nc
        result.extracted_non_compete = extracted_nc
        
        if gold_nc is not None:
            match, classification = self.compare_non_compete(extracted_nc, gold_nc)
            result.non_compete_match = match
            
            self.metrics.non_compete_samples += 1
            if classification == "tp":
                self.metrics.non_compete_tp += 1
            elif classification == "fp":
                self.metrics.non_compete_fp += 1
            elif classification == "tn":
                self.metrics.non_compete_tn += 1
            elif classification == "fn":
                self.metrics.non_compete_fn += 1
            
            if not match:
                self.metrics.confusion_examples.append({
                    "file": str(file_path),
                    "field": "non_compete",
                    "gold": gold_nc,
                    "extracted": extracted_nc,
                    "classification": classification,
                })
        
        return result
    
    def run(self) -> EvaluationResult:
        """Run evaluation on all annotations."""
        annotations = self.load_gold_annotations()
        
        for i, annotation in enumerate(annotations):
            if self.verbose:
                logger.info(f"Evaluating {i+1}/{len(annotations)}: {annotation.get('file')}")
            
            result = self.evaluate_single(annotation)
            if result:
                self.metrics.results.append(result)
                self.metrics.total_samples += 1
        
        # Compute final metrics
        final_result = self.metrics.compute_metrics()
        
        # Print summary
        self._print_summary(final_result)
        
        return final_result
    
    def _print_summary(self, result: EvaluationResult):
        """Print evaluation summary."""
        print("\n" + "=" * 60)
        print("EXTRACTION ACCURACY EVALUATION")
        print("=" * 60)
        print(f"Total samples: {result.total_samples}")
        print()
        print("SALARY:")
        print(f"  Exact match: {result.salary_exact_match_pct:.1f}%")
        print(f"  Within ±5%:  {result.salary_within_5pct:.1f}%")
        print()
        print("NOTICE PERIOD:")
        print(f"  Exact match: {result.notice_exact_match:.1f}%")
        print()
        print("NON-COMPETE:")
        print(f"  Precision: {result.non_compete_precision:.3f}")
        print(f"  Recall:    {result.non_compete_recall:.3f}")
        print(f"  F1 Score:  {result.non_compete_f1:.3f}")
        print()
        
        if result.confusion_examples:
            print("CONFUSION EXAMPLES:")
            for ex in result.confusion_examples[:5]:
                print(f"  {ex['field']}: gold={ex['gold']}, extracted={ex['extracted']} ({Path(ex['file']).name})")
        
        print("=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate extraction accuracy against gold annotations"
    )
    
    parser.add_argument(
        "--gold", "-g",
        type=str,
        required=True,
        help="Path to gold annotations JSONL file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file for results JSON"
    )
    
    args = parser.parse_args()
    
    evaluator = Evaluator(
        gold_path=Path(args.gold),
        verbose=args.verbose,
    )
    
    result = evaluator.run()
    
    # Save results if output specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result.model_dump(), f, indent=2)
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
