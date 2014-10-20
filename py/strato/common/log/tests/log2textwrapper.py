import fakeuser
import subprocess
import os


def run(logName):
    filename = os.path.join(fakeuser.tempDir(), '%s.stratolog' % logName)
    output = subprocess.check_output(
        ['python', '-m', 'strato.common.log.log2text', filename], stderr=subprocess.STDOUT, close_fds=True)
    return output
