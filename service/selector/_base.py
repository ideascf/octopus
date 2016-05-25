# coding=utf-8
import logging
import traceback
import gevent
from gevent.hub import Waiter
from gevent import Timeout
import time

from octopus.service.octp_client import OctpClient
from octopus.service.service import Service
from octopus import err
from octopus import constant

log = logging.getLogger(constant.LOGGER_NAME)


class _TimeOut(Exception):
    pass


class BaseSelector(object):

    def __init__(self, oc, service_name):
        """

        :param oc:
        :param service_name:
        :type oc: OctpClient
        :type service_name: str
        :return:
        """

        self.service_name = service_name

        self._oc = oc
        self._service_list = oc.service_dict[service_name]

    def get_service(self, timeout=None):
        """
        从集群中获取一个service的地址信息
        :param timeout: 最多等待timeout秒，如果为None则一直等待
        :type timeout: float
        :return: service的地址信息
        :rtype: None | Service
        """

        if len(self._service_list) == 0:
            self._wait(constant.SERVICE_ACTION.ADD, timeout)

        return self._get_service()

    def disable_service(self, service):
        """

        :param service:
        :type service: Service
        :return:
        """

        self._oc.disable_service(service)

    def _get_service(self):
        raise NotImplementedError

    def _wait(self, action=None, timeout=None):
        """
        等待本service_name下的service变更
        :param timeout:
        :type timeout: float
        :return:
        """

        remain = timeout

        waiter = Waiter()
        self._oc.add_waiter(self.service_name, waiter)
        try:
            while True:
                with Timeout(remain, _TimeOut):
                    start = time.time()
                    cur_action = waiter.get()
                    remain = remain - (time.time() - start)

                    if action is None:  # 没有特别指明需要的动作
                        break
                    elif action == cur_action:  # 捕获到需要的动作
                        break
                    elif remain < 0.001:  # 剩余超时时间不足1ms
                        raise _TimeOut
                    else:
                        continue
        except _TimeOut:  # 发生超时
            return False
        except Exception as e:
            raise err.OctpParamError('catch unexpect error: %s. more: %s', e, traceback.format_exc())
        else:
            return True
        finally:
            self._oc.del_waiter(self.service_name, waiter)
