import logging
import strato.common.log.morelevels

_PROGRESS = logging.PROGRESS
_SUCCESS = logging.SUCCESS
_WARNING = logging.WARNING
_ERROR = logging.ERROR
_CRITICAL = logging.CRITICAL
_STEP = logging.STEP


class ColoringFormatter(logging.Formatter):
    _RED = '\033[31m'
    _GREEN = '\033[32m'
    _YELLOW = '\033[33m'
    _CYAN = '\033[36m'
    _LIGHT_GREEN = '\033[92m'
    _NORMAL_COLOR = '\033[39m'

    STEP_COUNT = 1

    def format(self, record):
        record.endColor = self._NORMAL_COLOR
        if record.levelno == _PROGRESS:
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
        return super(type(self), self).format(record)
