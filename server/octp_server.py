# coding=utf-8
import etcd

import err
import constant
from proto import service_proto


class OctpServer():
    def __init__(self, etcd_addr, service_name, service_addr, etcd_options=None):
        self.etcd_addr = etcd_addr
        self.etcd_options = etcd_options if etcd_options else {}
        self.service_name = service_name
        self.service_addr = service_addr

        self.ec = etcd.Client(
            self.etcd_addr['addr'],
            self.etcd_addr['port'],
            **self.etcd_options,
        )
        self._token = ''

    def run(self, handler, parallel):
        """

        :param handler:
        :type handler:
        :return:
        """

        if callable(handler):
            raise err.OctpParamError('handler must be callable.')

        self._int()

        parallel(self._start_wather)  # 启动etcd服务监听器
        handler()

        self._stop()

    def _int(self):
        self._token = service_proto.register(self.ec, self.service_name, self.service_addr)

    def _stop(self):
        service_proto.unregister(self.ec, self._token)
        pass


    def _start_wather(self):
        """
        监听etcd服务器的状态，当连接丢失时，尝试重连。
        :return:
        """

        self.ec.watch(constant.ROOT_NODE)

        # TODO 处理etcd服务器断开的情况