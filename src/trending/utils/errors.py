class TrendingCLIError(Exception):
    """Base error for all application errors."""

    pass


class ValidationError(TrendingCLIError):
    """Raised when user input fails validation."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)


class APIError(TrendingCLIError):
    """Raised when GitHub API call fails."""

    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(APIError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, reset_time: str = None):
        self.reset_time = reset_time
        message = (
            f"GitHub API rate limit exceeded. "
            f"Resets at: {reset_time or 'unknown time'}. "
            f"Tip: Wait a few minutes and try again."
        )
        super().__init__(message, status_code=403)


class NetworkError(TrendingCLIError):
    """Raised when network connection fails."""

    pass


class ParseError(TrendingCLIError):
    """Raised when API response cannot be parsed."""

    pass
