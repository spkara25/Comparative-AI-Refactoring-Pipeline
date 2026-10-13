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

    @staticmethod
    def run_code_in_sandbox(
        source_code: str,
        test_code: str,
        source_filename: str,
        test_filename: str,
        metric_id: int = 1,
        image_name: str = "ai-refactor-sandbox",
    ) -> EvaluationMetrics:
        """Run one source file and its tests inside Docker."""
        import tempfile

        if (
            os.path.basename(source_filename) != source_filename
            or os.path.basename(test_filename) != test_filename
            or not source_filename.endswith(".py")
            or not test_filename.endswith(".py")
        ):
            raise ValueError("Provide simple Python filenames, not paths.")

        with tempfile.TemporaryDirectory() as workspace, \
             tempfile.TemporaryDirectory() as results_dir:

            legacy_dir = os.path.join(workspace, "datasets", "legacy")
            tests_dir = os.path.join(workspace, "datasets", "tests")
            os.makedirs(legacy_dir)
            os.makedirs(tests_dir)

            for directory in (
                os.path.join(workspace, "datasets"),
                legacy_dir,
                tests_dir,
            ):
                with open(os.path.join(directory, "__init__.py"), "w") as f:
                    f.write("")

            with open(os.path.join(legacy_dir, source_filename), "w") as f:
                f.write(source_code)
            with open(os.path.join(tests_dir, test_filename), "w") as f:
                f.write(test_code)

            coverage_file = "/results/coverage.json"
            junit_file = "/results/junit.xml"

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
                "-e", "PYTHONPATH=/sandbox/datasets/legacy:/sandbox",
                "-e", "COVERAGE_FILE=/results/.coverage",
                "-v", f"{os.path.abspath(workspace)}:/sandbox:ro",
                "-v", f"{os.path.abspath(results_dir)}:/results:rw",
                "-w", "/sandbox",
                image_name,
                "-p", "no:cacheprovider",
                f"/sandbox/datasets/tests/{test_filename}",
                f"--cov=datasets.legacy.{source_filename[:-3]}",
                f"--cov-report=json:{coverage_file}",
                f"--junitxml={junit_file}",
            ]

            result = subprocess.run(
                command, capture_output=True, text=True, timeout=90
            )

            report = os.path.join(results_dir, "junit.xml")
            coverage = os.path.join(results_dir, "coverage.json")

            print("Docker exit code:", result.returncode)
            print("Docker stdout:", result.stdout[-3000:])
            print("Docker stderr:", result.stderr[-3000:])
            print("Coverage report exists:", os.path.exists(coverage))

            if os.path.exists(coverage):
                with open(coverage, encoding="utf-8") as f:
                    print("Coverage report contents:", f.read()[:3000])

            if not os.path.exists(report):
                raise RuntimeError(
                    f"No test report produced. Docker exit code "
                    f"{result.returncode}.\n{result.stderr[-2000:]}"
                )

            root = ET.parse(report).getroot()
            total = failures = errors = 0
            for suite in root.iter("testsuite"):
                total += int(suite.get("tests", 0))
                failures += int(suite.get("failures", 0))
                errors += int(suite.get("errors", 0))

            if total == 0:
                raise RuntimeError("No tests were collected.")

            coverage_percentage = 0.0
            if os.path.exists(coverage):
                with open(coverage, encoding="utf-8") as f:
                    data = json.load(f)
                coverage_percentage = float(
                    data.get("totals", {}).get("percent_covered", 0.0)
                )

            if result.returncode not in (0, 1):
                raise RuntimeError(
                    f"Test infrastructure failed: {result.stderr[-2000:]}"
                )

            return EvaluationMetrics(
                metric_id=metric_id,
                cyclomatic_complexity=0.0,
                halstead_volume=0.0,
                maintainability_index=0.0,
                test_pass_rate=((total - failures - errors) / total) * 100.0,
                coverage_percentage=coverage_percentage,
            )
