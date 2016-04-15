# coding=utf-8
import os

import constant


def service_dir_name(service_name):
    """
    返回该service在etcd中的目录节点名称
    :param service_name:
    :type service_name: str
    :return:
    :rtype: str
    """

    return os.path.join(constant.SERVICE_NODE, service_name)


def locker_name(service_name):
    """

    :param service_name:
    :return:
    :rtype: str
    """

    # Don't start with '/'
    name = os.path.join(constant.LOCKER_NODE, service_name)
    if name.startswith('/'):
        return name[1:]
    else:
        return name
