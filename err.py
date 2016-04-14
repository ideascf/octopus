# coding=utf-8

class OctpError(Exception):
    """
    异常基类
    """
    pass


#### 服务相关 ####
class OctpServiceError(OctpError):
    """
    服务相关错误
    """
    pass


class OctpServiceNameError(OctpServiceError):
    """
    没有在etcd中找到对应的service的目录，如想在/service/service_xxx目录下注册一个节点，但是service_xxx目录不存在
    """
    pass


class OctpServiceNotFoundError(OctpServiceError):
    """
    在etcd中找到了对应service的目录，但是该目录下没有可用的服务节点
    """
    pass


class OctpServiceInvalidState(OctpServiceError):
    """
    非法的状态
    """
    pass


#### 统计相关 ####
class OctpStatError(OctpError):
    """
    统计模块相关的错误
    """
    pass


class OctpStatLoseError(OctpStatError):
    """
    和统计服务直接的连接丢失
    """
    pass


#### 编程相关的错误 ####
class OctpProgramError(OctpError):
    """
    编程相关的错误
    """
    pass


class OctpParamError(OctpProgramError):
    """
    传入参数错误
    """
    pass