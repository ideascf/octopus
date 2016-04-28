# coding=utf-8
import json
import logging

import constant

log = logging.getLogger(constant.LOGGER_NAME)

_SERVICE_STR_FORMATTER = '{name}: {addr}'


class Service(object):

    def __init__(self, name, service_info):
        self.addr = None  # 该服务地址，形如 {"addr": "1.2.3.4", "port": 8888}
        """:type: dict"""
        self.timeout = None  # 连接该服务的超时时间，单位：秒。 如 0.3
        """:type: float"""
        self.service_name = ''  # 该服务的名称。 如 cache
        """:type: str"""
        self.name = name  # 本服务在etcd中的key， 有etcd随机分配

        self._add_time = None
        """:type: datetime.datetime"""

        self._result = None
        """:type: etcd.EtcdResult"""

        self._parse(service_info)

    def _parse(self, service_info):
        try:
            info = json.loads(service_info)
            log.debug('service_info: %s', info)
            """:type: dict"""

            self.addr = info['addr']
            self.timeout = info.get('timeout')
        except Exception as e:
            log.warn('parse service_info error: %s', e)

    def __str__(self):
        return _SERVICE_STR_FORMATTER.format(name=self.name, addr=self.addr)
