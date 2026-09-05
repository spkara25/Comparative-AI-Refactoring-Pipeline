import os
from app.services.visual_reporting_service import VisualReportingService

def test_generate_delta_bar_chart():
    mock_records = [
        {
            "model_name": "mock-llm-1",
            "prompt_strategy": "pep8-basic",
            "delta_complexity": -2.0,
            "delta_maintainability_index": 12.5
        },
        {
            "model_name": "llama-3.3-70b",
            "prompt_strategy": "modular-clean",
            "delta_complexity": -5.0,
            "delta_maintainability_index": 24.0
        }
    ]

    output_path = "results/test_chart.png"
    result = VisualReportingService.generate_delta_bar_chart(mock_records, output_filepath=output_path)

    assert os.path.exists(output_path)
    assert result == output_path
    assert os.path.getsize(output_path) > 0  # File is not empty

    # Cleanup temporary test image
    if os.path.exists(output_path):
        os.remove(output_path)