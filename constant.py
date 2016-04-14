# coding=utf-8

# octopus在etcd中的根节点
ROOT_NODE = '/octopus'
# service信息在etcd的节点
SERVICE_NODE = ROOT_NODE + '/service'
# config信息在etcd的节点
CONFIG_NODE = ROOT_NODE + '/config'


# logger_name
LOGGER_NAME = 'octopus'

class SERVICE_ACTION:
    """
    service 变更操作
    """

    ADD = 'add'
    DEL = 'del'
    UPDATE = 'update'
    NONE = 'none'