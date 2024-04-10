import logging, inspect, os
from loguru import logger
from dotenv import load_dotenv

__all__ = ["logger"]

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[_InterceptHandler()], level=LOG_LEVEL, force=True)
logger.level(LOG_LEVEL)