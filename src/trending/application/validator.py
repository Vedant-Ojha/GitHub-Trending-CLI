from ..utils.config import config
from ..utils.errors import ValidationError


def validate_duration(duration: str) -> str:
    """
    Validate --duration argument.

    Args:
        duration: Raw string from CLI argument

    Returns:
        Validated lowercase duration string

    Raises:
        ValidationError: If duration is not in allowed values
    """
    if not isinstance(duration, str):
        raise ValidationError(
            f"Duration must be a string, got {type(duration).__name__}",
            field="duration"
        )

    normalized = duration.strip().lower()

    if normalized not in config.VALID_DURATIONS:
        valid = ", ".join(config.VALID_DURATIONS)
        raise ValidationError(
            f"Invalid duration '{duration}'. "
            f"Must be one of: {valid}",
            field="duration"
        )

    return normalized


def validate_limit(limit: int) -> int:
    """
    Validate --limit argument.

    Args:
        limit: Integer value from CLI argument

    Returns:
        Validated integer limit

    Raises:
        ValidationError: If limit is outside allowed range
    """
    if not isinstance(limit, int):
        raise ValidationError(
            f"Limit must be an integer, got {type(limit).__name__}",
            field="limit"
        )

    if limit < config.MIN_LIMIT:
        raise ValidationError(
            f"Limit must be at least {config.MIN_LIMIT}, "
            f"got {limit}",
            field="limit"
        )

    if limit > config.MAX_LIMIT:
        raise ValidationError(
            f"Limit cannot exceed {config.MAX_LIMIT}, "
            f"got {limit}",
            field="limit"
        )

    return limit