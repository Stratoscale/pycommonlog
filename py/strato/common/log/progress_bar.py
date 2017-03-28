from progressbar import ProgressBar, BouncingBar, Timer, Counter, Percentage, Bar
from contextlib import contextmanager
import logging
import os

DEFAULT_WIDTH = 145
DEFAULT_MAXVAL = 999


@contextmanager
def _progressbar_context(message, maxval=None, leave=False):
    widgets = [message]
    widgets.extend([" [ ", Percentage(), " ] "] if maxval else [Counter(format=" [#%3d] ")])
    widgets.extend([Timer(format=" <time: %s> "), Bar() if maxval else BouncingBar()])
    pbar = ProgressBar(widgets=widgets,
                       term_width=DEFAULT_WIDTH,
                       maxval=maxval if maxval else DEFAULT_MAXVAL).start()
    yield pbar
    if leave:
        pbar.finish()


@contextmanager
def _logging_context(message, maxval=None, leave=False):
    class DummyPbar(dict):
        def update(*args, **kwargs):
            pass
    logging.info("started " + message)
    yield DummyPbar()
    logging.info("finished " + message)


progressbar_context = _logging_context if 'jenkins' in os.environ.get('PWD', '').lower() else _progressbar_context
