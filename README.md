# octopus
## 简介
octopus是一个Python的分布式协调框架. 提供一些分布式环境中常见的需求的统一解决方案.
致力于为Python提供一个分布式开发工具套件.

## 目录结构
### 核心
- config
- election
- service

### 内部使用
- proto
    对注册中心进行API封装,提供统一的协议实现
- util
    内部使用的一些工具函数或类等

### 便利
- rpc

### 其他
- doc
    - API接口
    - 设计要点
    - 注意事项
    - more
- example
    示例代码. 简单的octopus使用样例.

## 主要功能
- 配置共享
- 服务发现
- 集群选主
    协助用户在分布式环境下,进行选主操作.