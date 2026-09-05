import os
import csv
from datetime import datetime
from app.models.evaluation_metrics import EvaluationMetrics
from app.services.reporting_service import ReportingService

def test_reporting_service_delta_calculation_and_export():
    orig_m = EvaluationMetrics(
        metric_id=1,
        cyclomatic_complexity=6.0,
        halstead_volume=150.0,
        maintainability_index=50.0,
        test_pass_rate=100.0,
        coverage_percentage=80.0
    )
    refact_m = EvaluationMetrics(
        metric_id=2,
        cyclomatic_complexity=2.0,  # Lower complexity (better)
        halstead_volume=95.0,       # Lower volume
        maintainability_index=78.5, # Higher MI (better)
        test_pass_rate=100.0,       # Behavior intact
        coverage_percentage=90.0    # Improved coverage
    )

    row = ReportingService.calculate_row(
        experiment_id=101,
        timestamp=datetime.now().isoformat(),
        model_name="mock-model",
        prompt_strategy="pep8-and-modularize",
        source_file="example_01.py",
        original=orig_m,
        refactored=refact_m
    )

    # Validate deltas
    assert row["delta_complexity"] == -4.0
    assert row["delta_maintainability_index"] == 28.5
    assert row["delta_coverage_percentage"] == 10.0
    assert row["behavior_preserved"] is True

    # Test file export
    test_csv_path = "results/test_report.csv"
    ReportingService.export_to_csv([row], output_filepath=test_csv_path)
    assert os.path.exists(test_csv_path)

    # Read back to ensure headers and data match
    with open(test_csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)
        assert len(data) == 1
        assert data[0]["model_name"] == "mock-model"
        assert float(data[0]["delta_complexity"]) == -4.0
        assert data[0]["behavior_preserved"] == "True"

    # Cleanup temporary test artifact
    if os.path.exists(test_csv_path):
        os.remove(test_csv_path)