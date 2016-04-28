# coding=utf-8
from abc import ABCMeta


class Stoppable(object):
    def __init__(self):
        self._stop = False

    def start(self):
        self._stop = False
        self._start_handler()

    def stop(self):
        self._stop = True
        self._stop_handler()

    def restart(self):
        self.stop()
        self.start()
        self._restart_handler()

    def _start_handler(self):
        raise NotImplementedError('Must implement _start_handler!')

    def _stop_handler(self):
        raise NotImplementedError('Must implement _stop_handler!')

    def _restart_handler(self):
        raise NotImplementedError('Must implement _restart_handler!')
