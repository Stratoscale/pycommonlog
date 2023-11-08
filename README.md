# pycommonlog

# Build
```bash
skipper make -i all
```

# Demo

```python
from strato.common.log import configurelogging
configurelogging.configureLogging('test-strato-log', forceDirectory=".")
import logging  # noqa: E402
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
```