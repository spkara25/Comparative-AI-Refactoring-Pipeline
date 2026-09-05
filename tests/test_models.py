from datetime import datetime
from app.models.researcher import Researcher
from app.models.legacy_dataset import LegacyDataset 
from app.models.prompt_configuration import PromptConfiguration
from app.models.refactoring_request import RefactoringRequest 
from app.models.refactored_code import RefactoredCode
from app.models.evaluation_metrics import EvaluationMetrics
from app.models.experiment_result import ExperimentResult 

def test_domain_model_relationships():
    researcher = Researcher(researcher_id = 1, name="Alice", email="alice@research.edu")
    assert researcher.name == "Alice"

    dataset = LegacyDataset(dataset_id = 1, name ="Legacy System A", source ="local", description ="Old Python 2 code", code_files=[])
    dataset.add_code("datasets/legacy/example_01.py")
    assert len(dataset.get_code()) == 1

    prompt = PromptConfiguration(prompt_id = 10, prompt_text = "Refactor this to clean Python 3", model_name = "mock-model", temperature =0.2)
    assert prompt.validate_prompt() == True
    request = RefactoringRequest(request_id = 100, original_code ="defo foo(): print 'bar'", language ="Python", status="DRAFT", prompt_config= prompt)
    request.submit()
    assert request.status == "SUBMITTED"
    refactored = RefactoredCode(code_id=500, code_content="def foo():\n    print('bar')", language="Python", request_id=request.request_id)
    assert refactored.compare_with_original(request.original_code) == True

    # 6. Mock Metrics
    orig_metrics = EvaluationMetrics(1, 10.0, 50.0, 45.0, 100.0, 80.0)
    new_metrics = EvaluationMetrics(2, 5.0, 40.0, 65.0, 100.0, 95.0)

    experiment = ExperimentResult(
        result_id=1000,
        experiment_date=datetime.now(),
        summary="Improved maintainability score.",
        researcher=researcher,
        request=request,
        refactored_code=refactored,
        original_metrics=orig_metrics,
        refactored_metrics=new_metrics
    )

    assert experiment.researcher.researcher_id == 1
    assert experiment.refactored_metrics.maintainability_index > experiment.original_metrics.maintainability_index
    print("\n[SUCCESS] Domain model instantiated and relationships verified successfully!")