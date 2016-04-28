# coding=utf-8
import json
import logging
import datetime

import constant
import err

log = logging.getLogger(constant.LOGGER_NAME)

_SERVICE_STR_FORMATTER = '{name}: {addr}'


class Service(object):

    def __init__(self, service_name, name, service_info):
        """

        :param service_name:
        :param name:
        :param service_info:
        :type service_name: str
        :type name: str
        :type service_info: str
        :return:
        """

        self.addr = None  # 该服务地址，形如 {"addr": "1.2.3.4", "port": 8888}
        """:type: dict"""
        self.timeout = None  # 连接该服务的超时时间，单位：秒。 如 0.3
        """:type: float"""
        self.service_name = service_name  # 该服务的名称。 如 cache
        """:type: str"""
        self.name = name  # 本服务在etcd中的key， 有etcd随机分配

        self._add_time = None
        """:type: datetime.datetime"""
        self._update_time = None
        """:type: datetime.datetime"""

        self._result = None
        """:type: etcd.EtcdResult"""

        self._parse_service_info(service_info)
        self._add_time = datetime.datetime.now()

    def update(self, service_info):
        """

        :param service_info:
        :type service_info: str
        :return:
        """

        self._parse_service_info(service_info)
        self._update_time = datetime.datetime.now()

    def _parse_service_info(self, service_info):
        """

        :param service_info:
        :type service_info: str
        :return:
        """

        try:
            info = json.loads(service_info)
            log.debug('service_info: %s', info)

            self.addr = info['addr']
            self.timeout = info.get('timeout')
        except Exception as e:
            log.warn('parse service_info error: %s', e)

            raise err.OctpServiceInfoError('Got invalid service_info(%s) from etcd. Should be ignore.', service_info)

    def __str__(self):
        return _SERVICE_STR_FORMATTER.format(name=self.name, addr=self.addr)
