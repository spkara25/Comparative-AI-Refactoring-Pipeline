from app.services.static_analysis_service import StaticAnalysisService

def test_static_analysis_on_valid_code():
    # 1. Define a piece of Python code to analyze
    code = """
def check_number(x):
    if x > 0:
        return "Positive"
    elif x < 0:
        return "Negative"
    else:
        return "Zero"
"""
    
    # 2. Run the service
    metrics = StaticAnalysisService.analyze_code(code, metric_id=50)
    
    # 3. Assertions
    assert metrics.metric_id == 50
    assert metrics.cyclomatic_complexity > 1.0 # Multiple branches = higher complexity
    assert metrics.halstead_volume > 0.0
    assert 0.0 <= metrics.maintainability_index <= 100.0
    
    print(f"\n[SUCCESS] Code Analyzed! CC: {metrics.cyclomatic_complexity:.2f}, MI: {metrics.maintainability_index:.2f}")

def test_static_analysis_on_syntax_error():
    # 1. Define broken code (missing colon, invalid syntax)
    bad_code = "def broken_function(x) return x"
    
    # 2. Run the service
    metrics = StaticAnalysisService.analyze_code(bad_code)
    
    # 3. Assertions to ensure it fails gracefully without crashing the app
    assert metrics.cyclomatic_complexity == -1.0
    assert metrics.maintainability_index == -1.0
    assert metrics.halstead_volume == -1.0
    
    print("\n[SUCCESS] Syntax error handled gracefully!")