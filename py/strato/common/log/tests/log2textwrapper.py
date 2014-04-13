import fakeuser
import subprocess
import os


def run():
    filename = os.path.join(fakeuser.tempDir(), 'fakeuser.log')
    output = subprocess.check_output(
        ['python', '-m', 'strato.common.log.log2text', filename], stderr=subprocess.STDOUT, close_fds=True)
    return output
