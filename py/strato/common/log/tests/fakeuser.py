import tempfile
import shutil
import os
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

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


def readLogContents(logName):
    with open(os.path.join(_tempDir, '%s.stratolog' % logName)) as f:
        return f.read()


class FakeUser:
    def __init__(self, program_path):
        assert _tempDir is not None
        try:
            self._output = subprocess.check_output(
                ['python2.7', program_path], stderr=subprocess.STDOUT, close_fds=True,
                env=dict(os.environ, PYTHONPATH='./py', STRATO_CONFIG_LOGGING="LOGS_DIRECTORY='%s'" % _tempDir)) \
                    .decode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise

    def output(self):
        return self._output
