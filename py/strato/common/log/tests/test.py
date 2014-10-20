import unittest
import fakeuser
import log2textwrapper


class Test(unittest.TestCase):
    def setUp(self):
        fakeuser.setUp()

    def tearDown(self):
        fakeuser.tearDown()

    def test_useCaseIsSimpleInADaemon(self):
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


if __name__ == '__main__':
    unittest.main()
