# -*- coding: UTF-8 -*-

import logging

LEVEL_DEBUG = 1
LEVEL_INFO = 2
LEVEL_WARN = 3
LEVEL_ERROR = 4


class Logger(object):
    def debug(self, message):  # type: (str) -> None
        pass

    def info(self, message):  # type: (str) -> None
        pass

    def warn(self, message):  # type: (str) -> None
        pass

    def error(self, message):  # type: (str) -> None
        pass


class LoggerProxy(Logger):
    """
    A common logger class, developers can specify behaviors when logs are emitted.
    """

    def __init__(self, log_level, logger):  # type: (int, Logger) -> None
        self.log_level = log_level
        self.logger = logger

    def debug(self, message):  # type: (str) -> None
        if self.log_level <= LEVEL_DEBUG:
            self.logger.debug(message)

    def info(self, message):  # type: (str) -> None
        if self.log_level <= LEVEL_INFO:
            self.logger.info(message)

    def warn(self, message):  # type: (str) -> None
        if self.log_level <= LEVEL_WARN:
            self.logger.warn(message)

    def error(self, message):  # type: (str) -> None
        if self.log_level <= LEVEL_ERROR:
            self.logger.error(message)


class DefaultLogger(Logger):
    """
    This is the default logger which emits logs to python logging APIs
    """

    def __init__(self):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    def debug(self, message):  # type: (str) -> None
        logging.debug(message)

    def info(self, message):  # type: (str) -> None
        logging.info(message)

    def warn(self, message):  # type: (str) -> None
        logging.warning(message)

    def error(self, message):  # type: (str) -> None
        logging.error(message)
