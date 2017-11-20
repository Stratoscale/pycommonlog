import logging
import strato.common.log.morelevels
from strato.common.log import config

_INFO = logging.INFO
_PROGRESS = logging.PROGRESS
_SUCCESS = logging.SUCCESS
_WARNING = logging.WARNING
_ERROR = logging.ERROR
_CRITICAL = logging.CRITICAL
_STEP = logging.STEP


class Formatter(logging.Formatter):

    LOCATION_WIDTH = 42

    def _update_location(self, record):
        max_pathname_width = self.LOCATION_WIDTH - 3 - len(str(record.lineno))
        pathname = record.pathname
        if len(record.pathname) > max_pathname_width:
            pathname = record.pathname[-max_pathname_width:]
        location = "...%s:%s" % (pathname, record.lineno)
        record.location = location.ljust(self.LOCATION_WIDTH)
        return record.location

    def format(self, record):
        self._update_location(record)
        return logging.Formatter.format(self, record)


class ColoringFormatter(Formatter):
    _RED = '\033[31m'
    _GREEN = '\033[32m'
    _YELLOW = '\033[33m'
    _CYAN = '\033[36m'
    _LIGHT_CYAN = '\033[96m'
    _LIGHT_MAGENTA = '\033[95m'
    _LIGHT_BLUE = '\033[1;34m'
    _LIGHT_GREEN = '\033[92m'
    _SALMON = '\033[91m'
    _NORMAL_COLOR = '\033[39m'

    STEP_COUNT = 1

    def __update_colors(self, record):
        record.endColor = self._NORMAL_COLOR
        if record.levelno == _INFO:
            record.startColor = self._LIGHT_BLUE
        elif record.levelno == _PROGRESS:
            record.startColor = self._CYAN
        elif record.levelno == _SUCCESS:
            record.startColor = self._GREEN
        elif record.levelno == _WARNING:
            record.startColor = self._YELLOW
        elif record.levelno == _STEP:
            record.startColor = self._LIGHT_GREEN
            record.levelname = "STEP [%d]" % self.STEP_COUNT
            self.STEP_COUNT += 1
        elif record.levelno == _ERROR or record.levelno == _CRITICAL:
            record.startColor = self._RED
        else:
            record.startColor = ""

    def _update_colors(self, record):
        record.endColor = config.COLORS['REGULAR']
        if record.levelno == _INFO:
            record.startColor = config.COLORS['LIGHT_BLUE']
        elif record.levelno == _PROGRESS:
            record.startColor = config.COLORS['CYAN']
        elif record.levelno == _SUCCESS:
            record.startColor = config.COLORS['GREEN']
        elif record.levelno == _WARNING:
            record.startColor = config.COLORS['YELLOW']
        elif record.levelno == _STEP:
            record.startColor = config.COLORS['LIGHT_GREEN']
            record.levelname = "STEP [%d]" % self.STEP_COUNT
            self.STEP_COUNT += 1
        elif record.levelno == _ERROR or record.levelno == _CRITICAL:
            record.startColor = config.COLORS['RED']
        else:
            record.startColor = ""

    def format(self, record):
        self._update_colors(record)
        self._update_location(record)
        return logging.Formatter.format(self, record)
