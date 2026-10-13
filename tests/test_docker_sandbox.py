import pytest
import subprocess
from app.services.docker_sandbox_service import DockerSandboxService

def check_docker_running():
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False

# Skip this test gracefully if Docker Desktop is closed
@pytest.mark.skipif(not check_docker_running(), reason="Docker is not installed or running.")
def test_docker_sandbox_execution():
    # 1. Build the Docker image (takes a few seconds the first time)
    DockerSandboxService.build_image()
    
    # 2. Run the secure pipeline
    metrics = DockerSandboxService.run_tests_in_sandbox()
    
    # 3. Assertions
    assert metrics.test_pass_rate == 100.0
    assert metrics.coverage_percentage > 0.0
    
    print(f"\n[SUCCESS] Sandbox Executed Safely! Pass Rate: {metrics.test_pass_rate}%, Coverage: {metrics.coverage_percentage:.2f}%")


def test_docker_sandbox_runs_specific_code():
    source_code = """
def calculate_things(x, y):
    return x + y
"""

    test_code = """
from datasets.legacy.example_01 import calculate_things

def test_addition():
    assert calculate_things(2, 3) == 5
    assert calculate_things(-1, 1) == 0
    assert calculate_things(0, 0) == 0
"""

    metrics = DockerSandboxService.run_code_in_sandbox(
        source_code=source_code,
        test_code=test_code,
        source_filename="example_01.py",
        test_filename="test_example_01.py",
    )

    assert metrics.test_pass_rate == 100.0
    assert metrics.coverage_percentage > 0.0
