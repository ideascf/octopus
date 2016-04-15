# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import logging

from server.election import Election
from server.octp_server import OctpServer
from server.election import log

log.setLevel('DEBUG')
import sys
log.addHandler(logging.StreamHandler(sys.stdout))

def handler():
    print "i'm master."
    gevent.sleep(20)
    print "i'm dead"

def main():
    os = OctpServer({}, 'locker_demo', None)
    el = Election(os)

    el.election(handler)

if __name__ == '__main__':
    main()
