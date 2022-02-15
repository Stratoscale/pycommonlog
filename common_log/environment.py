import os


def guessIfRunningAsAService():
    return os.getuid() == 0 and os.getppid() == 1
