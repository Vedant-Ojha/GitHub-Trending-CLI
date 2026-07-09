import logging
import sys


def get_logger(name: str, verbose: bool = False) -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        name: Logger name (use __name__ in each module)
        verbose: If True, set level to DEBUG; otherwise WARNING

    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger