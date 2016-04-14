# coding=utf-8
import etcd
import time
import logging

import err
import constant
from proto import service_proto

log = logging.getLogger(constant.LOGGER_NAME)

class OctpServer():
    def __init__(self, etcd_options, service_name, service_addr):
        self.etcd_options = etcd_options
        self.service_name = service_name
        self.service_addr = service_addr

        self.ec = etcd.Client(**self.etcd_options)
        self._token = ''

    def run(self, handler, parallel):
        """

        :param handler:
        :type handler:
        :return:
        """

        if not callable(handler):
            raise err.OctpParamError('handler must be callable.')

        self._int()

        parallel(self._start_watcher)  # 启动etcd服务监听器
        parallel(self._heartbeat)  # 启动心跳包
        handler()

        self._stop()

    def _int(self):
        self._token = service_proto.register(self.ec, self.service_name, self.service_addr)

    def _stop(self):
        service_proto.unregister(self.ec, self._token)
        pass


    def _start_watcher(self):
        """
        监听etcd服务器的状态，当连接丢失时，尝试重连。
        :return:
        """

        while True:
            try:
                self.ec.watch(constant.ROOT_NODE, timeout=constant.WATCH_TIMEOUT)
                # TODO 处理etcd服务器断开的情况
            except etcd.EtcdWatchTimedOut:
                continue

    def _heartbeat(self):
        while True:
            log.debug('refresh ttl for %s', self.service_name)
            service_proto.alive(self.ec, self.service_name, self._token)
            time.sleep(constant.SERVICE_REFRESH_INTERVAL)
