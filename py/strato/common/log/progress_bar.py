from progressbar import ProgressBar, BouncingBar, Timer, Counter, Percentage, Bar
from contextlib import contextmanager

DEFAULT_WIDTH = 145
DEFAULT_MAXVAL = 999


@contextmanager
def progressbar_context(message, maxval=None, leave=False):
    widgets = [message]
    widgets.extend([" [ ", Percentage(), " ] "] if maxval else [Counter(format=" [#%3d] ")])
    widgets.extend([Timer(format=" <time: %s> "), Bar() if maxval else BouncingBar()])
    pbar = ProgressBar(widgets=widgets,
                       term_width=DEFAULT_WIDTH,
                       maxval=maxval if maxval else DEFAULT_MAXVAL).start()
    yield pbar
    if leave:
        pbar.finish()
