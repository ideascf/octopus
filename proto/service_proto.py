# coding=utf-8
import traceback
import etcd
import logging

import err, constant
from util import tools

log = logging.getLogger(constant.LOGGER_NAME)

def register(ec, service_name, service_addr):
    """

    :param ec: etcd的客户端对象
    :param service_name:
    :param service_addr:
    :type ec: etcd.Client
    :type service_name: str
    :type service_addr: dict
    :return:
    :rtype: str
    """

    if not all(key in service_addr.iterkeys() for key in ['host', 'port']):
        raise err.OctpParamError('service_addr must contain "host" and "port".')

    result = ec.write(tools.service_dir_name(service_name), service_addr, append=True)

    return result.key


def unregister(ec, service_token):
    """

    :param ec:
    :param service_token:
    :type ec: etcd.Client
    :type service_token: str
    :return: 是否成功
    :rtype: bool
    """

    try:
        ec.delete(service_token)
    except Exception:
        # TODO 完善对异常的处理
        log.warn('Unregister service failed. err: %s', traceback.format_exc())
        return False
    else:
        return True


def watch(ec, service_name, timeout=None):
    """
    用来监听一个服务集群的改动
    :param ec:
    :param service_name:
    :param timeout:
    :type ec: etcd.Client
    :type
    :return:
    """

    return ec.watch(tools.service_dir_name(service_name), timeout=timeout, recursive=True)