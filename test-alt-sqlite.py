#!/usr/bin/env python3
#
#
# test-alt-sqlite.py
# (c) Noprianto <nop@noprianto.com>
# 2016
# License: GPL
# https://github.com/nopri/code/
#
# Tested in Python 3.4 using only standard library
#

import sqlite3


URL = 'http://localhost:8080/?q='
MAX_ROWS = 50000
FILE = 'test-alt.db'

def main():
    conn = sqlite3.connect(FILE)
    cur = conn.cursor()
    cur.execute('create table test(a integer)')
    #
    for i in range(MAX_ROWS):
        cur.execute('insert into test(a) values(%s)' %i)
    #
    cur.execute('select max(ROWID) from test')
    print(cur.fetchall())
    #
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
