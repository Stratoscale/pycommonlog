#!/usr/bin/env python
import json
import os
import sys
import time
import signal
import logging
import strato.common.log.morelevels

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
CYAN = '\033[36m'
NORMAL_COLOR = '\033[39m'
TIME_FORMAT = "%d/%m/%y-%H:%M:%S"


class Formatter:
    _COLORS = {logging.PROGRESS: CYAN, logging.ERROR: RED, logging.WARNING: YELLOW}

    def __init__(self, relativeTime, withThreads, showFullPaths, noDebug, microsecondPrecision, noColors):
        self._firstClock = None
        self._clock = self._relativeClock if relativeTime else self._absoluteClock
        self._relativeClockFormat = "%.6f" if microsecondPrecision else "%.3f"
        self._minimumLevel = logging.INFO if noDebug else logging.DEBUG
        useColors = False if noColors else _runningInATerminal()
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
        return time.strftime(TIME_FORMAT, time.gmtime(created))


def _runningInATerminal():
    return sys.stdout.isatty()


class NonStopableIterator:
    def __init__(self, logFile):
        self.logFile = logFile

    def next(self):
        while True:
            newLine = self.logFile.readline()
            if newLine:
                yield newLine
            time.sleep(0.5)


def printLog(logFile, formatter, follow):
    inputStream = sys.stdin if logFile == "-" else open(logFile)
    if follow:
        inputStream = NonStopableIterator(inputStream)
    for line in inputStream:
        try:
            obj = json.loads(line)
            formatted = formatter.process(obj)
            if formatted is None:
                continue
            print formatted
        except:
            print "Failed to parse record '%s' " % line


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("logFile", help='logfile to read or - for stdin')
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
    args = parser.parse_args()

    if _runningInATerminal and not args.noLess:
        args = " ".join(["'%s'" % a for a in sys.argv[1:]])
        result = os.system(
            "python -m strato.common.log.log2text %s --noLess | less --quit-if-one-screen" % args)
        sys.exit(result)

    formatter = Formatter(
        noDebug=args.noDebug, relativeTime=args.relativeTime, noColors=args.noColors,
        microsecondPrecision=args.microsecondPrecision, showFullPaths=args.showFullPaths,
        withThreads=args.withThreads)

    def _exitOrderlyOnCtrlC(signal, frame):
        sys.exit(0)
    signal.signal(signal.SIGINT, _exitOrderlyOnCtrlC)
    printLog(logFile=args.logFile, formatter=formatter, follow=args.follow)
