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

def _formatStratoscaleStyle(line, props, colorCode, logFile):
    try:
        obj = json.loads(line)
        obj['created'] = obj['created'] + props['skew']
        formatted = formatter.process(obj)
        return obj, None if formatted is None else _addLogName(formatted, colorCode, logFile)
    except:
        return None

def _formatTimestampStyle(line, props, colorCode, logFile):
    line = line.strip()
    timestampMatch = re.match(r'(\d+\.\d+)(?P<suffix>.*)', line)
    if timestampMatch is not None:
        timestamp = float(timestampMatch.group(1).split('.')[0]) + props['skew']
        formatted = "%s %s" % (formatter._absoluteClock(timestamp), timestampMatch.groupdict().get('suffix'))
        return {'created': timestamp}, _addLogName(formatted, colorCode, logFile)
    else:
        return None

def _formatDateStyle(line, props, colorCode, logFile):
    line = line.strip()
    dateMatch = re.match(r'(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})(?P<suffix>.*)', line)
    if dateMatch is not None:
        dt = datetime.datetime(int(dateMatch.group(1)), int(dateMatch.group(2)), int(dateMatch.group(3)),
                               int(dateMatch.group(4)), int(dateMatch.group(5)), int(dateMatch.group(6)))
        timestamp = time.mktime(dt.timetuple()) + props['skew']
        formatted = "%s %s" % (formatter._absoluteClock(timestamp), dateMatch.groupdict().get('suffix'))
        return {'created': timestamp}, _addLogName(formatted, colorCode, logFile)
    else:
        return None

def _formatNextEntry(inputStream, logFile, colorCode, formatter, props):
    try:
        line = inputStream.next()
    except StopIteration:
        return None

    stratoscaleStyle = _formatStratoscaleStyle(line, props, colorCode, logFile)
    if stratoscaleStyle is not None:
        return stratoscaleStyle

    timestampStyle = _formatTimestampStyle(line, props, colorCode, logFile)
    if timestampStyle is not None:
        return timestampStyle

    dateStyle = _formatDateStyle(line, props, colorCode, logFile)
    if dateStyle is not None:
        return dateStyle

    # returning the skew here will cause an effect of printing all entries from this log, until some
    # entry which timestamp can be derived will be encountered, because the value of skew is less that values
    # of any other timestamps.
    return {'created': props['skew']}, line.strip()

def _getColorCode(id):
    return MULTY_LOG_COLORS[id % (len(MULTY_LOG_COLORS) - 1)]

def _parseLogFileArg(str):
    parts = str.split('?')
    path = parts[0]
    props = {}
    if len(parts) > 1:
        for prop in parts[1].split('&'):
            keyvalue = prop.split('=')
            if len(keyvalue) > 1:
                props[keyvalue[0]] = keyvalue[1]
            else:
                props[keyvalue[0]] = True
    return path, props

def _parseSkew(skew):
    """
    example skew format '-2h11m5s', any part may be skipped
    """
    skewMatch = re.match(r'(?P<sign>[+-]?)((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?', skew)
    if skewMatch is not None:
        hours = int(skewMatch.groupdict().get('hours') or 0)
        minutes = int(skewMatch.groupdict().get('minutes') or 0)
        seconds = int(skewMatch.groupdict().get('seconds') or 0)
        sign = -1 if (skewMatch.groupdict().get('sign') or '+') == '-' else 1
        skew = sign * (hours * 60 * 60 + minutes * 60 + seconds)
    else:
        skew = 0
    return skew

def _parseLogFileArgs(logFiles):
    res = {}
    for str in logFiles:
        path, props = _parseLogFileArg(str)
        skew = _parseSkew(props.get('skew')) if 'skew' in props else 0
        res[path] = {'skew': skew}
    return res


def printLogs(logFilesRaw, formatter):
    logFileProps = _parseLogFileArgs(logFilesRaw)
    inputStreams = {path: open(path) for path in logFileProps.keys()}
    logId = {path: i for i, path in enumerate(logFileProps.keys())}

    # initialize current lines
    currentLines= {}
    for path, inputStream in inputStreams.iteritems():
        currentLines[path] = _formatNextEntry(inputStream, path, _getColorCode(logId[path]), formatter, logFileProps[path])

    while True:
        # finished all input streams
        if not any(currentLines.values()):
            break

        _, nextPath, formatted = min((line[0]['created'], path, line[1])
                                         for path, line in currentLines.iteritems() if line is not None)
        if formatted is not None:
            # prevent printing the Broken Pipe error when 'less' is quitted
            try:
                print formatted
            except IOError as e:
                break

        currentLines[nextPath] = _formatNextEntry(inputStreams[nextPath], nextPath, _getColorCode(logId[nextPath]),
                                                           formatter, logFileProps[nextPath])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("logFiles", metavar='logFile', nargs='+',
                        help='logfiles to read or - for stdin. '
                             'In a multilog or freeFormat mode, a logFile can be provided with skew attribute that will '
                             'adjust a timestamps on it\'s entries in a following way "consul.log?skew=-1h"')
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
    parser.add_argument("--freeFormat", action="store_true", help='support log files not in Stratoscale format')
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

    if len(args.logFiles) > 1 or args.freeFormat:
        printLogs(logFilesRaw=args.logFiles, formatter=formatter)
    elif len(args.logFiles) == 1:
        printLog(logFile=args.logFiles[0], formatter=formatter, follow=args.follow)
