import re
import os
import fcntl
import termios
import struct
import logging
import textwrap
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
        record.location = "...%s:%s" % (pathname, record.lineno)
        record.location = record.location.ljust(self.LOCATION_WIDTH).strip()
        return record.location

    def format(self, record):
        self._update_location(record)
        return logging.Formatter.format(self, record)


class ColoringFormatter(Formatter):

    STEP_COUNT = 1

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
        result = logging.Formatter.format(self, record)
        if len(escape_ansi(result)) > get_terminal_size()[0]:
            result = textwrap.fill(result, width=get_terminal_size()[0], subsequent_indent=" " * 60)
        return result


def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def get_terminal_size():
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(columns), int(rows)
    except:
        env = os.environ

        def ioctl_GWINSZ(fd):
            try:
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            except:
                return
            return cr

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
        return int(cr[1]), int(cr[0])  # (width. height)
