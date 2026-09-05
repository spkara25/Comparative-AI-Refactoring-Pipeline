from datasets.legacy.nested_calculator import calculate_shipping

def test_invalid_and_zero():
    assert calculate_shipping(0, "DOMESTIC", "REGULAR") == 0
    assert calculate_shipping(10, "MARS", "PLATINUM") == -1

def test_domestic_platinum():
    assert calculate_shipping(50, "DOMESTIC", "PLATINUM") == 5.0

def test_domestic_gold():
    assert calculate_shipping(5, "DOMESTIC", "GOLD") == 10.0
    assert calculate_shipping(12, "DOMESTIC", "GOLD") == 13.0

def test_domestic_regular():
    assert calculate_shipping(5, "DOMESTIC", "REGULAR") == 8.0
    assert calculate_shipping(15, "DOMESTIC", "REGULAR") == 15.0
    assert calculate_shipping(25, "DOMESTIC", "REGULAR") == 25.0

def test_international_regular_and_coupons():
    assert calculate_shipping(10, "INTERNATIONAL", "REGULAR") == 55.0
    assert calculate_shipping(10, "INTERNATIONAL", "REGULAR", coupon="HALF") == 27.5
    assert calculate_shipping(10, "INTERNATIONAL", "REGULAR", coupon="MINUS5") == 50.0