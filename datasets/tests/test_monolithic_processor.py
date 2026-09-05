from datasets.legacy.monolithic_processor import process_user_records

def test_empty_input():
    result = process_user_records("")
    assert result["valid_count"] == 0
    assert result["total_score"] == 0

def test_valid_records():
    raw = "user1,25,88.5;user2,30,92.0"
    result = process_user_records(raw)
    assert result["valid_count"] == 2
    assert result["total_score"] == 180.5
    assert len(result["errors"]) == 0

def test_invalid_records():
    raw = "bad_user!,20,50;user3,12,60;user4,22,not_num;broken"
    result = process_user_records(raw)
    assert result["valid_count"] == 0
    assert len(result["errors"]) == 4