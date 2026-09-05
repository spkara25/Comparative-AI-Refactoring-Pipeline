from dataclasses import dataclass 
from datetime import datetime
from app.models.researcher import Researcher
from app.models.refactoring_request import RefactoringRequest
from app.models.refactored_code import RefactoredCode
from app.models.evaluation_metrics import EvaluationMetrics

@dataclass
class ExperimentResult:
    result_id : int
    experiment_date : datetime
    summary : str
    researcher : Researcher
    request : RefactoringRequest
    refactored_code: RefactoredCode
    original_metrics : EvaluationMetrics
    refactored_metrics : EvaluationMetrics

    def generate_report(self) -> str:
        return f"Report {self.result_id} generated on {self.experiment_date}"