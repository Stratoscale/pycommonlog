import os
from strato.common.log import environment
import signal

LOGS_DIRECTORY = os.environ.get('STRATO_LOGS_DIRECTORY', None)
if LOGS_DIRECTORY is None:
    LOGS_DIRECTORY = os.path.join(os.environ['HOME'], "tmp", "stratoscalelogs")
LOGS_SUFFIX = ".stratolog"
LOG_CONFIGURATION = os.environ.get('STRATO_LOGS_CONFIGURATION_FILE', None)
LOGS_CONFIGURATION_OVERRIDE_FILE = '/etc/stratoscale/logs_override.json'
UPDATE_LOGGING_CONFIGURATION_SIGNAL = signal.SIGHUP

DEFAULT_CONSOLE_LEVEL = "ERROR" if environment.guessIfRunningAsAService() else "DEBUG"
DEFAULT_LOG_CONFIGURATION = {
    "handlers":
    {
        "console":
        {
            "level": DEFAULT_CONSOLE_LEVEL
        },
        "file":
        {
            "level": "DEBUG"
        }
    },
    "version": 1,
    "loggers":
    {
        "strato.common.subprocesswrappers":
        {
            "level": "INFO",
            "propogate": "no"
        }
    },
    "root":
    {
        "level": "DEBUG"
    },
    "incremental": True
}

COLORS = {
    'REGULAR': '\033[0m',
    'BLACK': '\033[0;30m',
    'RED': '\033[0;31m',
    'GREEN': '\033[0;32m',
    'BROWN': '\033[0;33m',
    'BLUE': '\033[0;34m',
    'PURPLE': '\033[0;35m',
    'CYAN': '\033[0;36m',
    'GRAY': '\033[0;37m',
    'DARK_GRAY': '\033[1;30m',
    'LIGHT_RED': '\033[1;31m',
    'LIGHT_GREEN': '\033[1;32m',
    'YELLOW': '\033[1;33m',
    'LIGHT_BLUE': '\033[1;34m',
    'LIGHT_PURPLE': '\033[1;35m',
    'LIGHT_CYAN': '\033[1;36m',
    'WHITE': '\033[1;37m',
}

exec os.environ.get("STRATO_CONFIG_LOGGING", "")
