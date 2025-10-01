from strato.common.log import configurelogging
configurelogging.configureLogging('mainlog')
configurelogging.configureLogger('sub.logger')

import logging  # noqa: E402
logging.info('write this message')
logging.getLogger('sub.logger').info('sub message')
