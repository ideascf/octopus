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

# 刷新service节点的间隔时间
SERVICE_REFRESH_INTERVAL = 20
# service节点的过期时间
SERVICE_TTL = 30
# watch操作的超时时间
WATCH_TIMEOUT=10

# server端，尝试重连etcd的的间隔时间
ETCD_RECONNECT_INTERVAL = 3
# 初始化时，尝试连接etcd的次数
ETCD_RECONNECT_MAX_RETRY_INIT = 5
# 尝试连接的等待时间
ETCD_CONNECT_TIMEOUT = 3