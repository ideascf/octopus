# coding=utf-8
import logging
import etcd
import gevent

import err
import constant
from octopus.server.octp_server import OctpServer
from proto import service_proto

log = logging.getLogger(constant.LOGGER_NAME)


class Election(object):

    def __init__(self, os):
        """
        init from ec or os.
        :param os: octopus server
        :type os: OctpServer
        :return:
        """

        self._os = os

        self._ec = os.ec
        self._service_name = os.service_name
        self._locker = service_proto.locker(self._ec, self._service_name)

    def election(self, handle):
        """

        :param handle: Election completed, will call this.
        :type handle: callable
        :return:
        """

        if not callable(handle):
            raise err.OctpProgramError('Parameter `handler` must be callable.')

        while True:
            self._election()  # do election

            if self._locker.is_acquired:
                log.debug('Got locker')
                gevent.spawn(self._heartbeat_handler)
                handle()  # call callback

                break  # everything finished
            else:
                log.debug('Get locker failed, start watcher.')
                g = gevent.spawn(self._watcher_handler)  # watch locker, election again when current locker is expired.
                g.join()  # wait master lose locker, then retry election

    def _election(self):
        for retry in range(constant.Election.MAX_RETRY):
            try:
                self._locker.acquire(
                    blocking=False,
                    lock_ttl=constant.Election.LOCKER_TTL,
                    timeout=constant.Election.TIMEOUT
                )
            except etcd.EtcdLockExpired as e:
                log.warn(e)
            except Exception as e:
                log.warn(e)
            else:
                # May got locker
                break

            gevent.sleep(constant.Election.LOCK_INTERVAL)

    def _watcher_handler(self):
        """
        wait locker change
        :return:
        """

        while True:
            try:
                service_proto.watch_locker(self._ec, self._locker.path, constant.WATCH_TIMEOUT)
            except etcd.EtcdWatchTimedOut:
                continue
            else:
                log.info('Locker(%s) may changed, election again.', self._service_name)
                break  # stop current greenlet

    def _heartbeat_handler(self):
        while True:
            # refresh locker's ttl
            self._locker.acquire(True, lock_ttl=constant.Election.LOCKER_TTL)
            gevent.sleep(constant.Election.LOCK_INTERVAL)
