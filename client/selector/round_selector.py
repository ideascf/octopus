# coding=utf-8
import logging

from ._base import BaseSelector
import constant

log = logging.getLogger(constant.LOGGER_NAME)

class RoundSelector(BaseSelector):
    def __init__(self, oc, service_name):
        super(RoundSelector, self).__init__(oc, service_name)

        self._cur_index = 0

    def _get_service(self):
        """

        :return:
        :rtype: None | Service
        """

        if len(self._service_lsit) != 0:
            self._cur_index = (self._cur_index + 1) % len(self._service_lsit)

            return self._service_lsit[self._cur_index]
        else:
            return None
