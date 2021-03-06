# coding=utf-8
import functools
import logging
import threading
import time
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

from octopus import err
from octopus import constant
from ._base import BaseClient
from octopus.service.selector._base import BaseSelector
from octopus.service.service import Service
from octopus.util import tools


log = logging.getLogger(constant.LOGGER_NAME)


class ThriftClient(BaseClient):
    def __init__(self, thrift_mod, selector, **options):
        """

        :param thrift_mod:
        :param selector:
        :param options:
        :type selector: BaseSelector
        :return:
        """

        super(ThriftClient, self).__init__(thrift_mod, selector)

        self._framed = options.pop('framed', None)
        if len(options) != 0:
            raise err.OctpProgramError('Unknown options: %s', options.items())

    def _call(self, func_name, *args, **kwargs):
        service = self._get_service()
        client = self._connect(service)

        start_time = time.time()
        try:
            func = getattr(client, func_name)
            ret = func(*args, **kwargs)
        except AttributeError as e:
            log.warn('error: %s', e)

            raise err.OctpProgramError("Don't have method: %s", func_name)
        except TTransport.TTransportException as e:  # maybe connection error, should try next
            log.info('Service(%s) may unavailable! error: %s', service, e)

            cost = time.time() - start_time
            self._call_log(service, func_name, False, cost, (args, kwargs), e)

            self._deal_unavailable_service(service)

            raise err.OctpServiceUnavailable('Service(%s) may unavailable!' % service)
        else:  # call success
            cost = time.time() - start_time
            self._call_log(service, func_name, True, cost, (args, kwargs), ret)

        return ret

    def _deal_unavailable_service(self, service):
        """

        :param service:
        :type service: Service
        :return:
        """

        self._selector.disable_service(service)

    def _connect(self, service):
        """

        :param service:
        :type service: Service
        :return:
        """

        client = self._gen_client(service)

        return client

    def _gen_client(self, service):
        """

        :param service:
        :type service: Service
        :return:
        """

        try:
            sock = TSocket.TSocket(service.addr['host'], service.addr['port'])
            sock.setTimeout(self._service_timeout(service))
            if self._framed:
                transport = TTransport.TFramedTransport(sock)
            else:
                transport = TTransport.TBufferedTransport(sock)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = self._thrift_mod.Client(protocol)

            try:
                # open this connection
                transport.open()
            except:
                pass
        except Exception as e:
            raise

        return client