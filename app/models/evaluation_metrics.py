from dataclasses import dataclass

@dataclass
class EvaluationMetrics:
    metric_id : int
    cyclomatic_complexity: float
    halstead_volume : float
    maintainability_index : float
    test_pass_rate : float 
    coverage_percentage: float

    def calculate_metrics(self):
        pass
    