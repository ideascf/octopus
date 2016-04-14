import logging
from . import constant

_log = logging.getLogger(constant.LOGGER_NAME)
_log.addHandler(logging.NullHandler())


import sys
_log.addHandler(logging.StreamHandler(sys.stdout))