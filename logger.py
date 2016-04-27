# coding=utf-8
import sys
import logging
from . import constant

log = logging.getLogger(constant.LOGGER_NAME)
log.addHandler(logging.NullHandler())
