# coding=utf-8
import gevent
from gevent import monkey
monkey.patch_all()

import logging
import sys

from election.election import Election
from server.octp_server import OctpServer

from logger import log
log.setLevel('DEBUG')
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
