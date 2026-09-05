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