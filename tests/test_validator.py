import pytest
from src.trending.application.validator import validate_duration, validate_limit
from src.trending.utils.errors import ValidationError

# ── validate_duration tests ──


def test_valid_duration_day():
    assert validate_duration("day") == "day"


def test_valid_duration_week():
    assert validate_duration("week") == "week"


def test_valid_duration_month():
    assert validate_duration("month") == "month"


def test_valid_duration_year():
    assert validate_duration("year") == "year"


def test_duration_uppercase_accepted():
    assert validate_duration("WEEK") == "week"


def test_duration_mixed_case_accepted():
    assert validate_duration("Month") == "month"


def test_invalid_duration_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_duration("fortnight")
    assert "fortnight" in str(exc_info.value)


def test_invalid_duration_has_correct_field():
    with pytest.raises(ValidationError) as exc_info:
        validate_duration("fortnight")
    assert exc_info.value.field == "duration"


# ── validate_limit tests ──


def test_valid_limit_minimum():
    assert validate_limit(1) == 1


def test_valid_limit_middle():
    assert validate_limit(50) == 50


def test_valid_limit_maximum():
    assert validate_limit(100) == 100


def test_limit_zero_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_limit(0)
    assert exc_info.value.field == "limit"


def test_limit_too_high_raises_error():
    with pytest.raises(ValidationError) as exc_info:
        validate_limit(101)
    assert exc_info.value.field == "limit"


def test_limit_negative_raises_error():
    with pytest.raises(ValidationError):
        validate_limit(-5)


def test_limit_wrong_type_raises_error():
    with pytest.raises(ValidationError):
        validate_limit("ten")
