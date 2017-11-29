import re
import os
import fcntl
import termios
import struct
import logging
import textwrap
import itertools
import strato.common.log.morelevels
from strato.common.log import config

_INFO = logging.INFO
_PROGRESS = logging.PROGRESS
_SUCCESS = logging.SUCCESS
_WARNING = logging.WARNING
_ERROR = logging.ERROR
_CRITICAL = logging.CRITICAL
_STEP = logging.STEP


def getTerminalSize():
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
    # _RED = '\033[31m'
    # _GREEN = '\033[32m'
    # _YELLOW = '\033[33m'
    # _CYAN = '\033[36m'
    # _LIGHT_CYAN = '\033[96m'
    # _LIGHT_MAGENTA = '\033[95m'
    # _LIGHT_BLUE = '\033[1;34m'
    # _LIGHT_GREEN = '\033[92m'
    # _SALMON = '\033[91m'
    # _NORMAL_COLOR = '\033[39m'

    STEP_COUNT = 1

    # def __update_colors(self, record):
    #     record.endColor = self._NORMAL_COLOR
    #     if record.levelno == _INFO:
    #         record.startColor = self._LIGHT_BLUE
    #     elif record.levelno == _PROGRESS:
    #         record.startColor = self._CYAN
    #     elif record.levelno == _SUCCESS:
    #         record.startColor = self._GREEN
    #     elif record.levelno == _WARNING:
    #         record.startColor = self._YELLOW
    #     elif record.levelno == _STEP:
    #         record.startColor = self._LIGHT_GREEN
    #         record.levelname = "STEP [%d]" % self.STEP_COUNT
    #         self.STEP_COUNT += 1
    #     elif record.levelno == _ERROR or record.levelno == _CRITICAL:
    #         record.startColor = self._RED
    #     else:
    #         record.startColor = ""

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

    def _format(self, record):
        self._update_colors(record)
        self._update_location(record)
        return logging.Formatter.format(self, record)

    def format(self, record):
        self._update_colors(record)
        self._update_location(record)

        right_column = "{:>16s} | {}".format("{} {}".format(record.process, record.threadName), record.location)

        def createColumns(format_str, widths, prefix_width, *columns):
            '''
            format_str describes the format of the report.
            {row[i]} is replaced by data from the ith element of columns.

            widths is expected to be a list of integers.
            {width[i]} is replaced by the ith element of the list widths.

            All the power of Python's string format spec is available for you to use
            in format_str. You can use it to define fill characters, alignment, width, type, etc.

            formatter takes an arbitrary number of arguments.
            Every argument after format_str and widths should be a list of strings.
            Each list contains the data for one column of the report.

            formatter returns the report as one big string.
            '''
            result = []
            for row in zip(*columns):
                # Create a indents for each row...
                sub = []

                # Loop through
                for r in row:
                    # Expand tabs to spaces to make our lives easier
                    r = r.expandtabs()

                    # Find the leading spaces and create indent character
                    if r.find(" ") == 0:
                        i = 0
                        for letters in r:
                            if not letters == " ":
                                break
                            i += 1
                        sub.append(" " * i)
                    else:
                        sub.append("")

                # Actually wrap and create the string to return...
                lines = [textwrap.wrap(elt, width=num, subsequent_indent=' ' * prefix_width + ind) for elt, num, ind in zip(row, widths, sub)]
                for line in itertools.izip_longest(*lines, fillvalue=''):
                    formatted_line = format_str.format(width=widths, row=line)
                    result.append(formatted_line)
            return '\n'.join(result)

        def msg_to_columns(msg, reserve_extra=0):
            datefmt_width = 22
            level_width = 13
            prefix_width = datefmt_width + level_width
            terminal_width = getTerminalSize()[0]
            right_column_width = len(right_column)
            reserved_width = prefix_width + right_column_width + reserve_extra
            widths = [terminal_width - reserved_width, right_column_width]

            # Instead of formatting...rewrite message as desired here
            format_str = '{row[0]:<{width[0]}}{row[1]:<{width[1]}}'
            return createColumns(format_str, widths, prefix_width, [msg], [right_column])

        record.msg = msg_to_columns(record.msg)
        result = super(ColoringFormatter, self).format(record)
        if len(escape_ansi(result)) > getTerminalSize()[0]:
            import ipdb
            ipdb.set_trace()
            record.msg = msg_to_columns(record.msg, reserve_extra=len(escape_ansi(result)) - getTerminalSize()[0])
            try:
                return super(ColoringFormatter, self).format(record)
            except:
                return result
        return result


def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)
