from datasets.legacy.humaneval_2 import truncate_number



METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate(3.5) == 0.5
    assert abs(candidate(1.33) - 0.33) < 1e-6
    assert abs(candidate(123.456) - 0.456) < 1e-6


def test_humaneval_2_functional():
    check(truncate_number)
