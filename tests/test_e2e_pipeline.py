import os
import subprocess
import sys

def test_full_pipeline_cli_execution():
    """Runs the application entry point end-to-end as a CLI subprocess."""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["LLM_PROVIDER"] = "mock"

    result = subprocess.run(
        [sys.executable, "-m", "app.main"],
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "PIPELINE EXECUTION COMPLETE" in result.stdout
    assert os.path.exists("results/benchmark_report.csv")
    assert os.path.exists("results/complexity_maintainability_delta.png")