from app.services.test_execution_service import TestExecutionService

def test_test_execution_service():
    metrics = TestExecutionService.run_tests(
        test_directory="datasets/tests",
        source_directory="datasets/legacy"
    )
    
    assert metrics.test_pass_rate == 100.0
    assert metrics.coverage_percentage > 0.0
    
    print(f"\n[SUCCESS] Tests Executed! Pass Rate: {metrics.test_pass_rate}%, Coverage: {metrics.coverage_percentage:.2f}%")