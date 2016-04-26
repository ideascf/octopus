# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import sys
import logging
import socket

from client import octp_client
from client.selector import round_selector, random_selector

from logger import log
log.setLevel('DEBUG')
log.addHandler(logging.StreamHandler(sys.stdout))

oc = octp_client.OctpClient({}, ['test', 'foo'])
# sel = round_selector.RoundSelector(oc, 'test')
sel = random_selector.RandomSelector(oc, 'test')


def main():
    while True:
        service = sel.get_service(5)
        print service

        if service:
            sock = socket.socket()
            sock.connect(tuple(service.addr.values()))
            sock.send('ping')
            print sock.recv(1024)

        gevent.sleep(1)


if __name__ == '__main__':
    g = gevent.spawn(main)
    g.join()
