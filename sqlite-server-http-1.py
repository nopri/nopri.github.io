#!/usr/bin/env python3
#
#
# sqlite-server-http-1.py
# Very simple SQLite Server (HTTP)
# (c) Noprianto <nop@noprianto.com>
# 2016
# License: GPL
# https://github.com/nopri/code/
#
# Based on some codes from https://github.com/nopri/sqliteboy
#
# Tested in Python 3.4 using only standard library
#

APP_NAME = 'sqlite-server-http-1'
APP_VERSION = 'version 0.1'
APP_TITLE = APP_NAME + ' ' + APP_VERSION
DEFAULT_PORT = 8080
DEFAULT_HOST = ''
CONTENT_HEADER = 'Content-type'
CONTENT_MIME = 'application/json'
QUERY_QUERY = 'q'
QUERY_COMMIT = 'c'
KEY_DATA = 'data'
KEY_ERROR = 'error'


from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
import base64
import json
import os
import sqlite3
import sys
import threading


lock = threading.Lock()
db_file = None


def log(msg, newline=1, stream=sys.stdout):
    try:
        newline = int(newline)
    except ValueError:
        newline = 0
    #
    end = os.linesep * newline
    #
    if not stream in [sys.stdout, sys.stderr]:
        return 
    #
    stream.write('%s%s' %(msg, end) )

def db_connect(db_file):
    ret = None
    try:
        ret = sqlite3.connect(db_file)
    except:
        pass
    #
    return ret

def db_get_query(s, q, decode=True):
    ret = ''
    #
    qs = urlparse(s).query
    try:
        q = parse_qs(qs).get(q, '')[0]
        if decode:
            ret = base64.decodestring(q.encode())
            ret = ret.decode()
        else:
            ret = q
    except:
        pass
    #
    return ret

def db_query(db, query):
    ret = {}
    try:
        c = db.cursor()
        c.execute(query)
        res = c.fetchall()
        ret[KEY_DATA] = res
    except Exception as e:
        ret[KEY_ERROR] = str(e)
    #
    return ret
    

class DatabaseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        res = {}
        #
        q = db_get_query(self.path, QUERY_QUERY)
        c = db_get_query(self.path, QUERY_COMMIT, decode=False)
        #
        self.send_response(200)
        self.send_header(CONTENT_HEADER, CONTENT_MIME)
        self.end_headers()
        #
        if q:
            with lock:
                db = db_connect(db_file)
                res = db_query(db, q)
                if c:
                    db.commit()
                db.close()
        #
        ret = json.dumps(res)
        self.wfile.write(ret.encode())
        #
        return
    
        
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
    

if __name__ == '__main__':
    log(APP_TITLE)
    log('')
    #
    if len(sys.argv) < 2:
        log('%s %s' %(sys.argv[0], '<database_file> [port]'))
        sys.exit(1)
    #
    try:
        port = int(sys.argv[2])
    except:
        port = DEFAULT_PORT    
    #
    db_file = os.path.abspath(sys.argv[1])
    db = db_connect(db_file)
    if not db:
        log('%s %s' %('ERROR: unable to connect to', db_file), stream=sys.stderr)
        sys.exit(2)        
    #
    log(db_file)
    log(port)
    log('')
    #
    try:
        server = ThreadedHTTPServer((DEFAULT_HOST, port), DatabaseHandler)
        server.serve_forever()
    except BaseException as e:
        log(e, stream=sys.stderr)
        sys.exit(3)

