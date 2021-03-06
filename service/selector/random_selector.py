# coding=utf-8
import random

from ._base import BaseSelector


class RandomSelector(BaseSelector):

    def _get_service(self):
        if len(self._service_list) != 0:
            return random.choice(self._service_list)
        else:
            return None
