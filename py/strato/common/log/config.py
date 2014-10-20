import os

LOGS_DIRECTORY = os.environ.get('STRATO_LOGS_DIRECTORY', None)
if LOGS_DIRECTORY is None:
    LOGS_DIRECTORY = os.path.join(os.environ['HOME'], "tmp", "stratoscalelogs")
LOGS_SUFFIX = ".stratolog"
LOG_CONFIGURATION = os.environ.get('STRATO_LOGS_CONFIGURATION_FILE', None)

DEFAULT_LOG_CONFIGURATION = {
    "handlers":
    {
        "console":
        {
            "level": "DEBUG"
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

exec os.environ.get("STRATO_CONFIG_LOGGING", "")
