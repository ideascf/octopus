# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import sys
import logging
import socket

from service import octp_client
from service.selector import round_selector, random_selector

from logger import log
log.setLevel('DEBUG')
log.addHandler(logging.StreamHandler(sys.stdout))


def main():
    while True:
        service = sel.get_service(5)
        print service

        if service:
            sock = socket.socket()
            try:
                sock.connect(tuple(service.addr.values()))
                sock.send('ping')
                print sock.recv(1024)
            except Exception as e:
                print e
                pass

        gevent.sleep(1)


if __name__ == '__main__':
    oc = octp_client.OctpClient({}, ['test', 'foo'])
    sel = round_selector.RoundSelector(oc, 'test')
    # sel = random_selector.RandomSelector(oc, 'test')

    oc.start()
    g = gevent.spawn(main)
    g.join()
    oc.stop()
