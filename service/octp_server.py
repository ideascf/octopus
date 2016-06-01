# coding=utf-8
import etcd
import time
import logging
import gevent

from octopus import err
from octopus import constant
from octopus.proto import service_proto
from octopus.util.stoppable import Stoppable

log = logging.getLogger(constant.LOGGER_NAME)


class OctpServer(Stoppable):
    def __init__(self, etcd_options, service_name, service_addr):
        """

        :param etcd_options: Options of etcd.
        :param service_name: Name of current service.
        :param service_addr: Address of current service.
        :type etcd_options: dict
        :type service_name: str
        :type service_addr: dict
        :return:
        """

        super(OctpServer, self).__init__()

        self.etcd_options = etcd_options
        self.service_name = service_name
        self.service_addr = service_addr

        self.ec = etcd.Client(**self.etcd_options)
        self._token = ''
        self._watcher_co = None
        self._heartbeat_co = None

    #### stoppable handler method ####
    def _start_handler(self):
        """
        Handle start event.
        """

        # STEP 1: publish first.
        self._publish()

        self._watcher_co = self._start_watcher()  # 启动etcd服务监听协程
        self._heartbeat_co = self._start_heartbeat()  # 启动心跳协程

        log.info('OctpServer(%s) started.', self.service_name)

    def _stop_handler(self):
        """
        Handle stop event.
        """

        gevent.joinall([self._watcher_co, self._heartbeat_co])

        service_proto.unregister(self.ec, self._token)

        log.info('OctpServer(%s) stopped.', self.service_name)

    def _restart_handler(self):
        pass

    #### action method ####
    def _publish(self):
        """
        Start coroutine for publish.
        :return:
        """

        for retry in range(constant.ETCD_RECONNECT_MAX_RETRY_INIT):
            try:
                co = gevent.spawn(self._publish_handler)
                co.join(constant.ETCD_CONNECT_TIMEOUT)

                e = co.exception
                if e:  # if _publish_handler raise some exception, reraise it.
                    raise e
                else:
                    co.kill()
            except (etcd.EtcdConnectionFailed, gevent.Timeout):
                log.info('Connect to etcd failed, Retry(%d)...', retry)
                gevent.sleep(constant.ETCD_RECONNECT_INTERVAL)
            else:
                log.info('Publish OK.')
                break
        else:  # publish failed
            raise err.OctpEtcdConnectError('Max attempts exceeded.')

    def _start_watcher(self):
        """
        Start watcher coroutine for watch status of etcd.
        :return:
        :rtype: gevent.Greenlet
        """

        co = gevent.spawn(self._watcher_handler)
        log.info('watcher_handler(%s) started.', co)

        return co

    def _start_heartbeat(self):
        """
        Start heartbeat coroutine for watch status of etcd.
        :return:
        :rtype: gevent.Greenlet
        """

        co = gevent.spawn(self._heartbeat_handler)
        log.info('heartbeat_handler(%s) started.', co)

        return co

    #### coroutine handler ####
    def _publish_handler(self):
        """
        Handler for publish service into etcd.
        :return:
        """

        try:
            self._token = service_proto.register(self.ec, self.service_name, self.service_addr)
        except etcd.EtcdConnectionFailed:
            log.warn('connect to etcd failed.')
            # TODO complete it.
            raise
        else:
            log.info('publish service(%s: %s) to etcd SUCCESS.', self.service_name, self.service_addr)

    def _watcher_handler(self):
        """
        Handler for watch etcd's health.
        """

        while not self._stop:
            try:
                self.ec.watch(constant.ROOT_NODE, timeout=constant.WATCH_TIMEOUT)
            except etcd.EtcdWatchTimedOut:
                continue
            except etcd.EtcdConnectionFailed:
                # TODO 处理etcd服务器断开的情况
                log.warn('etcd can NOT connect, maybe crash')
                gevent.sleep(constant.ETCD_RECONNECT_INTERVAL)
            except Exception as e:
                log.warn('unexpected Error: %s', e)
                raise

    def _heartbeat_handler(self):
        """
        Handler for keep alive.
        """

        while not self._stop:
            log.debug('refresh ttl for service(%s)', self.service_name)
            service_proto.alive(self.ec, self.service_name, self._token)
            time.sleep(constant.SERVICE_REFRESH_INTERVAL)
