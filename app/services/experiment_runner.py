
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.prompt_configuration import PromptConfiguration
from app.models.refactoring_request import RefactoringRequest

from app.services.dataset_service import DatasetService
from app.services.static_analysis_service import StaticAnalysisService
from app.services.ai_refactoring_service import AIRefactoringService
from app.services.provider_factory import ProviderFactory
from app.services.reporting_service import ReportingService
from app.services.docker_sandbox_service import DockerSandboxService

from app.storage.repository import DatabaseRepository
from app.storage.database import get_database_engine


class ExperimentRunner:
    """
    Automates comparative benchmarking across legacy code,
    prompt strategies, and AI providers.

    Static analysis is performed on the host.
    Original and refactored code are tested inside Docker.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
    ):
        if repository is None:
            engine = get_database_engine()
            self.repository = DatabaseRepository(engine)
            self.repository.init_schema()
        else:
            self.repository = repository

        # Resolve the project root independently of the working directory.
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

    def _evaluate_with_sandbox(
        self,
        code: str,
        test_code: str,
        filename: str,
        test_filename: str,
        metric_id: int = 1,
    ):
        """Run a source file and its tests in the Docker sandbox."""
        return DockerSandboxService.run_code_in_sandbox(
            source_code=code,
            test_code=test_code,
            source_filename=filename,
            test_filename=test_filename,
            metric_id=metric_id,
        )

    def _find_test_file(self, filename: str) -> str:
        """Find the test file corresponding to a dataset source file."""
        test_filename = f"test_{os.path.splitext(filename)[0]}.py"
        test_path = os.path.join(
            self.project_root,
            "datasets",
            "tests",
            test_filename,
        )

        if not os.path.isfile(test_path):
            raise FileNotFoundError(
                f"No matching test file found for '{filename}'. "
                f"Expected: {test_path}"
            )

        return test_path

    def run_single(
        self,
        file_path: str,
        prompt_config: PromptConfiguration,
        provider_name: str = "mock",
        researcher_id: int = 1,
    ) -> Dict[str, Any]:
        """Run one comparative experiment for a source file and prompt."""

        filename = os.path.basename(file_path)

        if filename == "__init__.py":
            raise ValueError(
                "Package __init__.py files are not benchmark targets."
            )

        # 1. Read the original source and locate its tests.
        original_code = DatasetService.read_code_content(file_path)
        test_path = self._find_test_file(filename)
        test_filename = os.path.basename(test_path)
        test_code = DatasetService.read_code_content(test_path)

        # 2. Calculate original static-analysis metrics.
        original_metrics = StaticAnalysisService.analyze_code(
            original_code
        )

        # 3. Create the selected AI provider.
        provider = ProviderFactory.create_provider(
            provider_name=provider_name,
            model_name=prompt_config.model_name,
            temperature=prompt_config.temperature,
        )

        ai_service = AIRefactoringService(provider=provider)

        # 4. Generate the refactored version.
        request = RefactoringRequest(
            request_id=1,
            original_code=original_code,
            language="Python",
            status="PENDING",
            prompt_config=prompt_config,
        )

        refactored = ai_service.process_request(request)

        # 5. Calculate refactored static-analysis metrics.
        refactored_metrics = StaticAnalysisService.analyze_code(
            refactored.code_content
        )

        # 6. Execute the original and refactored versions in Docker.
        original_test_metrics = self._evaluate_with_sandbox(
            code=original_code,
            test_code=test_code,
            filename=filename,
            test_filename=test_filename,
        )

        refactored_test_metrics = self._evaluate_with_sandbox(
            code=refactored.code_content,
            test_code=test_code,
            filename=filename,
            test_filename=test_filename,
        )

        # 7. Replace placeholder test metrics with measured values.
        original_metrics.test_pass_rate = (
            original_test_metrics.test_pass_rate
        )
        original_metrics.coverage_percentage = (
            original_test_metrics.coverage_percentage
        )

        refactored_metrics.test_pass_rate = (
            refactored_test_metrics.test_pass_rate
        )
        refactored_metrics.coverage_percentage = (
            refactored_test_metrics.coverage_percentage
        )

        # 8. Persist both sets of metrics.
        original_metric_id = self.repository.save_evaluation_metrics(
            cyclomatic_complexity=(
                original_metrics.cyclomatic_complexity
            ),
            halstead_volume=original_metrics.halstead_volume,
            maintainability_index=(
                original_metrics.maintainability_index
            ),
            test_pass_rate=original_metrics.test_pass_rate,
            coverage_percentage=original_metrics.coverage_percentage,
        )

        refactored_metric_id = self.repository.save_evaluation_metrics(
            cyclomatic_complexity=(
                refactored_metrics.cyclomatic_complexity
            ),
            halstead_volume=refactored_metrics.halstead_volume,
            maintainability_index=(
                refactored_metrics.maintainability_index
            ),
            test_pass_rate=refactored_metrics.test_pass_rate,
            coverage_percentage=refactored_metrics.coverage_percentage,
        )

        # 9. Persist the experiment record.
        provider_display_name = provider.get_provider_name()

        experiment_id = self.repository.save_experiment_result(
            summary=(
                f"Evaluated {filename} with {provider_display_name}"
            ),
            researcher_id=researcher_id,
            model_name=provider_display_name,
            original_metric_id=original_metric_id,
            refactored_metric_id=refactored_metric_id,
        )

        # 10. Generate the reporting row.
        return ReportingService.calculate_row(
            experiment_id=experiment_id,
            timestamp=datetime.now().isoformat(),
            model_name=provider_display_name,
            prompt_strategy=prompt_config.prompt_text[:30] + "...",
            source_file=filename,
            original=original_metrics,
            refactored=refactored_metrics,
        )

    def run_matrix(
        self,
        file_paths: List[str],
        prompts: List[PromptConfiguration],
        providers: List[str],
        output_csv: str = "results/benchmark_report.csv",
    ) -> List[Dict[str, Any]]:
        """Run experiments for every file, prompt, and provider combination."""

        rows: List[Dict[str, Any]] = []

        # Exclude package initialization files.
        benchmark_files = [
            path
            for path in file_paths
            if os.path.basename(path) != "__init__.py"
        ]

        for file_path in benchmark_files:
            for prompt in prompts:
                for provider_name in providers:
                    row = self.run_single(
                        file_path=file_path,
                        prompt_config=prompt,
                        provider_name=provider_name,
                    )
                    rows.append(row)

        # Resolve relative output paths from the project root.
        if not os.path.isabs(output_csv):
            output_csv = os.path.join(self.project_root, output_csv)

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        ReportingService.export_to_csv(
            rows,
            output_filepath=output_csv,
        )

        return rows
