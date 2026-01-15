"""
Runtime Benchmark Script for Contract Analysis.

Analyzes sample contracts and reports timing metrics.

Usage:
  python -m app.eval.benchmark --contracts data/raw_contracts
  python -m app.eval.benchmark --contracts data/raw_contracts --with-narration

Target latencies:
- Deterministic path (no LLM): <= 3 seconds
- With narration: <= 6 seconds
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field

from loguru import logger

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    file: str
    success: bool
    error: Optional[str] = None
    
    parse_ms: int = 0
    extract_ms: int = 0
    stats_ms: int = 0
    rag_ms: int = 0
    score_ms: int = 0
    total_ms: int = 0
    
    score: Optional[int] = None
    cached: bool = False


@dataclass
class BenchmarkSummary:
    """Summary of all benchmark runs."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    
    avg_total_ms: float = 0.0
    avg_parse_ms: float = 0.0
    avg_extract_ms: float = 0.0
    avg_stats_ms: float = 0.0
    avg_rag_ms: float = 0.0
    avg_score_ms: float = 0.0
    
    min_total_ms: int = 0
    max_total_ms: int = 0
    
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p99_ms: float = 0.0
    
    results: List[BenchmarkResult] = field(default_factory=list)


from typing import Optional


class Benchmarker:
    """Benchmarker for contract analysis performance."""
    
    # Target latencies
    TARGET_DETERMINISTIC_MS = 3000
    TARGET_WITH_NARRATION_MS = 6000
    
    def __init__(
        self,
        contracts_path: Path,
        with_narration: bool = False,
        limit: int = 10,
    ):
        """
        Initialize benchmarker.
        
        Args:
            contracts_path: Path to directory containing contracts
            with_narration: Enable LLM narration (slower)
            limit: Maximum number of contracts to benchmark
        """
        self.contracts_path = contracts_path
        self.with_narration = with_narration
        self.limit = limit
        
        # Import analysis service
        from app.services.analysis_service_v2 import AnalysisServiceV2
        self.analysis_service = AnalysisServiceV2(enable_narration=with_narration)
        
        self.results: List[BenchmarkResult] = []
    
    def discover_contracts(self) -> List[Path]:
        """Discover contract files to benchmark."""
        extensions = ['.pdf', '.docx', '.doc']
        contracts = []
        
        if not self.contracts_path.exists():
            raise FileNotFoundError(f"Contracts path not found: {self.contracts_path}")
        
        for ext in extensions:
            contracts.extend(self.contracts_path.glob(f"*{ext}"))
        
        # Limit
        contracts = contracts[:self.limit]
        
        logger.info(f"Discovered {len(contracts)} contracts for benchmarking")
        return contracts
    
    def benchmark_single(self, file_path: Path) -> BenchmarkResult:
        """Benchmark a single contract."""
        result = BenchmarkResult(file=str(file_path), success=False)
        
        try:
            # Read file
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Analyze
            start = time.time()
            analysis = self.analysis_service.analyze_contract(
                file_content=file_content,
                filename=file_path.name,
            )
            total_ms = int((time.time() - start) * 1000)
            
            # Extract timings
            timings = analysis.get("timings", {})
            result.parse_ms = timings.get("parse_ms", 0)
            result.extract_ms = timings.get("extract_ms", 0)
            result.stats_ms = timings.get("stats_ms", 0)
            result.rag_ms = timings.get("rag_ms", 0)
            result.score_ms = timings.get("score_ms", 0)
            result.total_ms = timings.get("total_ms", total_ms)
            
            result.score = analysis.get("score") or analysis.get("fairness_score")
            result.cached = analysis.get("cached", False)
            result.success = True
            
        except Exception as e:
            result.error = str(e)
            logger.error(f"Benchmark failed for {file_path.name}: {e}")
        
        return result
    
    def run(self) -> BenchmarkSummary:
        """Run benchmarks on all discovered contracts."""
        contracts = self.discover_contracts()
        
        summary = BenchmarkSummary(total_files=len(contracts))
        
        logger.info(f"Starting benchmark: {len(contracts)} contracts, narration={self.with_narration}")
        
        for i, contract in enumerate(contracts):
            logger.info(f"Benchmarking {i+1}/{len(contracts)}: {contract.name}")
            
            result = self.benchmark_single(contract)
            summary.results.append(result)
            
            if result.success:
                summary.successful += 1
            else:
                summary.failed += 1
            
            # Log result
            if result.success:
                status = "✓" if result.total_ms <= self.TARGET_DETERMINISTIC_MS else "⚠"
                logger.info(f"  {status} {result.total_ms}ms (score: {result.score})")
            else:
                logger.info(f"  ✗ Failed: {result.error}")
        
        # Compute summary statistics
        self._compute_summary_stats(summary)
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    def _compute_summary_stats(self, summary: BenchmarkSummary):
        """Compute summary statistics from results."""
        successful_results = [r for r in summary.results if r.success]
        
        if not successful_results:
            return
        
        # Averages
        summary.avg_total_ms = sum(r.total_ms for r in successful_results) / len(successful_results)
        summary.avg_parse_ms = sum(r.parse_ms for r in successful_results) / len(successful_results)
        summary.avg_extract_ms = sum(r.extract_ms for r in successful_results) / len(successful_results)
        summary.avg_stats_ms = sum(r.stats_ms for r in successful_results) / len(successful_results)
        summary.avg_rag_ms = sum(r.rag_ms for r in successful_results) / len(successful_results)
        summary.avg_score_ms = sum(r.score_ms for r in successful_results) / len(successful_results)
        
        # Min/Max
        total_times = [r.total_ms for r in successful_results]
        summary.min_total_ms = min(total_times)
        summary.max_total_ms = max(total_times)
        
        # Percentiles
        sorted_times = sorted(total_times)
        n = len(sorted_times)
        summary.p50_ms = sorted_times[int(n * 0.5)] if n > 0 else 0
        summary.p90_ms = sorted_times[int(n * 0.9)] if n > 0 else 0
        summary.p99_ms = sorted_times[int(n * 0.99)] if n > 0 else 0
    
    def _print_summary(self, summary: BenchmarkSummary):
        """Print benchmark summary."""
        target = self.TARGET_WITH_NARRATION_MS if self.with_narration else self.TARGET_DETERMINISTIC_MS
        
        print("\n" + "=" * 60)
        print("RUNTIME BENCHMARK RESULTS")
        print("=" * 60)
        print(f"Mode: {'With Narration' if self.with_narration else 'Deterministic Only'}")
        print(f"Target: {target}ms")
        print()
        print(f"Total files: {summary.total_files}")
        print(f"Successful:  {summary.successful}")
        print(f"Failed:      {summary.failed}")
        print()
        print("TIMING (ms):")
        print(f"  Average Total:   {summary.avg_total_ms:>8.1f}")
        print(f"  Average Parse:   {summary.avg_parse_ms:>8.1f}")
        print(f"  Average Extract: {summary.avg_extract_ms:>8.1f}")
        print(f"  Average Stats:   {summary.avg_stats_ms:>8.1f}")
        print(f"  Average RAG:     {summary.avg_rag_ms:>8.1f}")
        print(f"  Average Score:   {summary.avg_score_ms:>8.1f}")
        print()
        print(f"  Min:  {summary.min_total_ms}ms")
        print(f"  Max:  {summary.max_total_ms}ms")
        print(f"  P50:  {summary.p50_ms:.0f}ms")
        print(f"  P90:  {summary.p90_ms:.0f}ms")
        print(f"  P99:  {summary.p99_ms:.0f}ms")
        print()
        
        # Check against target
        if summary.avg_total_ms <= target:
            print(f"✓ PASS: Average {summary.avg_total_ms:.0f}ms <= target {target}ms")
        else:
            print(f"✗ FAIL: Average {summary.avg_total_ms:.0f}ms > target {target}ms")
        
        print("=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark contract analysis performance"
    )
    
    parser.add_argument(
        "--contracts", "-c",
        type=str,
        default="data/raw_contracts",
        help="Path to contracts directory"
    )
    
    parser.add_argument(
        "--with-narration",
        action="store_true",
        help="Enable LLM narration (increases target latency)"
    )
    
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="Maximum number of contracts to benchmark"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file for results JSON"
    )
    
    args = parser.parse_args()
    
    benchmarker = Benchmarker(
        contracts_path=Path(args.contracts),
        with_narration=args.with_narration,
        limit=args.limit,
    )
    
    summary = benchmarker.run()
    
    # Save results if output specified
    if args.output:
        output_data = {
            "total_files": summary.total_files,
            "successful": summary.successful,
            "failed": summary.failed,
            "avg_total_ms": summary.avg_total_ms,
            "min_ms": summary.min_total_ms,
            "max_ms": summary.max_total_ms,
            "p50_ms": summary.p50_ms,
            "p90_ms": summary.p90_ms,
            "results": [
                {
                    "file": r.file,
                    "success": r.success,
                    "total_ms": r.total_ms,
                    "score": r.score,
                }
                for r in summary.results
            ],
        }
        
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")


if __name__ == "__main__":
    main()
