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
from app.storage.repository import DatabaseRepository
from app.storage.database import get_database_engine

class ExperimentRunner:
    """
    Automates comparative benchmarking across matrices of legacy code,
    prompt strategies, and LLM models.
    """

    def __init__(self, repository: Optional[DatabaseRepository] = None):
        if repository is None:
            engine = get_database_engine()
            self.repository = DatabaseRepository(engine)
            self.repository.init_schema()
        else:
            self.repository = repository

    def run_single(
        self,
        file_path: str,
        prompt_config: PromptConfiguration,
        provider_name: str = "mock",
        researcher_id: int = 1
    ) -> Dict[str, Any]:
        """Executes the pipeline for a single code file and prompt strategy."""
        
        # 1. Read Legacy Code
        original_code = DatasetService.read_code_content(file_path)
        filename = os.path.basename(file_path)

        # 2. Static Analysis on Original Legacy Code
        original_metrics = StaticAnalysisService.analyze_code(original_code)

        # 3. Setup AI Service via Factory
        provider = ProviderFactory.create_provider(
            provider_name=provider_name,
            model_name=prompt_config.model_name,
            temperature=prompt_config.temperature
        )
        ai_service = AIRefactoringService(provider=provider)

        # 4. Create and Process Request
        request = RefactoringRequest(
            request_id=1,
            original_code=original_code,
            language="Python",
            status="PENDING",
            prompt_config=prompt_config
        )
        refactored = ai_service.process_request(request)

        # 5. Static Analysis on Refactored Code
        refactored_metrics = StaticAnalysisService.analyze_code(refactored.code_content)

        # 6. Persist Metrics & Experiment to DB
        orig_m_id = self.repository.save_evaluation_metrics(
            cyclomatic_complexity=original_metrics.cyclomatic_complexity,
            halstead_volume=original_metrics.halstead_volume,
            maintainability_index=original_metrics.maintainability_index,
            test_pass_rate=original_metrics.test_pass_rate,
            coverage_percentage=original_metrics.coverage_percentage
        )
        refact_m_id = self.repository.save_evaluation_metrics(
            cyclomatic_complexity=refactored_metrics.cyclomatic_complexity,
            halstead_volume=refactored_metrics.halstead_volume,
            maintainability_index=refactored_metrics.maintainability_index,
            test_pass_rate=refactored_metrics.test_pass_rate,
            coverage_percentage=refactored_metrics.coverage_percentage
        )
        exp_id = self.repository.save_experiment_result(
            summary=f"Evaluated {filename} with {provider.get_provider_name()}",
            researcher_id=researcher_id,
            model_name=provider.get_provider_name(),
            original_metric_id=orig_m_id,
            refactored_metric_id=refact_m_id
        )

        # 7. Calculate Reporting Row
        return ReportingService.calculate_row(
            experiment_id=exp_id,
            timestamp=datetime.now().isoformat(),
            model_name=provider.get_provider_name(),
            prompt_strategy=prompt_config.prompt_text[:30] + "...",
            source_file=filename,
            original=original_metrics,
            refactored=refactored_metrics
        )

    def run_matrix(
        self,
        file_paths: List[str],
        prompts: List[PromptConfiguration],
        providers: List[str],
        output_csv: str = "results/benchmark_report.csv"
    ) -> List[Dict[str, Any]]:
        """Executes a Cartesian product sweep across files, prompts, and models."""
        rows = []
        for file_path in file_paths:
            for prompt in prompts:
                for provider_name in providers:
                    row = self.run_single(
                        file_path=file_path,
                        prompt_config=prompt,
                        provider_name=provider_name
                    )
                    rows.append(row)

        ReportingService.export_to_csv(rows, output_filepath=output_csv)
        return rows