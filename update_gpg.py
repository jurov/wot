#!/usr/bin/env python2
#
# Script to synchronize GPG keyring with published level2 WoT of assbot of #bitcoin-assets.
#
# All commandline options are passed unchanged to gpg.

import sys, subprocess
import csv, StringIO
from urllib2 import urlopen

res = subprocess.check_output(['gpg'] + sys.argv[1:] + ['-k','--fingerprint','--with-colons','--fixed-list-mode'])

gpgkeys = set()
assbotkeys = set()

addkey = True
csvReader = csv.reader(StringIO.StringIO(res), delimiter=':', quoting=csv.QUOTE_NONE)
for row in csvReader:
    if row[0] == 'pub':
        #Skip expired, they should be refreshed
        addkey = not ('e' in row[1])
    elif row[0] == 'fpr' and addkey:
        gpgkeys.add(row[9])


res = urlopen('http://files.bitcoin-assets.com/wot/trustlist.txt')
csvReader = csv.reader(res, delimiter=' ', quoting=csv.QUOTE_NONE)
for row in csvReader:
    assbotkeys.add(row[0])

for keyid in (assbotkeys - gpgkeys):
    print("Adding %s" % keyid)
    subprocess.call(['gpg'] + sys.argv[1:] + ['--batch', '--recv-keys', keyid])


for keyid in (gpgkeys - assbotkeys):
    print("Removing %s" % keyid)
    subprocess.call(['gpg'] + sys.argv[1:] + ['--batch', '--delete-key', keyid])