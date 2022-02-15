import logging


def discardLogsOf(loggerNames):
    if isinstance(loggerNames, str):
        loggerNames = [loggerNames]
    for name in loggerNames:
        logger = logging.getLogger(name)
        logger.setLevel(logging.CRITICAL)
