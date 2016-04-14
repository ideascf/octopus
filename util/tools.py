# coding=utf-8
import constant

def service_dir_name(service_name):
    """
    返回该service在etcd中的目录节点名称
    :param service_name:
    :type service_name: str
    :return:
    :rtype: str
    """

    return constant.SERVICE_NODE + service_name
