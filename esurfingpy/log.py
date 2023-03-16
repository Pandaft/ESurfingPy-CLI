import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)


class Logger(logging.Logger):

    def __new__(cls, name):
        return logging.getLogger(name)

    def debug(self, msg: object, *args, **kwargs) -> object:
        super().debug(msg, *args, **kwargs)
        return msg

    def info(self, msg: object, *args, **kwargs) -> object:
        super().info(msg, *args, **kwargs)
        return msg

    def warning(self, msg: object, *args, **kwargs) -> object:
        super().warning(msg, *args, **kwargs)
        return msg

    def error(self, msg: object, *args, **kwargs) -> object:
        super().error(msg, *args, **kwargs)
        return msg

    def critical(self, msg: object, *args, **kwargs) -> object:
        super().critical(msg, *args, **kwargs)
        return msg


log = Logger("rich")
