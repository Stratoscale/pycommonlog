import logging


def discardLogsOf(loggerName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.CRITICAL)
