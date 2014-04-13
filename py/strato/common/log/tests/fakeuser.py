import subprocess
import tempfile
import shutil
import os

_tempDir = None


def setUp():
    global _tempDir
    assert _tempDir is None
    _tempDir = tempfile.mkdtemp()


def tearDown():
    global _tempDir
    shutil.rmtree(_tempDir, ignore_errors=True)
    assert _tempDir is not None
    _tempDir = None


def tempDir():
    global _tempDir
    assert _tempDir is not None
    return _tempDir


_PROGRAM = """
from strato.common.log import configurelogging
configurelogging.configureLogging('fakeuser')
import logging
logging.info("dict %%(here)s", dict(here='there'))
logging.info('%(message)s')
"""


class FakeUser:
    def __init__(self, message):
        assert _tempDir is not None
        program = _PROGRAM % dict(message=message)
        try:
            self._output = subprocess.check_output(
                ['python', '-c', program], stderr=subprocess.STDOUT, close_fds=True,
                env=dict(os.environ, STRATO_CONFIG_LOGGING="LOGS_DIRECTORY='%s'" % _tempDir))
        except subprocess.CalledProcessError as e:
            print e.output
            raise

    def output(self):
        return self._output

    def readLogContents(self):
        return open(os.path.join(_tempDir, 'fakeuser.log')).read()
