#!/usr/bin/env python

'''
Kentang: Simple Network Monitoring Program
- Features:
  - protocols: http, https, ftp, smtp, imap4, imap4ssl, pop3, pop3ssl
  - multi threaded
  - multi platform
  - command line interface
  - simple event handler (ok/fail)
  - simple configuration file (INI file)

- Configuration section
  [<host>[,optional tag]]
  protocol = <supported protocol>
  port     = [optional, port]
  ok       = [optional, execute this command if ok]
  fail     = [optional, execute this command if fails]
   
- Arguments passed to event handler:
  - time 
  - hostname
  - port

- Started by: Noprianto <nop@noprianto.com>

- Website: http://www.noprianto.com

- License: GPL
'''


import os
import sys; sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
import ConfigParser
import time
import threading
import httplib
import ftplib
import smtplib
import imaplib
import poplib
import socket

NAME = 'kentang'
VERSION = ( (0, 30), '26-OCT-2012-UTC+7' )
PROTOCOLS = (
        'http', 
        'https',
        'ftp', 
        'smtp', 
        'imap4', 
        'imap4ssl',
        'pop3',
        'pop3ssl',
        )
PROTOLEN = max([len(x) for x in PROTOCOLS]) 
ITEMS = [
        'protocol', 
        'port', 
        'ok', 
        'fail'
        ]
TIMEOUT = 10
ERRORS = {
            0  : ['', '', ''],
            1  : ['', 'Config file not specified', ''],
            2  : ['', 'Unable to open config file', ''],
            3  : ['', 'Error parsing config file', ''],
            64 : ['', 'Interrupted by user', ''],
            127: ['', 'General error', ''],
        }


def error(code, func='', extra=''):
    global ERRORS
    #
    ERRORS[code][0] = func
    ERRORS[code][2] = extra
    #
    return code


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


def print_version():
    v = '.'.join([str(x) for x in VERSION[0]])
    s = '%s version %s (%s)' %(NAME, v, VERSION[1])
    log(s)
    #
    return error(0)


def parse_config(file):
    log('Using config file: %s' %(file))
    ret = []
    #
    c = ConfigParser.ConfigParser()
    #
    try:
        c.read(file)
    except:
        return ret
    #
    s = c.sections()
    for i in s:
        error = 0
        entry = {}
        try:
            host = i.split(',')[0].strip()
        except:
            host = ''
        entry['host'] = host
        #
        for j in ITEMS:
            try:
                e = c.get(i, j).strip()
            except ConfigParser.NoOptionError:
                e = ''
            #
            if j == 'protocol' and e not in PROTOCOLS:
                log('Unsupported protocol: %s(%s), ignoring...' %(
                    e, i), stream=sys.stderr)
                error = 1
            elif j == 'port':
                try:
                    e = int(e)
                except ValueError:
                    e = None
            #
            entry[j] = e
        #
        if not error:
            ret.append(entry)
    #
    return ret


def working(config):
    socket.setdefaulttimeout(TIMEOUT)    
    log('Timeout: %ds' %(TIMEOUT))
    log('Found %d host(s)' %(len(config)))
    log('Please wait...')
    start = time.time()
    #
    threads = []
    for i in config:
        thread = HostChecker(i)
        threads.append(thread)
        thread.start()
    #    
    while True:
        for i in threads:
            if not i.isAlive():
                threads.remove(i)
        if not threads:
            break
    #
    finish = time.time()
    #
    msg = 'Done, checked %d host(s) in %0.2f second(s)' %(
            len(config), finish-start       
        )
    log(msg)
    #
    return error(0)
        

def main(argv):
    print_version()
    try:
        c = argv[1]
    except IndexError:
        return error(1)
    #
    c = os.path.abspath(c)
    try:
        ct = open(c)
    except IOError:
        return error(2, extra=c)
    #
    config = parse_config(c)
    if not config:
        return error(3, extra=c)
    #
    try:
        ret = working(config)
    except KeyboardInterrupt:
        return error(64)
    #
    return ret


class HostChecker(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        self.host = host

    def handler_http(self, secure=False):
        ret = 0
        status = '000'
        info = '[FAILED]'
        port = self.host['port']
        try:
            if secure:
                if not port: 
                    port = 443
                    self.host['port'] = port
                conn = httplib.HTTPSConnection(self.host['host'], port)
            else:
                if not port:
                    port = 80
                    self.host['port'] = port
                conn = httplib.HTTPConnection(self.host['host'], port)
            #
            conn.request('HEAD', '/')
            res = conn.getresponse()
            status = str(res.status)
            msg = '%s: %s:%s %s ' %(
                self.host['protocol'].ljust(PROTOLEN),
                self.host['host'], 
                port,
                status
                )
        except:
            msg = '%s: %s:%s ' %(
                self.host['protocol'].ljust(PROTOLEN),
                self.host['host'],
                port,
                )
        #
        if status[0] in ['1', '2', '3']:
            info = '[OK]'
            ret = 1
        #
        log(msg + info)
        #
        return ret
    
    def handler_https(self):
        return self.handler_http(secure=True)
    
    def handler_ftp(self):
        ret = 0
        info = '[FAILED]'
        #
        port = self.host['port']
        if not port:
            port = 21
            self.host['port'] = port
        #
        try:
            conn = ftplib.FTP()
            conn.connect(self.host['host'], port)
            info = '[OK]'
            ret = 1
        except:
            ret = 0
        #
        msg = '%s: %s:%s ' %(
            self.host['protocol'].ljust(PROTOLEN),
            self.host['host'], 
            port,
            )
        log(msg + info)
        #
        return ret        

    def handler_smtp(self):
        ret = 0
        info = '[FAILED]'
        #
        port = self.host['port']
        if not port:
            port = 25
            self.host['port'] = port
        #
        try:
            conn = smtplib.SMTP(self.host['host'], port)
            info = '[OK]'
            ret = 1
        except:
            ret = 0
        #
        msg = '%s: %s:%s ' %(
            self.host['protocol'].ljust(PROTOLEN),
            self.host['host'], 
            port, 
            )
        log(msg + info)
        #
        return ret        

    def handler_imap4(self, secure=False):
        ret = 0
        info = '[FAILED]'
        #
        port = self.host['port']
        try:
            if secure:
                if not port: 
                    port = 993
                    self.host['port'] = port
                conn = imaplib.IMAP4_SSL(self.host['host'], port)
            else:
                if not port:
                    port = 143
                    self.host['port'] = port
                conn = imaplib.IMAP4(self.host['host'], port)
            #
            info = '[OK]'
            ret = 1
        except:
            ret = 0
        #
        msg = '%s: %s:%s ' %(
            self.host['protocol'].ljust(PROTOLEN),
            self.host['host'], 
            port, 
            )
        log(msg + info)
        #
        return ret        
    
    def handler_imap4ssl(self):
        return self.handler_imap4(secure=True)

    def handler_pop3(self, secure=False):
        ret = 0
        info = '[FAILED]'
        #
        port = self.host['port']
        try:
            if secure:
                if not port: 
                    port = 995
                    self.host['port'] = port
                conn = poplib.POP3_SSL(self.host['host'], port)
            else:
                if not port:
                    port = 110
                    self.host['port'] = port
                conn = poplib.POP3(self.host['host'], port)
            #
            info = '[OK]'
            ret = 1
        except:
            ret = 0
        #
        msg = '%s: %s:%s ' %(
            self.host['protocol'].ljust(PROTOLEN),
            self.host['host'], 
            port, 
            )
        log(msg + info)
        #
        return ret        
    
    def handler_pop3ssl(self):
        return self.handler_pop3(secure=True)
        
    def run(self):
        fn = 'handler_' + self.host['protocol']
        func = getattr(HostChecker, fn)
        ret = func(self)
        #
        cmd = ''
        if not ret:
            if self.host['fail']:
                htype = 'fail'
                cmd = self.host['fail']
        else:
            if self.host['ok']:
                htype = 'ok'
                cmd = self.host['ok']
        #
        if cmd:
            cmds = "%s '%s' '%s' '%s'" %(
                cmd, time.asctime(), 
                self.host['host'], 
                self.host['port'])
            log('  Execute %s %s-%s handler: %s' %(
                    self.host['host'], 
                    self.host['protocol'],
                    htype,
                    cmd
                    ))                
            os.system(cmds)


if __name__ == '__main__':        
    ret = main(sys.argv)
    if ret > 0:
        err = [x for x in ERRORS[ret] if x.strip()]
        msg = ': '.join(err)
        log(msg, stream=sys.stderr)
    #
    sys.exit(ret)

