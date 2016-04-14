# coding=utf-8
import etcd
import gevent
import logging
from gevent.hub import Waiter

from . import service
from proto import service_proto
import err, constant

log = logging.getLogger(constant.LOGGER_NAME)

class OctpClient():
    def __init__(self, etcd_options, service_names):
        """

        :param etcd_options: etcd配置选项
        :param service_names: 需要监听的所有service的名称
        :type etcd_options: dict
        :type service_names: list, tuple
        :return:
        """

        self.service_names = service_names
        self.service_dict = {}  # 所有service_name 对应的service list
        """:type: dict[str, list[service.Service]]"""

        self._etcd_options = etcd_options
        self._ec = etcd.Client(**self._etcd_options)
        """:type: etcd.Client"""

        self._watcher_dict = {
            service_name: gevent.spawn(self._watcher_handler, service_name)
            for service_name in self.service_names
        }
        self._waiter_dict = {
            service_name: set()
            for service_name in self.service_names
        }
        """:type: dict[str, set[Waiter]]"""

    def init(self):
        for service_name in self.service_names:
            self.service_dict[service_name] = []

        gevent.spawn(self._start_watcher)  # 开启独立的协程用于监听service的变更

    def add_waiter(self, service_name, waiter):
        """
        向指定service_name下增加一个waiter， 以等待该service_name下有新的事件发生
        :param service_name:
        :param waiter: Waiter
        :type service_name: str
        :type waiter: Waiter
        :return:
        """

        self._waiter_dict[service_name].add(waiter)

    def del_waiter(self, service_name, waiter):
        """
        移除指定service_name下的一个waiter
        :param service_name:
        :param waiter:
        :type service_name: str
        :type waiter: Waiter
        :return:
        """

        self._waiter_dict[service_name].discard(waiter)

    def _notify_waiter(self, service_name, action):
        """
        通知指定service_name下的所有waiter
        :param service_name:
        :param action: 当前变更动作，定义与constatn.SERVICE_ACTION
        :type service_name: str
        :type action: str
        :return:
        """

        for waiter in self._waiter_dict[service_name]:
            waiter.switch(action)

    #### 监听service的改动 ####
    def _start_watcher(self):
        gevent.joinall(self._watcher_dict.values())

    def _watcher_handler(self, service_name):
        while True:
            # TODO 这里可能会丢失事件
            result = service_proto.watch(self._ec, service_name)
            self._deal_watch_result(service_name, result)

    def _deal_watch_result(self, service_name, result):
        """

        :param result: watch 返回的EtcdResult对象
        :type result: etct.EtcdResult
        :return:
        """

        action = constant.SERVICE_ACTION.NONE

        if result.action in ('create',):
            self._add_service(service_name, result)
            action = constant.SERVICE_ACTION.ADD
        elif result.action in ('delete', 'expire', 'compareAndDelete'):
            self._del_service(service_name, result)
            action = constant.SERVICE_ACTION.DEL
        elif result.action in ('set', 'compareAndSwap'):
            self._update_service(service_name, result)
            action = constant.SERVICE_ACTION.UPDATE
        else:
            raise err.OctpServiceInvalidState('Encounter invalid action: %s', result.action)

        self._notify_waiter(service_name, action)

    def _add_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self.service_dict[service_name]
        try:
            new_service = service.Service(result.value)
        except Exception as e:
            # TODO
            log.warn(e)
            return

        service_list.append(new_service)

    def _del_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self.service_dict[service_name]

        for index, old_service in service_list:
            if old_service.name == result.key:
                break
        else:
            log.debug('service(%s) NOT find. maybe delete already.')
            return

        del service_list[index]

    def _update_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self.service_dict[service_name]

        for index, old_service in service_list:
            if old_service.name == result.key:
                break
        else:
            self._add_service(service_name, result)
            return

        try:
            new_service = service.Service(result.value)
        except Exception as e:
            # TODO
            log.warn(e)
            return
        else:
            service_list[index] = new_service