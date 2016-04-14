# coding=utf-8
import random

from ._base import BaseSelector
import constant

class RandomSelector(BaseSelector):
    def _get_service(self):
        return random.choice(self._service_lsit)