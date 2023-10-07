import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(
        show_path=False,
        markup=True,
        rich_tracebacks=True,
    )]
)

logger = logging.getLogger("rich")


def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)
    return msg


def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)
    return msg


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)
    return msg


def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)
    return msg


def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)
    return msg
