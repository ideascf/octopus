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


def human_time(time=None):
    """
    将秒级时间转换为微秒级
    :param float time: 妙级的时间
    :return int: 毫秒级时间
    """

    return int(time * 1000000)