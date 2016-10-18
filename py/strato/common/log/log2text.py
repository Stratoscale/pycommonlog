#!/usr/bin/env python
import json
import os
import sys
import time
import signal
import logging
import yaml
import glob
import strato.common.log.morelevels
import socket
import subprocess
import re
import gzip
import select
import dateparser
from strato.common.log import lineparse


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
LOG_CONFIG_FILE_PATH = "/etc/stratoscale/strato-log.conf"
HIGHEST_PRIORITY = 0
EPOCH_HOUR = 3600


class Formatter:
    _COLORS = {logging.PROGRESS: CYAN, logging.ERROR: RED, logging.WARNING: YELLOW}

    converter = time.gmtime

    def __init__(self, relativeTime, withThreads, showFullPaths, minimumLevel, microsecondPrecision, noColors, utc=False, sinceTime=None, untilTime="01/01/2025"):
        try:
            self.configFile = yaml.load(open(LOG_CONFIG_FILE_PATH, 'r').read())
            if self.configFile['defaultTimezone'] != None:
                self._localTimezoneOffset = self.configFile['defaultTimezone'] * EPOCH_HOUR
            else:
                self._localTimezoneOffset = lineparse.getTimezoneOffset()
        except:
            self._localTimezoneOffset = lineparse.getTimezoneOffset()
            print "Failed to load config file. Please check the configuration"
        self._firstClock = None
        self._clock = self._relativeClock if relativeTime else self._absoluteClock
        self._relativeClockFormat = "%.6f" if microsecondPrecision else "%.3f"
        self._minimumLevel = minimumLevel
        if sinceTime:
            self._sinceTime = int(time.mktime(dateparser.parse(sinceTime).timetuple()))
        else:
            self._sinceTime = 0
        self._untilTime = int(time.mktime(dateparser.parse(untilTime).timetuple()))
        self._exceptionLogsFileColorMapping = {}
        useColors = False if noColors else _runningInATerminal()
        if not utc:
            self.converter = time.localtime
        self._logFormat = \
            "%(log2text_clock)s " + \
            ('%(process)s%(threadName)s:' if withThreads else '') + \
            ('%(log2text_colorPrefix)s' if useColors else '') + \
            "%(levelname)-7s " + \
            "%(message)s" + \
            (NORMAL_COLOR if useColors else '') + \
            ("(%(pathname)s:%(lineno)s)" if showFullPaths else "(%(module)s::%(funcName)s:%(lineno)s)")

    def process(self, line, logTypeConf=None):
        formatted, timestamp = None, None
        try:
            parsed = json.loads(line)
            if 'msg' in parsed:
                formatted, timestamp = self._processStratolog(line)
            elif 'message' in parsed:
                formatted, timestamp = self._processExceptionLog(line)
        except:
            formatted, timestamp = self._processGenericLog(line, logTypeConf)

        if timestamp >= self._sinceTime and (timestamp <= self._untilTime or self._untilTime == -1):
            return formatted, timestamp
        else:
            return None, None

    def _getLogTypeConf(self, logPath):
        try:
            for logType in self.configFile['logTypes']:
                for pattern in logType['paths']:
                    if re.compile(pattern).match(os.path.basename(logPath)):
                        return logType
            return None
        except:
            return None

    def _processGenericLog(self, line, logTypeConf):
        try:
            msg, timestamp = lineparse.seperateTimestamp(line, logTypeConf['logFormat']['timestamp'])
            if logTypeConf['timeStampFormat']:
                epochTime = lineparse.translateToEpoch(timestamp, logTypeConf['timeStampFormat'])
            else:
                epochTime = float(timestamp)
            if logTypeConf['timezoneOffset'] == 'localtime':
                epochTime += self._localTimezoneOffset
            return line.strip().replace(timestamp, self._clock(epochTime)), epochTime
        except:
            # in case the line wasn't able to get parsed for some reason, print it as when you encounter it
            return line.strip('\n'), HIGHEST_PRIORITY

    def _processStratolog(self, line):
        parsedLine = json.loads(line)
        if parsedLine['levelno'] < self._minimumLevel:
            return None, 0

        if 'args' in parsedLine and parsedLine['args']:
            if isinstance(parsedLine['args'], (dict, tuple)):
                message = parsedLine['msg'] % parsedLine['args']
            elif isinstance(parsedLine['args'], list):
                message = parsedLine['msg'] % tuple(parsedLine['args'])
            else:
                message = parsedLine['msg'].replace('%', '%%')
        else:
            message = parsedLine['msg'].replace('%', '%%')
        clock = self._clock(parsedLine['created'])
        colorPrefix = self._COLORS.get(parsedLine['levelno'], '')
        formatted = self._logFormat % dict(
            parsedLine, message=message, log2text_clock=clock, log2text_colorPrefix=colorPrefix)
        if parsedLine['exc_text']:
            formatted += "\n" + parsedLine['exc_text']
        return formatted, parsedLine['created']

    def _processExceptionLog(self, line):
        parsedLine = json.loads(line)
        line = parsedLine['message']
        logPath = parsedLine['source']
        if logPath not in self._exceptionLogsFileColorMapping:
            self._exceptionLogsFileColorMapping[logPath] = _getColorCode(len(self._exceptionLogsFileColorMapping))
        logTypeConf = self._getLogTypeConf(logPath)
        line, timestamp = self.process(line, logTypeConf)
        return _addLogName(line, self._exceptionLogsFileColorMapping[logPath], logPath), timestamp

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


def printLog(logFile, formatter, follow, tail):
    if logFile:
        inputStream = universalOpen(logFile[0], 'r', tail=tail)
        logTypeConf = formatter._getLogTypeConf(logFile[0])
    else:
        inputStream = sys.stdin
        logTypeConf = None

    if follow:
        inputStream = follow_generator(inputStream)
    for line in inputStream:
        try:
            formatted, timestamp = formatter.process(line, logTypeConf)
            if formatted is None:
                continue
            print formatted
        except IOError:
            inputStream.close()
            break
        except:
            print "Failed to parse record '%s' " % line


def _addLogName(line, colorCode, logFile):
    return "%s %s(%s)%s" % (line, colorCode, os.path.basename(logFile), COLOR_OFF)

def _getNextParsableEntry(inputStream, logFile, colorCode, formatter):
    """
    list the file until the next parsable line
    finish when all lines were listed
    """
    logTypeConf = formatter._getLogTypeConf(logFile)
    while True:
        try:
            line = inputStream.next()
            formatted, timestamp = formatter.process(line, logTypeConf)
            return None if formatted is None else _addLogName(formatted, colorCode, logFile), timestamp
        except StopIteration:
            return None
        except:
            return line, HIGHEST_PRIORITY

def _getColorCode(id):
    return MULTY_LOG_COLORS[id % (len(MULTY_LOG_COLORS) - 1)]


def printLogs(logFiles, formatter, tail):
    inputStreams = [(universalOpen(logFile, 'r', tail=tail), logFile) for logFile in logFiles]

    currentLines= [_getNextParsableEntry(inputStream, logFile, _getColorCode(streamId), formatter)
                   for streamId, (inputStream, logFile) in enumerate(inputStreams)]

    while any(currentLines):
        _, nextStreamId, formatted = min((line[1], streamId, line[0])
                                         for streamId, line in enumerate(currentLines) if line is not None)
        if formatted is not None:
            # prevent printing the Broken Pipe error when 'less' is quit
            try:
                print formatted
            except IOError as e:
                break

        inputStream = inputStreams[nextStreamId]
        currentLines[nextStreamId] = _getNextParsableEntry(inputStream[0], inputStream[1], _getColorCode(nextStreamId),
                                                           formatter)


def updateConfFile(field, value):
    try:
        with open(LOG_CONFIG_FILE_PATH, 'r') as f:
            conf = yaml.load(f.read())
    except:
        print "No configuration file was found. creating new"
        conf = {}
    finally:
        conf[field] = value
    with open('/tmp/stratolog-conf.tmp', 'w') as f:
        f.write(yaml.dump(conf))
        f.close()
    os.system('sudo mv /tmp/stratolog-conf.tmp %s' % LOG_CONFIG_FILE_PATH)


def universalOpen(filePath, mode='r', tail=0):
    if filePath.endswith('.gz'):
        fileObj = gzip.GzipFile(filePath, mode)
    else:
        if tail > 0:
            fileObj = tailFile(filePath, tail)
        else:
            fileObj = open(filePath, mode)
    return fileObj

def tailFile(filePath, n):
    p = subprocess.Popen(["tail", "-n", str(n), filePath], stdout=subprocess.PIPE)
    return p.stdout

def checkSshConnectivity(host):
    try:
        ip = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((ip, 22))
        s.close()
        return True
    except Exception as e:
        if e.message == "timed out":
            print "Connection has timed out on host %s" % host
            s.close()
        return False

def runRemotely(host, ignoreArgs):
    try:
        configFile = yaml.load(open(LOG_CONFIG_FILE_PATH, 'r').read())
    except:
        configFile = {}
        print "Configuration file was not found"

    args = [arg for arg in sys.argv[1:] if arg not in ignoreArgs]
    command = "strato-log %s" % ' '.join(args)

    user = configFile.get("defaultRemoteUser", 'root')
    password = configFile.get("defaultRemotePassword", 'password')

    possibleResolveSuffixes = configFile.get("possibleResolveSuffixes", [])
    hostname = findHostname(host, possibleResolveSuffixes)
    if hostname == None:
        print "No reachable host was found for %s" % host
        return 1

    host = "%(user)s@%(hostname)s" % dict(user=user,
                                          hostname=hostname)

    sshCommand = 'sshpass -p %(password)s ssh -X -f -o ServerAliveInterval=5 -o ServerAliveCountMax=1 -o ' \
                 'StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 ' \
                 '%(host)s %(command)s | less -r'

    os.system(sshCommand % dict(command=command,
                                host=host,
                                password=password))
    return 0

def findHostname(host, possibleResolveSuffixes):
    if checkSshConnectivity(host):
        return host
    else:
        for suffix in possibleResolveSuffixes:
            if checkSshConnectivity(host + suffix):
                return host + suffix
    return None


class LogPathFinder:
    def __init__(self, confFile):
        try:
            self.confFile = yaml.load(open(confFile, 'r').read())
        except:
            pass
        self.defaultPaths = []

    def findLogFiles(self, providedPaths, extensionsToIgnore, showAll=False):
        if showAll:
            extensionsToIgnore = []
        logsToRead = []
        [logsToRead.append(filePath) if os.path.isfile(filePath) else
         logsToRead.extend(self._tryToMatchShortcut(filePath, extensionsToIgnore)) for filePath in providedPaths]
        return logsToRead

    def filterIgnoredExtensions(self, listPaths, ignoredExtensions):
        for path in list(listPaths):
            for ignoredExtension in ignoredExtensions:
                if path.endswith(ignoredExtension):
                    listPaths.remove(path)

    def _tryToMatchShortcut(self, filePath, extensionsToIgnore):
        try:
            if filePath in self.confFile['defaultBundles']:
                return self.matchBundle(filePath)
            else:
                matches = self.tryToMatchDefaultPath(filePath)
                self.filterIgnoredExtensions(matches, extensionsToIgnore)
                return matches
        except:
            raise Exception("No matching files were found for %s" % filePath)

    def matchBundle(self, filePath):
        filesInBundle = glob.glob(self.confFile['defaultBundles'][filePath])
        if filesInBundle:
            return filesInBundle
        else:
            raise Exception("No matching files were found for %s" % filePath)

    def tryToMatchDefaultPath(self, filePath):
        if not self.defaultPaths:
            self._getDefaultPaths()
        matchingFiles = [defaultFilePath for defaultFilePath in self.defaultPaths
                         if filePath.lower() in defaultFilePath.lower() and os.path.isfile(defaultFilePath)]
        if not matchingFiles:
            raise Exception("No matching files were found for %s" % filePath)
        else:
            return matchingFiles

    def _getDefaultPaths(self):
        for filePath in self.confFile['defaultPaths']:
            self.defaultPaths.extend(glob.glob(filePath))

def executeRemotely(args):
    if args.user != None:
        updateConfFile('defaultRemoteUser', args.user)
        ignoreArgs.extend(['-u', '--user', args.user])

    if args.password != None:
        updateConfFile('defaultRemotePassword', args.password)
        ignoreArgs.extend(['-p', '--password', args.password])

    ignoreArgs.extend(['-n', '--node', args.node])
    return runRemotely(args.node, ignoreArgs)


def minimumLevel(minLevel, noDebug):
    if minLevel is None:
        return logging.INFO if noDebug else logging.DEBUG
    level_dict = {'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'progress': logging.PROGRESS,
                  'success': logging.SUCCESS,
                  'step': logging.STEP}
    for string, level in level_dict.iteritems():
        if string.startswith(minLevel.lower()):
            return level
    return logging.DEBUG


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("logFiles", metavar='logFile', nargs='*', help='logfiles to read')
    parser.add_argument('-d', "--noDebug", action='store_true', help='filter out debug messages')
    parser.add_argument('-l', '--min-level', action='store', default='', metavar='LEVEL', help='minimal log level to display (substring is OK, case-insensitive)')
    parser.add_argument('-r', "--relativeTime", action='store_true', help='print relative time, not absolute')
    parser.add_argument('-C', "--noColors", action='store_true', help='force monochromatic output even on a TTY')
    parser.add_argument('-L',
        "--noLess", action="store_true", help='Do not pipe into less even when running in a TTY')
    parser.add_argument('-m',
        "--microsecondPrecision", action="store_true",
        help='print times in microsecond precision (instead of millisecond percision)')
    parser.add_argument(
        "--showFullPaths", action='store_true',
        help='show full path to files instead of just module and function')
    parser.add_argument("--withThreads", action="store_true", help='print process and thread name')
    parser.add_argument("-f", "--follow", action="store_true", help='follow file forever', default=False)
    parser.add_argument("-U", "--utc", action="store_true", help='print logs in UTC time (default: localtime)', default=False)
    parser.add_argument("--setLocaltimeOffset", type=int, metavar='HOURS', help='set custom localtime offset in hours')
    parser.add_argument("-i", "--ignoreExtensions", nargs="+", metavar='EXT', help="list extensions that you don\'t want to read", default=[".gz"])
    parser.add_argument("-a", "--showAll", action="store_true", help='show all logs', default=False)
    parser.add_argument("-n", "--node", type=str, help='run strato-log on remote node (possible input is host name or service with DNS resolve', default=None)
    parser.add_argument("-p", "--password", type=str, help='set default remote password to connect with', default=None)
    parser.add_argument("-u", "--user", type=str, help='set default remote user to connect with', default=None)
    parser.add_argument("--restoreLocaltimeOffset", action="store_true", help='restore localtime offset to machine\'s offset')
    parser.add_argument("-t", "--tail", type=int, metavar='n', help='print n last lines only', default=0)
    parser.add_argument("--since", type=str, metavar='DATE', help='Show entries not older than the specified date (e.g., 1h, 5m, two hours ago, 8/aug/1997)')
    parser.add_argument("--until", type=str, metavar='DATE', help='Show entries not newer than the specified date (e.g., 0.5h, 4m, one hour ago)', default="01/01/2025")

    args, unknown = parser.parse_known_args()
    ignoreArgs = []

    if select.select([sys.stdin,],[],[],0.0)[0]:
        stdin = True
    else:
        stdin = False

    if len(sys.argv) <= 1 and not stdin:
        print 'No input was provided'
        exit(1)

    if args.node != None:
        exit(executeRemotely(args))

    elif unknown:
        for arg in unknown:
            print "Not a valid argument \"%s\"" % arg
        exit(1)

    if args.setLocaltimeOffset != None:
        updateConfFile('defaultTimezone', args.setLocaltimeOffset)

    if args.restoreLocaltimeOffset == True:
        updateConfFile('defaultTimezone', None)

    if _runningInATerminal and not args.noLess:
        args = " ".join(["'%s'" % a for a in sys.argv[1:]])
        result = os.system(
            "python -m strato.common.log.log2text %s --noLess | less --quit-if-one-screen --RAW-CONTROL-CHARS" % args)
        sys.exit(result)

    formatter = Formatter(
        minimumLevel=minimumLevel(args.min_level, args.noDebug), relativeTime=args.relativeTime, noColors=args.noColors,
        microsecondPrecision=args.microsecondPrecision, showFullPaths=args.showFullPaths,
        withThreads=args.withThreads, utc=args.utc, sinceTime=args.since, untilTime=args.until)

    def _exitOrderlyOnCtrlC(signal, frame):
        sys.exit(0)
    signal.signal(signal.SIGINT, _exitOrderlyOnCtrlC)
    if args.logFiles:
        logFinder = LogPathFinder(LOG_CONFIG_FILE_PATH)
        logFiles = logFinder.findLogFiles(args.logFiles, args.ignoreExtensions, args.showAll)
    else:
        logFiles = []

    if stdin or len(logFiles) == 1:
    # use this function in case there is a single file read or there is something in stdin (single stream)
        printLog(logFile=logFiles, formatter=formatter, follow=args.follow, tail=args.tail)
    else:
        printLogs(logFiles=logFiles, formatter=formatter, tail=args.tail)

