import unittest
import fakeuser
import log2textwrapper
from strato.common.log import configurelogging
configurelogging.configureLogging('test-strato-log', forceDirectory=".")
import logging  # noqa: E402


class Test(unittest.TestCase):
    def setUp(self):
        fakeuser.setUp()

    def tearDown(self):
        fakeuser.tearDown()

    def test_import(self):
        import strato.common.log.log2text

    def test_useCaseFromCommandLine(self):
        PROGRAM_PATH = 'py/strato/common/log/tests/test_scripts/command_line.py'
        user = fakeuser.FakeUser(PROGRAM_PATH)
        self.assertTrue('write this message' in user.output())
        self.assertTrue('write this message' in fakeuser.readLogContents('fakeuser'))
        self.assertTrue('write this message' in log2textwrapper.run('fakeuser'))

    def test_useCaseWithSublogger(self):
        PROGRAM_PATH = 'py/strato/common/log/tests/test_scripts/sublogger.py'
        user = fakeuser.FakeUser(PROGRAM_PATH)
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
        PROGRAM_PATH = 'py/strato/common/log/tests/test_scripts/daemon.py'
        user = fakeuser.FakeUser(PROGRAM_PATH)
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
        PROGRAM_PATH = 'py/strato/common/log/tests/test_scripts/config_change.py'
        user = fakeuser.FakeUser(PROGRAM_PATH)
        self.assertTrue('write this message' not in user.output())
        self.assertTrue('write this message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('root error message' in user.output())
        self.assertTrue('root error message' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('sub message' in user.output())
        self.assertTrue('sub message' in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('sub error message' in user.output())
        self.assertTrue('sub error message' in fakeuser.readLogContents('mainlog__sub.logger'))

        self.assertTrue('message after config change' in user.output())
        self.assertTrue('message after config change' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('root error after config change' in user.output())
        self.assertTrue('root error after config change' in fakeuser.readLogContents('mainlog'))
        self.assertTrue('sub after config change' not in user.output())
        self.assertTrue('sub after config change' not in fakeuser.readLogContents('mainlog__sub.logger'))
        self.assertTrue('sub error after config change' in user.output())
        self.assertTrue('sub error after config change' in fakeuser.readLogContents('mainlog__sub.logger'))


def main():
    logging.warning('Running test')
    logging.error('Running test')
    logging.progress('Running test')
    logging.step('Running test')
    logging.critical('Running test')
    logging.success('Running test')
    logging.debug('Running test')
    try:
        raise Exception('Test exception')
    except Exception:
        logging.exception('Running test')
    unittest.main()


logging.info('Imported test')

if __name__ == '__main__':
    main()
