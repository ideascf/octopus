# coding=utf-8
import etcd
import logging

from octopus import constant
from octopus import err
from octopus.util import tools


log = logging.getLogger(constant.LOGGER_NAME)

def watch(ec, service_name, timeout=None):
    """
    用来监听服务的配置改变
    :param ec:
    :param service_name:
    :param timeout:
    :type ec: etcd.Client
    :type service_name: str
    :type timeout: float
    :return:
    """

    return ec.watch(tools.config_name(service_name), timeout=timeout)


def get(ec, service_name):
    """

    :param ec:
    :param service_name:
    :type ec: etcd.Client
    :return:
    """

    try:
        result = ec.get(tools.config_name(service_name))
    except etcd.EtcdKeyNotFound:
        raise err.OctpConfigNotFoundError("Can't find config(%s) from etcd", service_name)
    else:
        return result