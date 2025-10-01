import strato.common.log.config
strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE = '/tmp/test_logging'
import json  # noqa: E402
firstConfig = {'default_log_overrides':
               {'handlers': {'console': {'level': 'WARNING'}, 'file': {'level': 'INFO'}}}}
with open(strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE, 'wt') as fd:
    json.dump(firstConfig, fd)
from strato.common.log import configurelogging  # noqa: E402
configurelogging.configureLogging('mainlog')
configurelogging.configureLogger('sub.logger')
import logging  # noqa: E402
logging.info('write this message')
logging.error('root error message')
logging.getLogger('sub.logger').info('sub message')
logging.getLogger('sub.logger').error('sub error message')
secondConfig = {'mainlog': {'loggers': {'sub.logger': {'level': 'WARNING', 'propagate': False}},
                            'handlers': {'console': {'level': 'INFO'}, 'file': {'level': 'INFO'}},
                            'root': {'level': 'INFO'}, 'incremental': True}}
with open(strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE, 'wt') as fd:
    json.dump(secondConfig, fd)

import os  # noqa: E402
os.kill(os.getpid(), strato.common.log.config.UPDATE_LOGGING_CONFIGURATION_SIGNAL)
logging.getLogger().info('message after config change')
logging.error('root error after config change')
logging.getLogger('sub.logger').info('sub after config change')
logging.getLogger('sub.logger').error('sub error after config change')
