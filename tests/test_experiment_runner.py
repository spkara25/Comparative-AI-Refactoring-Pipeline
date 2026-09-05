import os
from sqlalchemy import create_engine
from app.storage.repository import DatabaseRepository
from app.models.prompt_configuration import PromptConfiguration
from app.services.experiment_runner import ExperimentRunner

def test_experiment_runner_matrix():
    # Setup test in-memory DB
    engine = create_engine("sqlite:///:memory:")
    repo = DatabaseRepository(engine)
    repo.init_schema()
    repo.save_researcher(name="Lead Researcher", email="lead@ai-benchmark.org")

    runner = ExperimentRunner(repository=repo)

    # Define matrix parameters
    files = ["datasets/legacy/example_01.py"]
    prompts = [
        PromptConfiguration(1, "Refactor for readability", "mock-v1", 0.0),
        PromptConfiguration(2, "Refactor to reduce cyclomatic complexity", "mock-v2", 0.2)
    ]
    providers = ["mock"]

    output_csv = "results/test_matrix_report.csv"

    # Run matrix
    results = runner.run_matrix(
        file_paths=files,
        prompts=prompts,
        providers=providers,
        output_csv=output_csv
    )

    # 1 file * 2 prompts * 1 provider = 2 results
    assert len(results) == 2
    assert os.path.exists(output_csv)
    assert results[0]["source_file"] == "example_01.py"
    assert "MockLLMProvider" in results[0]["model_name"]

    # Cleanup temporary artifact
    if os.path.exists(output_csv):
        os.remove(output_csv)