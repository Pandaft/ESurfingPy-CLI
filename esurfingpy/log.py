import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)


class Logger(logging.Logger):

    def __init__(self, name: str):
        super().__init__(name)
        self.log = logging.getLogger(name)

    def debug(self, msg: object, *args, **kwargs) -> object:
        self.log.debug(msg, *args, **kwargs)
        return msg

    def info(self, msg: object, *args, **kwargs) -> object:
        self.log.info(msg, *args, **kwargs)
        return msg

    def warning(self, msg: object, *args, **kwargs) -> object:
        self.log.warning(msg, *args, **kwargs)
        return msg

    def error(self, msg: object, *args, **kwargs) -> object:
        self.log.error(msg, *args, **kwargs)
        return msg

    def critical(self, msg: object, *args, **kwargs) -> object:
        self.log.critical(msg, *args, **kwargs)
        return msg


log = Logger("rich")
