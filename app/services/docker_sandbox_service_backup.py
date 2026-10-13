import os
import subprocess
import json
import xml.etree.ElementTree as ET
import tempfile
from pathlib import Path
import shutil
from app.models.evaluation_metrics import EvaluationMetrics

class DockerSandboxService:
    """
    Executes unit tests securely inside an ephemeral Docker container.
    Prevents untrusted AI-generated code from accessing the host OS.
    """


    @staticmethod
    def run_code_in_sandbox(
        source_code: str,
        test_code: str,
        source_filename: str,
        test_filename: str,
        metric_id: int = 1,
        image_name: str = "ai-refactor-sandbox",
    ) -> EvaluationMetrics:
        """
        Test one source-code version in an isolated Docker container.

        The source and tests are mounted read-only. Reports are written
        to a separate temporary directory.
        """
        # Accept filenames only, never arbitrary paths.
        if os.path.basename(source_filename) != source_filename:
            raise ValueError("source_filename must be a filename, not a path.")
        if os.path.basename(test_filename) != test_filename:
            raise ValueError("test_filename must be a filename, not a path.")
        if not source_filename.endswith(".py") or not test_filename.endswith(".py"):
            raise ValueError("Source and test filenames must end in .py.")

        with tempfile.TemporaryDirectory(prefix="refactor_workspace_") as workspace, \
             tempfile.TemporaryDirectory(prefix="refactor_results_") as results_dir:

            # Re-create the package layout expected by the dataset tests.
            legacy_dir = os.path.join(workspace, "datasets", "legacy")
            tests_dir = os.path.join(workspace, "datasets", "tests")
            os.makedirs(legacy_dir)
            os.makedirs(tests_dir)

            for init_dir in (
                os.path.join(workspace, "datasets"),
                legacy_dir,
                tests_dir,
            ):
                with open(os.path.join(init_dir, "__init__.py"), "w",
                          encoding="utf-8") as f:
                    f.write("")

            source_path = os.path.join(legacy_dir, source_filename)
            test_path = os.path.join(tests_dir, test_filename)

            with open(source_path, "w", encoding="utf-8") as f:
                f.write(source_code)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_code)

            coverage_path = "/results/coverage.json"
            junit_path = "/results/junit.xml"

            command = [
                "docker", "run", "--rm",
                "--network", "none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--memory=256m",
                "--cpus=1",
                "--pids-limit=64",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
                "-e", "PYTHONPATH=/sandbox",
                "-e", "PYTHONDONTWRITEBYTECODE=1",
                "-e", "COVERAGE_FILE=/results/.coverage",
                "-v", f"{os.path.abspath(workspace)}:/sandbox:ro",
                "-v", f"{os.path.abspath(results_dir)}:/results:rw",
                "-w", "/sandbox",
                image_name,
                "-p", "no:cacheprovider",
                f"/sandbox/datasets/tests/{test_filename}",
                f"--cov=/sandbox/datasets/legacy/{source_filename}",
                f"--cov-report=json:{coverage_path}",
                f"--junitxml={junit_path}",
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=90,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(
                    "Sandbox test timed out after 90 seconds."
                ) from exc
            except OSError as exc:
                raise RuntimeError(
                    f"Could not start Docker: {exc}"
                ) from exc

            host_junit = os.path.join(results_dir, "junit.xml")
            host_coverage = os.path.join(results_dir, "coverage.json")

            if not os.path.exists(host_junit):
                details = (result.stderr or result.stdout or "").strip()
                raise RuntimeError(
                    "Docker did not produce a JUnit report. "
                    f"Exit code: {result.returncode}. Details: {details[-2000:]}"
                )

            try:
                root = ET.parse(host_junit).getroot()
                total = failures = errors = 0

                for suite in root.iter("testsuite"):
                    total += int(suite.get("tests", 0))
                    failures += int(suite.get("failures", 0))
                    errors += int(suite.get("errors", 0))
            except (ET.ParseError, OSError, ValueError) as exc:
                raise RuntimeError(
                    "Could not parse the sandbox test report."
                ) from exc

            if total == 0:
                raise RuntimeError(
                    "No tests were collected. This is not a valid benchmark result."
                )

            passed = max(0, total - failures - errors)
            pass_rate = (passed / total) * 100.0

            coverage_percentage = 0.0
            if os.path.exists(host_coverage):
                try:
                    with open(host_coverage, encoding="utf-8") as f:
                        coverage_data = json.load(f)
                    coverage_percentage = float(
                        coverage_data.get("totals", {}).get(
                            "percent_covered", 0.0
                        )
                    )
                except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
                    raise RuntimeError(
                        "Could not read the sandbox coverage report."
                    ) from exc

            # Pytest exit code 1 can mean assertion failures; those are
            # represented in the test metrics. Infrastructure failures above
            # are raised rather than silently turned into zero scores.
            if result.returncode not in (0, 1):
                details = (result.stderr or result.stdout or "").strip()
                raise RuntimeError(
                    f"Pytest/Docker exited unexpectedly ({result.returncode}): "
                    f"{details[-2000:]}"
                )

            return EvaluationMetrics(
                metric_id=metric_id,
                cyclomatic_complexity=0.0,
                halstead_volume=0.0,
                maintainability_index=0.0,
                test_pass_rate=pass_rate,
                coverage_percentage=coverage_percentage,
            )


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