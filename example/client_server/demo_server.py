# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import socket
import logging
import sys
from gevent import server
import random

from server import octp_server

from logger import log
log.setLevel('DEBUG')
log.addHandler(logging.StreamHandler(sys.stdout))

server_info = {
    'addr': {'host': 'localhost', 'port': random.randint(9000, 10000)},
    'timeout': 1000,
}

def handle(client, addr):
    """

    :param client:
    :param addr:
    :type client: socket.SocketType
    :return:
    """

    print client
    print client.recv(1024)
    client.send('pong')

    client.close()

def main():
    os = octp_server.OctpServer({}, 'test', server_info)
    s = server.StreamServer(tuple(server_info['addr'].values()), handle)
    s.start()

    os.init()
    s.serve_forever()
    os.destroy()


if __name__ == '__main__':
    main()
