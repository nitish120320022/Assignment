import logging
import sys


def configure_logging() -> None:
    """
    Configure application-wide logging.
    Logs go to stdout so they work well with Docker / Kubernetes.
    """

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)