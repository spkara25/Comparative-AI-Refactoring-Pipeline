from sqlalchemy import create_engine
from app.storage.repository import DatabaseRepository

def test_database_repository_persistence():
    # Use an in-memory SQLite database for deterministic test execution
    engine = create_engine("sqlite:///:memory:")
    repo = DatabaseRepository(engine=engine)
    
    # Initialize tables
    repo.init_schema()

    # 1. Persist researcher
    researcher_id = repo.save_researcher(name="Dr. Smith", email="smith@benchmark.org")
    assert researcher_id == 1

    # 2. Persist original and refactored metrics
    orig_metric_id = repo.save_evaluation_metrics(
        cyclomatic_complexity=8.0,
        halstead_volume=120.5,
        maintainability_index=45.2,
        test_pass_rate=100.0,
        coverage_percentage=75.0
    )
    refact_metric_id = repo.save_evaluation_metrics(
        cyclomatic_complexity=3.0,
        halstead_volume=80.0,
        maintainability_index=72.1,
        test_pass_rate=100.0,
        coverage_percentage=90.0
    )
    assert orig_metric_id == 1
    assert refact_metric_id == 2

    # 3. Store experiment result linking the metrics
    exp_id = repo.save_experiment_result(
        summary="Refactored loops into list comprehension",
        researcher_id=researcher_id,
        model_name="mock-provider",
        original_metric_id=orig_metric_id,
        refactored_metric_id=refact_metric_id
    )
    assert exp_id == 1

    # 4. Retrieve and verify
    record = repo.get_experiment_result(result_id=exp_id)
    assert record is not None
    assert record["model_name"] == "mock-provider"
    assert record["original_metric_id"] == orig_metric_id
    assert record["refactored_metric_id"] == refact_metric_id