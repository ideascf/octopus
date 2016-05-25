# coding=utf-8
import etcd
import gevent
import logging
from gevent.hub import Waiter

from .service import Service
from proto import service_proto
import err
import constant
from util.stoppable import Stoppable

log = logging.getLogger(constant.LOGGER_NAME)


class OctpClient(Stoppable):

    def __init__(self, etcd_options, service_names):
        """

        :param etcd_options: etcd配置选项
        :param service_names: 需要监听的所有service的名称
        :type etcd_options: dict
        :type service_names: list, tuple
        :return:
        """

        super(OctpClient, self).__init__()

        self.service_names = service_names
        self.service_dict = {  # 所有service_name 对应的service list
            service_name: []
            for service_name in self.service_names
        }
        """:type: dict[str, list[Service]]"""

        self._diabled_service_list = []  # all disabled service
        """:type: list[Service]"""

        self._etcd_options = etcd_options
        self._ec = etcd.Client(**self._etcd_options)
        """:type: etcd.Client"""

        self._watcher_dict = {
            service_name: gevent.spawn(self._watcher_handler, service_name)
            for service_name in self.service_names
        }
        """:type: dict[str, Greenlet]"""
        self._waiter_dict = {
            service_name: set()
            for service_name in self.service_names
        }
        """:type: dict[str, set[Waiter]]"""
        self._watcher_starter_coroutine = None
        """:type: Greenlet"""


    def _start_handler(self):
        self._watcher_starter_coroutine = gevent.spawn(self._start_watcher)

        self._get_initialize_service()  # 获取当前的service列表
        log.info('OctpClient(%s) started.', self.service_names)

    def _stop_handler(self):
        gevent.joinall([self._watcher_starter_coroutine,])
        log.info('OctpClient(%s) stopped.', self.service_names)

    def _restart_handler(self):
        pass

    def _get_initialize_service(self):
        for service_name in self.service_names:
            try:
                result = service_proto.get(self._ec, service_name)
            except err.OctpServiceNotFoundError:
                log.warn('Now, NO node for service(%s).', service_name)
                continue

            if not result._children:
                log.warn('Now, NO any server for service(%s).', service_name)
            else:
                for service_node in result.leaves:
                    self._add_service(service_name, service_node)

    #### service ####
    def disable_service(self, service):
        """

        :param service:
        :type service: Service
        :return:
        """

        service_list = self._get_service_list(service.service_name)
        service_list.remove(service)
        self._diabled_service_list.append(service)

    def _get_service_list(self, service_name):
        """
        Get service_list for the service_name.
        :param service_name:
        :type service_name: str
        :return:
        :rtype: list
        """
        service_list = self.service_dict[service_name]

        return service_list

    #### waiter ####
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
            gevent.get_hub().loop.run_callback(lambda: waiter.switch(action))

    #### 监听service的改动 ####
    def _start_watcher(self):
        gevent.joinall(self._watcher_dict.values())

    def _watcher_handler(self, service_name):
        while not self._stop:
            try:
                result = service_proto.watch(self._ec, service_name, timeout=10)
                self._deal_watch_result(service_name, result)
            except etcd.EtcdWatchTimedOut:
                log.debug('service watch timeout.')
                continue

    def _deal_watch_result(self, service_name, result):
        """

        :param result: watch 返回的EtcdResult对象
        :type result: etcd.EtcdResult
        :return:
        """

        log.debug('service change: %s', result)
        action = constant.SERVICE_ACTION.NONE

        if result.action in ('create',):
            self._add_service(service_name, result)
            action = constant.SERVICE_ACTION.ADD
        elif result.action in ('delete', 'expire', 'compareAndDelete'):
            self._del_service(service_name, result)
            action = constant.SERVICE_ACTION.DEL
        elif result.action in ('set', 'compareAndSwap', 'update',):
            self._update_service(service_name, result)
            action = constant.SERVICE_ACTION.UPDATE
        else:
            raise err.OctpServiceInvalidState('Encounter invalid action: %s', result.action)

        self._notify_waiter(service_name, action)

        log.debug('Now, service_dict: %s', self.service_dict)

    def _add_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self._get_service_list(service_name)
        try:
            new_service = Service(service_name, result.key, result.value)
        except err.OctpServiceInfoError as e:
            # ignore invalid service_info
            log.warn(e)
            return

        service_list.append(new_service)
        log.info('Add service (%s : %s)', service_name, new_service)

    def _del_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self._get_service_list(service_name)

        for index, old_service in enumerate(service_list):
            if old_service.name == result.key:
                break
        else:
            log.debug('service(%s) NOT find. maybe delete already.')
            return

        del service_list[index]
        log.info('Del service (%s : %s)', service_name, old_service)

    def _update_service(self, service_name, result):
        """

        :param service_name:
        :param result:
        :type service_name: str
        :type result: etcd.EtcdResult
        :return:
        """

        service_list = self._get_service_list(service_name)

        for index, old_service in enumerate(service_list):
            if old_service.name == result.key:
                break
        else:
            self._add_service(service_name, result)
            return

        try:
            new_service = Service(service_name, result.key, result.value)
        except err.OctpServiceInfoError as e:
            # ignore invalid service_info
            log.warn(e)
            return
        else:
            service_list[index] = new_service
            log.info('Update service (%s : %s -> %s)', service_name, old_service, new_service)
