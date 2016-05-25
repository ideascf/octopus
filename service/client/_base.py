# coding=utf-8
import logging
import threading
import time

from octopus import err
from octopus import constant
from octopus.service.selector._base import BaseSelector
from octopus.util import tools


log = logging.getLogger(constant.LOGGER_NAME)


class BaseClient(object):
    def __init__(self, thrift_mod, selector, **options):
        self._selector = selector
        """:type: BaseSelector"""
        self._thrift_mod = thrift_mod
        """:type: """

        self._raise_error = options.pop('raise_error', False)
        """:type: bool"""
        self._timeout = options.pop('timeout', None)
        """:type: bool"""

    def __del__(self):
        # TODO close all connection
        pass

    def __getattr__(self, name):
        def _(*args, **kwargs):
            return self.call(name, *args, **kwargs)

        return _

    def call(self, func_name, *args, **kwargs):
        ret = None

        while True:
            try:
                self._call(func_name, *args, **kwargs)
            except err.OctpServiceUnavailable:
                continue
            except err.OctpError as e:
                log.warn('Call func(%s) encounter ERROR: %s', e)

                raise e

        return ret

    def _deal_unavailable_service(self, service):
        raise NotImplementedError()

    def _call(self, func_name, *args, **kwargs):
        pass

    def _call_log(self, service, func_name, result, cost, in_param, out_param):
        """

        :param resullt:
        :param service:
        :type service: Service
        :return:
        """

        info  = {
            'server': service.service_name,
            'thread': threading.currentThread(),
            'caller': 'octopus.service.thrift_client',
            'type': 'RPC-CALL',  # caller
            'func': func_name,
            'result': result,
            'time': tools.human_time(time.time()),
            'cost': tools.human_time(cost),
            'in': in_param,
            'out': out_param,
            'tag': 'octopus,rpc-call,thrift',

            # addition fields
            'service_addr': service.addr,
        }

        info_list = ('{key}={value}'.format(key=key, value=value) for key, value in info.iteritems())
        out_str = '|'.join(info_list)

        log.info(out_str)

    def _service_timeout(self, service):
        """
        Get timeout which is the time call service.

        self._timeout FIRST, then service.timeout.
        :param service:
        :type service: Service
        :return:
        """

        if self._timeout is not None:
            return self._timeout
        else:
            return service.timeout

    def _get_service(self):
        """
        Get one service or else raise err.OctpServiceAllFault.
        :return:
        :rtype: service.Service
        :raise: err.OctpServiceAllFault
        """

        service = self._selector.get_service(0)  # Don't wait
        if service is None:
            raise err.OctpServiceAllFault('Not one service is available!')

        return service