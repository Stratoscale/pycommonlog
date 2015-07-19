import unittest
import fakeuser
import log2textwrapper


class Test(unittest.TestCase):
    def setUp(self):
        fakeuser.setUp()

    def tearDown(self):
        fakeuser.tearDown()

    def test_useCaseFromCommandLine(self):
        PROGRAM = "\n".join([
            """from strato.common.log import configurelogging""",
            """configurelogging.configureLogging('fakeuser')""",
            """import logging""",
            """logging.info("dict %%(here)s", dict(here='there'))""",
            """logging.info('write this message')""",
            ""])

        user = fakeuser.FakeUser(PROGRAM)
        self.assertTrue('write this message' in user.output())
        self.assertTrue('write this message' in fakeuser.readLogContents('fakeuser'))
        self.assertTrue('write this message' in log2textwrapper.run('fakeuser'))

    def test_useCaseWithSublogger(self):
        PROGRAM = "\n".join([
            """from strato.common.log import configurelogging""",
            """configurelogging.configureLogging('mainlog')""",
            """configurelogging.configureLogger('sub.logger')""",
            """import logging""",
            """logging.info('write this message')""",
            """logging.getLogger('sub.logger').info('sub message')""",
            ""])

        user = fakeuser.FakeUser(PROGRAM)
        self.assertTrue('write this message' in user.output())
        self.assertTrue('sub message' in user.output())

        self.assertTrue('write this message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('write this message' in log2textwrapper.run('mainlog'))
        self.assertTrue('sub message' not in fakeuser.readLogContents('mainlog'))
        self.assertTrue('sub message' not in log2textwrapper.run('mainlog'))

        self.assertTrue('sub message' in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('sub message' in log2textwrapper.run('mainlog__sub.logger'))
        self.assertTrue('write this message' not in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('write this message' not in log2textwrapper.run('mainlog__sub.logger'))

    def test_useCaseForDaemon(self):
        PROGRAM = "\n".join([
            """import strato.common.log.environment""",
            """strato.common.log.environment.guessIfRunningAsAService = lambda: True""",
            """from strato.common.log import configurelogging""",
            """configurelogging.configureLogging('mainlog')""",
            """configurelogging.configureLogger('sub.logger')""",
            """import logging""",
            """logging.info('write this message')""",
            """logging.error('root error message')""",
            """logging.getLogger('sub.logger').info('sub message')""",
            """logging.getLogger('sub.logger').error('sub error message')""",
            ""])

        user = fakeuser.FakeUser(PROGRAM)
        self.assertTrue('write this message' not in user.output())
        self.assertTrue('sub message' in user.output())
        self.assertTrue('root error message' in user.output())
        self.assertTrue('sub error message' in user.output())

        self.assertTrue('write this message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('write this message' in log2textwrapper.run('mainlog'))
        self.assertTrue('sub message' not in fakeuser.readLogContents('mainlog'))
        self.assertTrue('sub message' not in log2textwrapper.run('mainlog'))
        self.assertTrue('root error message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('root error message' in log2textwrapper.run('mainlog'))
        self.assertTrue('sub error message' not in fakeuser.readLogContents('mainlog'))
        self.assertTrue('sub error message' not in log2textwrapper.run('mainlog'))

        self.assertTrue('sub message' in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('sub message' in log2textwrapper.run('mainlog__sub.logger'))
        self.assertTrue('write this message' not in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('write this message' not in log2textwrapper.run('mainlog__sub.logger'))
        self.assertTrue('sub error message' in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('sub error message' in log2textwrapper.run('mainlog__sub.logger'))
        self.assertTrue('root error message' not in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('root error message' not in log2textwrapper.run('mainlog__sub.logger'))


    def test_useCaseForConfigurationChange(self):
        PROGRAM = "\n".join([
            """import strato.common.log.config""",
            """strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE = '/tmp/test_logging'""",
            """import json""",
            """firstConfig = {'default_log_overrides': {'handlers': {'console': {'level': 'WARNING'}, 'file': {'level': 'INFO'}}}}""",
            """with open(strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE, 'wt') as fd:""",
            """    json.dump(firstConfig, fd)""",
            """from strato.common.log import configurelogging""",
            """configurelogging.configureLogging('mainlog')""",
            # """configurelogging.configureLogger('sub.logger')""",
            """import logging""",
            """logging.info('write this message')""",
            """logging.error('root error message')""",
            # """logging.getLogger('sub.logger').info('sub message')""",
            # """logging.getLogger('sub.logger').error('sub error message')""",
            """secondConfig = {'mainlog': {'loggers': {'sub.logger': {'level': 'WARNING', 'propagate' : False}},"""\
            """'handlers': {'console': {'level': 'INFO'}, 'file': {'level': 'INFO'}}, 'root': {'level': 'INFO'}, 'incremental' : True}}""",
            """with open(strato.common.log.config.LOGS_CONFIGURATION_OVERRIDE_FILE, 'wt') as fd:""",
            """    json.dump(secondConfig, fd)""",
            """import os""",
            """import signal""",
            """os.kill(os.getpid(), strato.common.log.config.UPDATE_LOGGING_CONFIGURATION_SIGNAL)""",
            """logging.getLogger().info('message after config change')""",
            """logging.error('root error after config change')""",
            # """logging.getLogger('sub.logger').info('sub after config change')""",
            # """logging.getLogger('sub.logger').error('sub error after config change')""",
            ""])

        user = fakeuser.FakeUser(PROGRAM)
        self.assertTrue('write this message' not in user.output())
        self.assertTrue('write this message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('root error message' in user.output())
        self.assertTrue('root error message' in fakeuser.readLogContents('mainlog'))
        # self.assertTrue('sub message' in user.output())
        # self.assertTrue('sub message' in fakeuser.readLogContents('mainlog__sub.logger'))
        # self.assertTrue('sub error message' in user.output())
        # self.assertTrue('sub error message' in fakeuser.readLogContents('mainlog__sub.logger'))

        self.assertTrue('message after config change' in user.output())
        self.assertTrue('message after config change' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('root error after config change' in user.output())
        self.assertTrue('root error after config change' in fakeuser.readLogContents('mainlog'))
        # self.assertTrue('sub after config change' not in user.output())
        # self.assertTrue('sub after config change' not in fakeuser.readLogContents('mainlog__sub.logger'))
        # self.assertTrue('sub error after config change' in user.output())
        # self.assertTrue('sub error after config change' in fakeuser.readLogContents('mainlog__sub.logger'))

if __name__ == '__main__':
    unittest.main()
