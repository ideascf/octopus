# coding=utf-8
import traceback
import etcd
import logging
import json

import err, constant
from util import tools

log = logging.getLogger(constant.LOGGER_NAME)

def register(ec, service_name, service_info):
    """

    :param ec: etcd的客户端对象
    :param service_name:
    :param service_info:
    :type ec: etcd.Client
    :type service_name: str
    :type service_info: dict
    :return:
    :rtype: str
    """


    add_info = service_info.get('addr')
    if not add_info\
            or not {'host', 'port'}.issubset(add_info.keys()):
        raise err.OctpParamError('service_addr must contain "host" and "port".')


    result = ec.write(
        tools.service_dir_name(service_name),
        json.dumps(service_info),
        append=True,
        ttl=constant.SERVICE_TTL
    )
    log.debug('new key: %s', result.key)

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


def get(ec, service_name):
    """

    :param ec:
    :param service_name:
    :type ec: etcd.Client
    :return:
    """

    try:
        result = ec.get(tools.service_dir_name(service_name))
    except etcd.EtcdKeyNotFound:
        raise err.OctpServiceNotFoundError('Can NOT find service(%s) from etcd', service_name)
    else:
        return result


def alive(ec, service_name, service_token):
    """

    :param ec:
    :param service_name:
    :param service_token:
    :type ec: etcd.Client
    :return:
    """

    # this way, not upload parameter 'refresh', so can't only refresh ttl.
    # return ec.write(
    #     service_token,
    #     None,
    #     ttl=constant.SERVICE_TTL,
    #     refresh=True,
    #     prevExist=True,  # refresh and prevExist, can refresh ttl only.
    # )

    return ec.api_execute(
        '/v2/keys/'+service_token,
        ec._MPUT,
        {
            'refresh': True,
            'prevExist': True,
            'ttl': constant.SERVICE_TTL,
        }
    )