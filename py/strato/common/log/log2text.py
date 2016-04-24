#!/usr/bin/env python
import json
import os
import sys
import time
import signal
import re
import datetime
import logging
import strato.common.log.morelevels

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
CYAN = '\033[36m'
NORMAL_COLOR = '\033[39m'
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

MULTY_LOG_COLORS = (
    "\033[1;30m",
    # "\033[1;41m",
    "\033[1;32m",
    "\033[1;33m",
    "\033[1;34m",
    "\033[1;35m",
    "\033[1;36m",
    "\033[2;30m",
    # "\033[0;41m",
    "\033[2;32m",
    "\033[2;33m",
    "\033[2;34m",
    "\033[2;35m",
    "\033[2;36m",
)
COLOR_OFF = "\033[0;0m"

class Formatter:
    _COLORS = {logging.PROGRESS: CYAN, logging.ERROR: RED, logging.WARNING: YELLOW}

    converter = time.gmtime

    def __init__(self, relativeTime, withThreads, showFullPaths, noDebug, microsecondPrecision, noColors, localTime=False):
        self._firstClock = None
        self._clock = self._relativeClock if relativeTime else self._absoluteClock
        self._relativeClockFormat = "%.6f" if microsecondPrecision else "%.3f"
        self._minimumLevel = logging.INFO if noDebug else logging.DEBUG
        useColors = False if noColors else _runningInATerminal()
        if localTime:
            self.converter = time.localtime
        self._logFormat = \
            "%(log2text_clock)s " + \
            ('%(process)s%(threadName)s:' if withThreads else '') + \
            ('%(log2text_colorPrefix)s' if useColors else '') + \
            "%(levelname)-7s " + \
            "%(message)s" + \
            (NORMAL_COLOR if useColors else '') + \
            ("(%(pathname)s:%(lineno)s)" if showFullPaths else "(%(module)s::%(funcName)s:%(lineno)s)")

    def process(self, obj):
        if obj['levelno'] < self._minimumLevel:
            return None
        if 'args' in obj:
            if isinstance(obj['args'], (dict, tuple)):
                message = obj['msg'] % obj['args']
            elif isinstance(obj['args'], list):
                message = obj['msg'] % tuple(obj['args'])
            else:
                message = obj['msg']
        else:
            message = obj['msg']
        clock = self._clock(obj['created'])
        colorPrefix = self._COLORS.get(obj['levelno'], '')
        formatted = self._logFormat % dict(
            obj, message=message, log2text_clock=clock, log2text_colorPrefix=colorPrefix)
        if obj['exc_text']:
            formatted += "\n" + obj['exc_text']
        return formatted

    def _relativeClock(self, created):
        if self._firstClock is None:
            self._firstClock = created
        return self._relativeClockFormat % (created - self._firstClock)

    def _absoluteClock(self, created):
        msec = (created - long(created)) * 1000
        return '%s.%.03d' % (time.strftime(TIME_FORMAT, self.converter(created)), msec)


def _runningInATerminal():
    return sys.stdout.isatty()


def follow_generator(istream):
    while True:
        newLine = istream.readline()
        if newLine:
            yield newLine
            continue
        time.sleep(0.1)


def printLog(logFile, formatter, follow):
    inputStream = sys.stdin if logFile == "-" else open(logFile)
    if follow:
        inputStream = follow_generator(inputStream)
    for line in inputStream:
        try:
            obj = json.loads(line)
            formatted = formatter.process(obj)
            if formatted is None:
                continue
            print formatted
        except:
            print "Failed to parse record '%s' " % line


def _addLogName(line, colorCode, logFile):
    return "%s %s(%s)%s" % (line, colorCode, logFile, COLOR_OFF)

def _getNextParsableEntry(inputStream, logFile, colorCode, formatter):
    """
    list the file until the next parsable line
    finish when all lines were listed
    """
    while True:
        try:
            line = inputStream.next()
            obj = json.loads(line)
            formatted = formatter.process(obj)
            return obj, None if formatted is None else _addLogName(formatted, colorCode, logFile)
        except StopIteration:
            return None
        except:
            line = line.strip()
            timestampMatch = re.match(r'(\d+\.\d+)(.*)', line)
            if timestampMatch is not None:
                timestamp = float(timestampMatch.group(1).split('.')[0])
                formatted = "%s %s" % (formatter._absoluteClock(timestamp), timestampMatch.group(2))
                return {'created': timestamp}, _addLogName(formatted, colorCode, logFile)
            else:
                dateMatch = re.match(r'(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})', line)
                if dateMatch is not None:
                    dt = datetime.datetime(int(dateMatch.group(1)), int(dateMatch.group(2)), int(dateMatch.group(3)),
                                           int(dateMatch.group(4)), int(dateMatch.group(5)), int(dateMatch.group(6)))
                    timestamp = time.mktime(dt.timetuple())
                    return {'created': timestamp}, _addLogName(line, colorCode, logFile)
                else:
                    return {'created': 0}, line
            # print "Failed to parse record '%s' " % line


def _getColorCode(id):
    return MULTY_LOG_COLORS[id % (len(MULTY_LOG_COLORS) - 1)]


def printLogs(logFiles, formatter):
    inputStreams = [(open(logFile), logFile) for logFile in logFiles]

    # initialize current lines
    currentLines= []
    for streamId, (inputStream, logFile) in enumerate(inputStreams):
        currentLines.append(_getNextParsableEntry(inputStream, logFile, _getColorCode(streamId), formatter))

    while True:
        # finished all input streams
        if not any(currentLines):
            break

        _, nextStreamId, formatted = min((line[0]['created'], streamId, line[1])
                                         for streamId, line in enumerate(currentLines) if line is not None)
        if formatted is not None:
            # prevent printing the Broken Pipe error when 'less' is quitted
            try:
                print formatted
            except IOError as e:
                break

        inputStream = inputStreams[nextStreamId]
        currentLines[nextStreamId] = _getNextParsableEntry(inputStream[0], inputStream[1], _getColorCode(nextStreamId),
                                                           formatter)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("logFiles", metavar='logFile', nargs='+', help='logfiles to read or - for stdin')
    parser.add_argument("--noDebug", action='store_true', help='filter out debug messages')
    parser.add_argument("--relativeTime", action='store_true', help='print relative time, not absolute')
    parser.add_argument("--noColors", action='store_true', help='force monochromatic output even on a TTY')
    parser.add_argument(
        "--noLess", action="store_true", help='Do not pipe into less even when running in a TTY')
    parser.add_argument(
        "--microsecondPrecision", action="store_true",
        help='print times in microsecond precision (instead of millisecond percision)')
    parser.add_argument(
        "--showFullPaths", action='store_true',
        help='show full path to files instead of just module and function')
    parser.add_argument("--withThreads", action="store_true", help='print process and thread name')
    parser.add_argument("-f", "--follow", action="store_true", help='follow file forever', default=False)
    parser.add_argument("-l", "--localtime", action="store_true", help='print logs in localtime (default utc)', default=False)
    args = parser.parse_args()

    if _runningInATerminal and not args.noLess:
        args = " ".join(["'%s'" % a for a in sys.argv[1:]])
        result = os.system(
            "python -m strato.common.log.log2text %s --noLess | less --quit-if-one-screen --RAW-CONTROL-CHARS" % args)
        sys.exit(result)

    formatter = Formatter(
        noDebug=args.noDebug, relativeTime=args.relativeTime, noColors=args.noColors,
        microsecondPrecision=args.microsecondPrecision, showFullPaths=args.showFullPaths,
        withThreads=args.withThreads, localTime=args.localtime)

    def _exitOrderlyOnCtrlC(signal, frame):
        sys.exit(0)
    signal.signal(signal.SIGINT, _exitOrderlyOnCtrlC)

    if len(args.logFiles) == 1:
        printLog(logFile=args.logFiles[0], formatter=formatter, follow=args.follow)
    else:
        printLogs(logFiles=args.logFiles, formatter=formatter)
