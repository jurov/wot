#!/usr/bin/env python2
#
# Script to synchronize a sqlite database with published level2 WoT of assbot of #bitcoin-assets.
#
# All commandline options are passed unchanged to gpg.

import sys
import csv
import re
from urllib2 import urlopen
import sqlite3

def db_conn(dbfile):
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS WoT (keyid text primary key, l1 integer, l2 integer, nick text)")
    conn.commit()
    return conn



res = urlopen('http://files.bitcoin-assets.com/wot/trustlist.txt')
# download ought to be checked by /msg assbot !shasum wot
# but we just check if data looks like fingerprints to avoid parameter injections
check = re.compile('^[0-9A-F]{40}$')
trustre = re.compile('^L1:([0-9]+)/L2:([0-9]+)$')
conn = None
cur = None
exist = None
csvReader = csv.reader(res, delimiter=' ', quoting=csv.QUOTE_NONE)
for row in csvReader:
    trust = trustre.match(row[1])
    if trust and check.match(row[0]):
        if not conn:
            conn = db_conn(sys.argv[1])
            cur = conn.cursor()
            cur.execute("UPDATE WoT SET l1 = -9999, l2= -9999")
            cur.execute("SELECT keyid from WoT")
            exist = frozenset([item for (item,) in cur.fetchall()])
    else:
        raise ValueError("Bad data: %s" % row)

    trust = trust.groups()
    params = dict(keyid=row[0], l1=trust[0], l2=trust[1], nick=row[2])
    if row[0] in exist:
        cur.execute("UPDATE WoT set l1 = :l1, l2 = :l2, nick = :nick WHERE keyid = :keyid", params)
    else:
        cur.execute("INSERT INTO WoT (keyid, l1, l2, nick) VALUES (:keyid, :l1, :l2, :nick)", params)
conn.commit()
