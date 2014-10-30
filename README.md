Examples
====

Logging to a Rotating File
=====

```python
from ayu import Checker
from ayu.handlers import LogHandler

import logging
import logging.handlers

logger = logging.getLogger('cool-languages-logger')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler('health.log', maxBytes=200, backupCount=5)
logger.addHandler(handler)

c = Checker(('https://www.python.org/',
             'http://www.rust-lang.org/',
             'https://www.haskell.org/haskellwiki/Haskell'), 60, LogHandler(logger))

c.run(lambda checker: True)

```
