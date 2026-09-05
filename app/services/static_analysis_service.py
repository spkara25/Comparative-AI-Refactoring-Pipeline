import radon.complexity as cc_module
import radon.metrics as metrics_module
from app.models.evaluation_metrics import EvaluationMetrics

class StaticAnalysisService:
    """
    Performs static analysis on Python source code using radon.
    Extracts Complexity, Halstead Volume, and Maintainability Index.
    """

    @staticmethod
    def analyze_code(code: str, metric_id: int = 1) -> EvaluationMetrics:
        """
        Analyzes a string of Python code and returns an EvaluationMetrics object.
        If the code has syntax errors, it safely returns -1.0 for the metrics.
        """
        if not code.strip():
            # Empty code baseline
            return EvaluationMetrics(metric_id, 0.0, 0.0, 100.0, 0.0, 0.0)

        try:
            # 1. Cyclomatic Complexity
            cc_blocks = cc_module.cc_visit(code)
            if cc_blocks:
                # Average complexity of all functions/classes in the file
                avg_cc = sum(block.complexity for block in cc_blocks) / len(cc_blocks)
            else:
                avg_cc = 1.0 # Base complexity for straight-line code
                
            # 2. Maintainability Index
            # Returns a score usually between 0 (very hard to maintain) and 100 (very easy)
            mi = metrics_module.mi_visit(code, multi=False)
            
            # 3. Halstead Volume
            halstead = metrics_module.h_visit(code)
            # Radon's return structure can vary, so we safely extract the volume
            if isinstance(halstead, tuple) and hasattr(halstead[0], 'volume'):
                volume = halstead[0].volume
            elif hasattr(halstead, 'volume'):
                volume = halstead.volume # type: ignore
            else:
                volume = 0.0

        except SyntaxError:
            # If AI generates broken Python code, we penalize it with -1.0
            avg_cc = -1.0
            mi = -1.0
            volume = -1.0
        except Exception:
            # Catch-all for unexpected radon parsing errors
            avg_cc = 0.0
            mi = 0.0
            volume = 0.0

        return EvaluationMetrics(
            metric_id=metric_id,
            cyclomatic_complexity=float(avg_cc),
            halstead_volume=float(volume),
            maintainability_index=float(mi),
            test_pass_rate=0.0,      # We will populate this in Phase 5
            coverage_percentage=0.0  # We will populate this in Phase 5
        )