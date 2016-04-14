# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import logging
import sys

from server import octp_server
octp_server.log.setLevel('DEBUG')
octp_server.log.addHandler(logging.StreamHandler(sys.stdout))

def handler():
    while True:
        print 'hello'
        gevent.sleep(10)

oc = octp_server.OctpServer({}, 'test', {'host': 'localhost', 'port': 9999})
oc.run(handler, gevent.spawn)
