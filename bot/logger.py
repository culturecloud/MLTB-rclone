import os
import logging
import sys

from gunicorn.glogging import Logger
from loguru import logger


LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False
LOGGER = logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOG_LEVEL)
        self.access_logger.setLevel(LOG_LEVEL)


intercept_handler = InterceptHandler()
# logging.basicConfig(handlers=[intercept_handler], level=LOG_LEVEL)
# logging.root.handlers = [intercept_handler]
logging.root.setLevel(LOG_LEVEL)

seen = set()
for name in [
    *logging.root.manager.loggerDict.keys(),
    "gunicorn",
    "gunicorn.access",
    "gunicorn.error",
    ]:
    if name not in seen:
        seen.add(name.split(".")[0])
        logging.getLogger(name).handlers = [intercept_handler]

logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
