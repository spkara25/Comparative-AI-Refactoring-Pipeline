import csv
import os
from typing import List, Dict, Any
from app.models.evaluation_metrics import EvaluationMetrics

class ReportingService:
    """
    Computes delta metrics and generates research-grade CSV benchmark reports.
    """

    CSV_HEADERS = [
        "experiment_id",
        "timestamp",
        "model_name",
        "prompt_strategy",
        "source_file",
        # Original baseline metrics
        "orig_cyclomatic_complexity",
        "orig_halstead_volume",
        "orig_maintainability_index",
        "orig_test_pass_rate",
        "orig_coverage_percentage",
        # Refactored metrics
        "refact_cyclomatic_complexity",
        "refact_halstead_volume",
        "refact_maintainability_index",
        "refact_test_pass_rate",
        "refact_coverage_percentage",
        # Comparative Deltas (Refactored - Original)
        "delta_complexity",
        "delta_halstead_volume",
        "delta_maintainability_index",
        "delta_test_pass_rate",
        "delta_coverage_percentage",
        "behavior_preserved"  # True if test pass rate did not drop
    ]

    @staticmethod
    def calculate_row(
        experiment_id: int,
        timestamp: str,
        model_name: str,
        prompt_strategy: str,
        source_file: str,
        original: EvaluationMetrics,
        refactored: EvaluationMetrics
    ) -> Dict[str, Any]:
        """Calculates differences and returns a structured record for export."""
        delta_cc = refactored.cyclomatic_complexity - original.cyclomatic_complexity
        delta_hv = refactored.halstead_volume - original.halstead_volume
        delta_mi = refactored.maintainability_index - original.maintainability_index
        delta_pr = refactored.test_pass_rate - original.test_pass_rate
        delta_cov = refactored.coverage_percentage - original.coverage_percentage
        
        behavior_preserved = (
            refactored.test_pass_rate >= original.test_pass_rate
            if original.test_pass_rate > 0 else refactored.test_pass_rate == 100.0
        )

        return {
            "experiment_id": experiment_id,
            "timestamp": timestamp,
            "model_name": model_name,
            "prompt_strategy": prompt_strategy,
            "source_file": source_file,
            "orig_cyclomatic_complexity": round(original.cyclomatic_complexity, 2),
            "orig_halstead_volume": round(original.halstead_volume, 2),
            "orig_maintainability_index": round(original.maintainability_index, 2),
            "orig_test_pass_rate": round(original.test_pass_rate, 2),
            "orig_coverage_percentage": round(original.coverage_percentage, 2),
            "refact_cyclomatic_complexity": round(refactored.cyclomatic_complexity, 2),
            "refact_halstead_volume": round(refactored.halstead_volume, 2),
            "refact_maintainability_index": round(refactored.maintainability_index, 2),
            "refact_test_pass_rate": round(refactored.test_pass_rate, 2),
            "refact_coverage_percentage": round(refactored.coverage_percentage, 2),
            "delta_complexity": round(delta_cc, 2),
            "delta_halstead_volume": round(delta_hv, 2),
            "delta_maintainability_index": round(delta_mi, 2),
            "delta_test_pass_rate": round(delta_pr, 2),
            "delta_coverage_percentage": round(delta_cov, 2),
            "behavior_preserved": behavior_preserved
        }

    @classmethod
    def export_to_csv(cls, rows: List[Dict[str, Any]], output_filepath: str = "results/benchmark_report.csv"):
        """Writes a collection of evaluated runs to a CSV file."""
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        with open(output_filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.CSV_HEADERS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)