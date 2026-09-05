import os
import sys
import subprocess
import json
import xml.etree.ElementTree as ET
from app.models.evaluation_metrics import EvaluationMetrics

class TestExecutionService:
    """
    Executes unit tests in a separate process and extracts coverage and pass rates.
    (This exact CLI invocation will be moved inside Docker in Phase 6).
    """

    @staticmethod
    def run_tests(test_directory: str, source_directory: str, metric_id: int = 1) -> EvaluationMetrics:
        os.makedirs("results", exist_ok=True)
        coverage_file = "results/coverage.json"
        junit_file = "results/junit.xml"
        
        if os.path.exists(coverage_file): 
            os.remove(coverage_file)
        if os.path.exists(junit_file): 
            os.remove(junit_file)
        
        command = [
            sys.executable, "-m", "pytest",
            test_directory,
            f"--cov={source_directory}",
            f"--cov-report=json:{coverage_file}",
            f"--junitxml={junit_file}"
        ]
        
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        total_tests, failures, errors = 0, 0, 0
        coverage_percentage = 0.0
        
        if os.path.exists(junit_file):
            try:
                tree = ET.parse(junit_file)
                for suite in tree.getroot().iter('testsuite'):
                    total_tests += int(suite.get('tests', 0))
                    failures += int(suite.get('failures', 0))
                    errors += int(suite.get('errors', 0))
            except Exception:
                pass
                
        if os.path.exists(coverage_file):
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    cov_data = json.load(f)
                    coverage_percentage = float(cov_data.get("totals", {}).get("percent_covered", 0.0))
            except Exception:
                pass
                
        pass_rate = 0.0
        if total_tests > 0:
            passed = total_tests - failures - errors
            pass_rate = (passed / total_tests) * 100.0
            
        return EvaluationMetrics(
            metric_id=metric_id,
            cyclomatic_complexity=0.0,
            halstead_volume=0.0,
            maintainability_index=0.0,
            test_pass_rate=pass_rate,
            coverage_percentage=coverage_percentage
        )