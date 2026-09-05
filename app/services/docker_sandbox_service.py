import os
import subprocess
import json
import xml.etree.ElementTree as ET
import tempfile
from app.models.evaluation_metrics import EvaluationMetrics

class DockerSandboxService:
    """
    Executes unit tests securely inside an ephemeral Docker container.
    Prevents untrusted AI-generated code from accessing the host OS.
    """

    @staticmethod
    def build_image(image_name: str = "ai-refactor-sandbox"):
        """Builds the Docker image from our Dockerfile."""
        dockerfile_path = os.path.join(os.getcwd(), "docker")
        subprocess.run(
            ["docker", "build", "-t", image_name, dockerfile_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True
        )

    @staticmethod
    def run_tests_in_sandbox(metric_id: int = 1) -> EvaluationMetrics:
        """
        Mounts the code into a container, runs pytest, extracts results, and destroys it.
        """
        # Get absolute path of the datasets directory to preserve Python module paths
        abs_datasets_dir = os.path.abspath("datasets")
        
        # Create a temporary directory on the host to safely receive the XML/JSON reports
        with tempfile.TemporaryDirectory() as temp_results_dir:
            
            coverage_file_internal = "/results/coverage.json"
            junit_file_internal = "/results/junit.xml"
            
            # THE SECURE DOCKER COMMAND
            command = [
                "docker", "run", "--rm", 
                "--network", "none", # BLOCK INTERNET ACCESS
                "-e", "PYTHONPATH=/sandbox", # Help Python find the datasets module
                "-v", f"{abs_datasets_dir}:/sandbox/datasets:ro", # READ-ONLY Mount
                "-v", f"{temp_results_dir}:/results:rw",          # READ-WRITE Mount
                "ai-refactor-sandbox",
                "/sandbox/datasets/tests",
                "--cov=/sandbox/datasets/legacy",
                f"--cov-report=json:{coverage_file_internal}",
                f"--junitxml={junit_file_internal}"
            ]
            
            # Run the container
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Extract metrics from the temp directory on the host machine
            host_junit = os.path.join(temp_results_dir, "junit.xml")
            host_coverage = os.path.join(temp_results_dir, "coverage.json")

            total_tests, failures, errors = 0, 0, 0
            coverage_percentage = 0.0

            if os.path.exists(host_junit):
                try:
                    tree = ET.parse(host_junit)
                    for suite in tree.getroot().iter('testsuite'):
                        total_tests += int(suite.get('tests', 0))
                        failures += int(suite.get('failures', 0))
                        errors += int(suite.get('errors', 0))
                except Exception:
                    pass

            if os.path.exists(host_coverage):
                try:
                    with open(host_coverage, 'r', encoding='utf-8') as f:
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