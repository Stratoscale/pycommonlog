import fakeuser
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess
import os


def run(logName):
    filename = os.path.join(fakeuser.tempDir(), '%s.stratolog' % logName)
    command = ['python2.7', '-m', 'strato.common.log.log2text', filename]
    output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                     env=dict(PYTHONPATH="./py"), close_fds=True)
    return output.decode()
