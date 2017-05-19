#!/usr/bin/env python3
#
#
# test-3-sqlite-server-http-1.py
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
import threading
import urllib.request


URL = 'http://localhost:8080/?q='
MAX_THREADS = 2000


def build_query(q, c=False):
    q = q.encode()
    q = base64.encodebytes(q).decode().strip()
    ret = URL + q
    if c:
        ret += '&c=1'
    return ret

def test_query():
    q = 'select undefined_function_test()'
    u = build_query(q)
    f = urllib.request.urlopen(u)
    r = json.loads(f.read().decode())
    #
    msg = '[%s][response: %s]' %(
            threading.current_thread().name,
            r
        )
    print(msg)
    #
    q = 'create tables error'
    u = build_query(q)
    f = urllib.request.urlopen(u)
    r = json.loads(f.read().decode())
    #
    msg = '[%s][response: %s]' %(
            threading.current_thread().name,
            r
        )
    print(msg)

def main():
    for i in range(MAX_THREADS):
        t = threading.Thread(target=test_query)
        t.start()    


if __name__ == '__main__':
    main()
