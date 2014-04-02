#!/usr/bin/python
# (c) - vitush@maven.co
#
from spyderlib.utils.qthelpers import action2button

import sys, getopt
import imaplib
import re

def get_quota(imap_connection, mailbox='inbox'):
    status,value = imap_connection.getquotaroot(mailbox)
    #status,value = ('OK',
    #    [['inbox user/xyz12'], ['user/xyz12 (STORAGE 80000 102400)']])
    quota = value[1][0]
    regexp = re.compile(r'(.*) \(STORAGE ([0-9]*) ([0-9]*)\)')
    m = regexp.match(quota)
    root,used,avail = m.groups()
    return (root, int(used), int(avail))


def get_mailbox_size(imap_connection, mailbox='inbox'):
    status,value = imap_connection.select(mailbox, readonly=True)
    if status != 'OK':
        raise Exception(value)
    status,value = imap_connection.search(None, 'ALL')
    size = 0
    regexp = re.compile(r'.*RFC822\.SIZE ([0-9]*).*')
    for num in value[0].split():
        status,value = imap_connection.fetch(num, '(RFC822.SIZE)')
        #status,value = ('OK', ['231 (RFC822.SIZE 4882)'])
        match = regexp.match(value[0])
        msg_size = int(match.group(1))
        size += msg_size
    return size

def get_connection(host,ssl=True):
    imap = None
    if ssl is True:
        imap = imaplib.IMAP4_SSL(host)
    else:
        imap = imaplib.IMAP4(host)
    return imap


def usage():
    print 'check_mailbox.py  <--used|--quota|--percent> --host=<host> [--ssl] --user=<user> --password=<password>  '
    print '     --used     -  Get used bytes '
    print '     --quota    -  Get mailbox quota'
    print '     --percent  -  Get percents if usage'
    print '     --host     -  Imap Server'
    print '     --user     -  User'
    print '     --password -  password'
    print '     --ssl      -  Use secure connection'


def main(argv):
    host = None
    port = None
    user = None
    password = None
    ssl = False
    action = None

    try:
        opts, args = getopt.getopt(argv,"h",["used","quota","percent","ssl","host=","user=","password="])
    except getopt.GetoptError, err :
        print "Unknown parameter : %s" % str(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "Usage: "
            usage()
            sys.exit()
        elif opt in ("--ssl"):
            ssl = True
        elif opt in ("--host"):
            host = arg
        elif opt in ("--user"):
            user = arg
        elif opt in ("--password"):
            password = arg
        elif opt in ("--used"):
            action = "used"
        elif opt in ("--quota"):
            action = "quota"
        elif opt in ("--percent"):
            action = "percent"


    if host is None or user is None or password is None or action is None:
        usage()
        sys.exit()


    imap = get_connection(host,ssl)
    imap.login(user, password)

    z,u,q = get_quota(imap)
    if action == "used" :
        print u
    elif action == "percent" :
        #print '%.2f' % (float(u)/float(q)*100)
        print int(float(u)/float(q)*100)
    elif action == "quota":
        print q
    else :
        print "Unknown parameter"



if __name__ == "__main__":
   main(sys.argv[1:])