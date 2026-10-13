import os
import sys
from app.models.prompt_configuration import PromptConfiguration
from app.services.dataset_service import DatasetService
from app.services.experiment_runner import ExperimentRunner
from app.services.visual_reporting_service import VisualReportingService
from app.storage.database import get_database_engine
from app.storage.repository import DatabaseRepository
from app.services.logging_config import configure_logging

def main():
    configure_logging()


    print("=" * 60)
    print("COMPARATIVE AI REFACTORING PIPELINE")
    print("=" * 60)

    # 1. Initialize Storage
    print("\n[1/5] Initializing Database & Repository...")
    engine = get_database_engine()
    repo = DatabaseRepository(engine)
    repo.init_schema()
    researcher_id = repo.save_researcher(
        name=os.getenv("RESEARCHER_NAME", "Default Researcher"),
        email=os.getenv("RESEARCHER_EMAIL", "researcher@benchmark.local")
    )
    print(f"✓ Repository initialized. Active Researcher ID: {researcher_id}")

    # 2. Ingest Dataset
    print("\n[2/5] Ingesting Legacy Datasets...")
    legacy_dir = "datasets/legacy"
    dataset = DatasetService.load_from_directory(legacy_dir, dataset_id=1, name="Brownfield Legacy Suite")
    files = dataset.get_code()
    if not files:
        print(f"Error: No Python files found in '{legacy_dir}'.")
        sys.exit(1)
    print(f"✓ Found {len(files)} target file(s): {[os.path.basename(f) for f in files]}")

    # 3. Configure Prompts & Provider
    print("\n[3/5] Setting up Experiment Matrix...")
    prompts = [
        PromptConfiguration(
            prompt_id=1,
            prompt_text="Refactor the code to adhere strictly to PEP8 standards, adding type hints and docstrings.",
            model_name=os.getenv("LLM_MODEL", "mock-default"),
            temperature=0.2
        ),
        PromptConfiguration(
            prompt_id=2,
            prompt_text="Refactor to reduce cyclomatic complexity and optimize conditional logic.",
            model_name=os.getenv("LLM_MODEL", "mock-default"),
            temperature=0.2
        )
    ]
    provider_name = os.getenv("LLM_PROVIDER", "mock")
    print(f"✓ Active Provider: {provider_name}")
    print(f"✓ Prepared {len(prompts)} prompting strategy variations.")

    # 4. Execute Benchmark Matrix
    print("\n[4/5] Executing Refactoring, Static Analysis & Metrics Calculation...")
    runner = ExperimentRunner(repository=repo)
    csv_output = "results/benchmark_report.csv"
    results = runner.run_matrix(
        file_paths=files,
        prompts=prompts,
        providers=[provider_name],
        output_csv=csv_output
    )
    print(f"✓ Benchmark finished. {len(results)} experiment runs evaluated.")
    print(f"✓ Results exported to: {csv_output}")

    # 5. Generate Visual Reports
    print("\n[5/5] Generating Visual Delta Summaries...")
    chart_output = "results/complexity_maintainability_delta.png"
    try:
        VisualReportingService.generate_delta_bar_chart(results, output_filepath=chart_output)
        print(f"✓ Comparison chart exported to: {chart_output}")
    except Exception as e:
        print(f"Warning: Visual generation skipped: {e}")

    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
