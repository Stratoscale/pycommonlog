import strato.common.log.environment
strato.common.log.environment.guessIfRunningAsAService = lambda: True
from strato.common.log import configurelogging  # noqa: E402
configurelogging.configureLogging('mainlog')
configurelogging.configureLogger('sub.logger')
import logging  # noqa: E402
logging.info('write this message')
logging.error('root error message')
logging.getLogger('sub.logger').info('sub message')
logging.getLogger('sub.logger').error('sub error message')
