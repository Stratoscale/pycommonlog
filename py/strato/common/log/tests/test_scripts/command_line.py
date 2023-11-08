from strato.common.log import configurelogging
configurelogging.configureLogging('fakeuser')
import logging  # noqa: E402
logging.info("dict %%(here)s", dict(here='there'))
logging.info('write this message')
