from strato.common.log import config
from strato.common.log import machinereadableformatter
from strato.common.log import coloringformatter
import logging
import logging.config
import os
import sys
import atexit
import json
import subprocess
import signal

_name = None
_registered_file_handles = dict()


def logFilename(name):
    return '%s/%s%s' % (config.LOGS_DIRECTORY, name, config.LOGS_SUFFIX)


def configureLogging(name, forceDirectory=None, registerConfigurationReloadSignal=True):
    """
    This is the 'setUp' function for logging. Should be called once, as early as possible
    (a good idea is to call this even before 'import' statements).
    Note: control over the logging level should be by way of STRATO_LOGS_CONFIGURATION_FILE
    environment variable, which should point to a json text file with the "dict config"
    for the loggers (look at python logging documentation for details, or example in config.py)
    """
    global _name
    _name = name
    if forceDirectory is not None:
        os.environ['STRATO_CONFIG_LOGGING'] = os.environ.get('STRATO_CONFIG_LOGGING', '') + \
            '\nLOGS_DIRECTORY = "%s"\n' % os.path.join(os.getcwd(), forceDirectory)
        config.LOGS_DIRECTORY = forceDirectory
    _configureOutputToScreen(logging.getLogger(), name)
    _configureOutputToFile(logging.getLogger(), name)
    _configureLogLevels(name)
    if os.path.exists('/usr/bin/hostname'):
        hostname = subprocess.check_output('/usr/bin/hostname').strip()
    else:
        hostname = subprocess.check_output('/bin/hostname').strip()
    if registerConfigurationReloadSignal:
        _configureLoggingSignalHandlers()

    from py.strato.tests.monitors import loggerconfig
    log=loggerconfig.LogStashLogger(loggerName="_logs", messageType="_logs", verbose=False)

    _log = log.getLogger()
    _log.setLevel(logging.INFO)

    logging.root.addHandler(_log)


    logging.info("Logging started for '%(name)s' on '%(hostname)s'", dict(
        name=name, hostname=hostname))


def configureLogger(loggerName):
    """
    The purpose of this function is to setup a non-root logger.
    This function should be called only after configureLogging has already been called.
    Note: control over the logging level should be by way of STRATO_LOGS_CONFIGURATION_FILE
    environment variable, which should point to a json text file with the "dict config"
    for the loggers (look at python logging documentation for details, or example in config.py)
    """
    assert loggerName is not None
    global _name
    assert _name is not None, "configureLogging must be called first, before any call to 'configureLogger'"
    logging.getLogger(loggerName).propagate = False
    _configureOutputToScreen(logging.getLogger(loggerName), loggerName)
    outputFilename = "%s__%s" % (_name, loggerName)
    _configureOutputToFile(logging.getLogger(loggerName), outputFilename)

def addFileHandler(name, path):
    fileHandler = logging.FileHandler(filename=path)
    formatter = logging.Formatter(
        '%(created).03f(%(process)d%(threadName)s):%(levelname)s:%(message)s (%(pathname)s:%(lineno)d)')
    fileHandler.setFormatter(formatter)
    fileHandler.set_name(name)
    fileHandler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(fileHandler)
    logging.info("Logging started for %s" % name)


def changeHandlerLogLevelbyHandlerType(logger, logLevel, handlerType=None):
    """ if not specifying handlers type (leaving it None) , log level will be changed to all handlers """
    [handler.setLevel(logLevel) for handler in logger.handlers if not handlerType or type(handler) == handlerType]


def _findCaller():
    f = sys._getframe(3)
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if 'logging/__init__.py' in filename or 'common/log/morelevels.py' in filename:
            f = f.f_back
            continue
        return (filename, f.f_lineno, co.co_name)
    return ("(unknown file)", 0, "(unknown function)")


def _useColorsForScreenOutput():
    if 'STRATO_LOGS_NO_COLORS' in os.environ:
        return False
    if 'STRATO_FORCE_COLORS' in os.environ:
        return True
    if os.system("stty > /dev/null 2>&1") != 0:
        return False
    return True


def _configureOutputToScreen(logger, loggerName):
    if logger.handlers == []:
        streamHandler = logging.StreamHandler()
        if _useColorsForScreenOutput():
            streamHandler.setFormatter(coloringformatter.ColoringFormatter(
                '%(created).03f(%(process)d%(threadName)s):%(startColor)s%(levelname)s'
                ': %(message)s%(endColor)s (%(pathname)s:%(lineno)d)'))
        else:
            streamHandler.setFormatter(logging.Formatter(
                '%(created).03f(%(process)d%(threadName)s):%(levelname)s:%(message)s '
                '(%(pathname)s:%(lineno)d)'))
        handlerName = "console_%s" % loggerName if loggerName != _name else "console"
        streamHandler.set_name(handlerName)
        streamHandler.setLevel(logging.DEBUG)
        logger.addHandler(streamHandler)


def _configureOutputToFile(logger, logName):
    if not os.path.isdir(config.LOGS_DIRECTORY):
        os.makedirs(config.LOGS_DIRECTORY, mode=0777)
    handler = logging.FileHandler(filename=logFilename(logName))
    atexit.register(handler.close)
    handler.setFormatter(machinereadableformatter.MachineReadableFormatter())
    handlerName = "file_%s" % logName if logName != _name else "file"
    handler.set_name(handlerName)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    global _registered_file_handles
    _registered_file_handles[logName] = (logger, handler)
    logger.findCaller = _findCaller

def _configureLogLevels(name):
    if config.LOG_CONFIGURATION is not None:
        with open(config.LOG_CONFIGURATION, 'rt') as f:
            dictConfig = json.load(f)
    else:
        dictConfig = config.DEFAULT_LOG_CONFIGURATION
    if os.path.exists(config.LOGS_CONFIGURATION_OVERRIDE_FILE):
        try:
            with open(config.LOGS_CONFIGURATION_OVERRIDE_FILE, 'rt') as f:
                overrides = json.load(f)
        except: #pylint: disable=bare-except
            overrides = {}
        default_overrides = overrides.get('default_log_overrides', {})
        dictConfig.update(default_overrides)
        dictConfig.update(overrides.get(name, {}))
    logging.config.dictConfig(dictConfig)

def reopenLogginFiles():
    global _registered_file_handles
    save_handles = _registered_file_handles
    _registered_file_handles = dict()
    for logName, (logger, handler) in save_handles.iteritems():
        handler.close()
        logger.removeHandler(handler)
        _configureOutputToFile(logger, logName)

def reloadLoggingConfiguration():
    reopenLogginFiles()
    global _name
    if _name is not None:
        _configureLogLevels(_name)

def _handleLoggingConfigurationSignal(signal, stackFrame):
    reloadLoggingConfiguration()

def _getMultipleFuncsHandler(funcs):
    def _multipleFuncsHandler(signalNumber, stackFrame):
        for func in funcs:
            func(signalNumber, stackFrame)
    return _multipleFuncsHandler

def _configureLoggingSignalHandlers():
    currentHandler = signal.getsignal(config.UPDATE_LOGGING_CONFIGURATION_SIGNAL)
    if currentHandler in [signal.SIG_IGN, signal.SIG_DFL, None]:
        # No handler for SIGHUP defined yet
        newHandler = _handleLoggingConfigurationSignal
    else:
        # A different handler was defined, call both handler on SIGHUP
        newHandler = _getMultipleFuncsHandler([currentHandler, _handleLoggingConfigurationSignal])
    signal.signal(signal.SIGHUP, newHandler)
