#!/usr/bin/env python3
#
#
# test-4-sqlite-server-http-1.py
# Tester for sqlite-server-http-1.py (Very simple SQLite Server (HTTP))
# (c) Noprianto <nop@noprianto.com>
# 2016
# License: GPL
# https://github.com/nopri/code/
#
# Tested in Python 3.4 using only standard library
#

import base64
import json
import random
import time
import threading
import urllib.request


URL = 'http://localhost:8080/?q='
MIN_RANDOM = 1
MAX_RANDOM = 10000
MAX_ROWS = 200
MAX_THREADS = 100


def build_query(q, c=False):
    q = q.encode()
    q = base64.encodebytes(q).decode().strip()
    ret = URL + q
    if c:
        ret += '&c=1'
    return ret

def test_query():
    table_name = 'table_%s_%s' %(
        str(int(time.time())),
        str(random.randint(MIN_RANDOM, MAX_RANDOM))
        )
    #
    q = 'create table %s(a integer)' %(table_name)
    u = build_query(q, True)
    f = urllib.request.urlopen(u)
    #
    for i in range(MAX_ROWS):
        q = 'insert into %s(a) values(%s)' %(table_name, str(i))
        u = build_query(q, True)
        f = urllib.request.urlopen(u)
        msg = '[%s][Table: %s][%s]' %(
                threading.current_thread().name,
                table_name,
                i
            )
        print(msg)
    #
    q = 'select max(ROWID) from %s' %(table_name)
    u = build_query(q)
    f = urllib.request.urlopen(u)
    r = json.loads(f.read().decode())
    #
    msg = '[%s][Table: %s][response: %s]' %(
            threading.current_thread().name,
            table_name,
            r
        )
    print(msg)

def main():
    for i in range(MAX_THREADS):
        t = threading.Thread(target=test_query)
        t.start()    


if __name__ == '__main__':
    main()
