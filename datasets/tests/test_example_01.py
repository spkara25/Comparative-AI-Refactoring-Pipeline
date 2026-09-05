from datasets.legacy.example_01 import calculate_things

def test_calculate_things():
    assert calculate_things(2, 3) == 5
    assert calculate_things(-1, 1) == 0
    assert calculate_things(0, 0) == 0