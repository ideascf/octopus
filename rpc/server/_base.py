# coding=utf-8
from octopus.service.octp_server import OctpServer

class BaseServer(object):
    def __init__(self, oct_s):
        """

        :param oct_s:
        :type oct_s: OctpServer
        """

        self._oct_s = oct_s
