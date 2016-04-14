# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import sys
import logging

from client import octp_client
from client.selector import round_selector

octp_client.log.setLevel('DEBUG')
octp_client.log.addHandler(logging.StreamHandler(sys.stdout))

oc = octp_client.OctpClient({}, ['test', 'foo'])
sel = round_selector.RoundSelector(oc, 'test')

def main():
    while True:
        service = sel.get_service(5)
        if service:
            print service.addr

        gevent.sleep(1)


if __name__ == '__main__':
    g = gevent.spawn(main)
    g.join()