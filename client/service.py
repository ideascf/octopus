# coding=utf-8
import datetime
import etcd

class Service(object):
    def __init__(self, service_info):
        self.addr = None  # 该服务地址，形如 {"addr": "1.2.3.4", "port": 8888}
        """:type: dict"""
        self.timeout = None  # 连接该服务的超时时间，单位：秒。 如 0.3
        """:type: float"""
        self.service_name = ''  # 该服务的名称。 如 cache
        """:type: str"""
        self.name = ''  # 该服务在etcd中的名称， 有etcd随机分配

        self._add_time = None
        """:type: datetime.datetime"""

        self._result = None
        """:type: etcd.EtcdResult"""