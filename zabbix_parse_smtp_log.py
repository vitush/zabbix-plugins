#!/usr/bin/python

import re
import time
import datetime
import sys, getopt

logfile = "/home/vitush/workspace.maven3.6/maven_zabbix/mail.log"
logfile_time_label = "/home/vitush/workspace.maven3.6/maven_zabbix/mail.log.time"

def get_smtp_subject(code):
    if code=="0":
     return "Other or Undefined Status"  
    elif code=="1":
     return "Addressing Status"  
    elif code=="2":
     return "Mailbox Status"  
    elif code=="3":
     return "Mail System Status"  
    elif code=='4':
     return "Network and Routing Status"  
    elif code=="5":
     return "Mail Delivery Protocol Status"  
    elif code=="6":
     return "Message Content or Media Status"  
    elif code=="7":
     return "Security or Policy Status" 
    else :
     return "Unknown" 


def get_smtp_detail(code):
    if code=="1.0" : 
     return "Other address status"  
    elif code=="1.1" : 
     return "Bad destination mailbox address"  
    elif code=="1.2" : 
     return "Bad destination system address"  
    elif code=="1.3" : 
     return "Bad destination mailbox address syntax"  
    elif code=="1.4" : 
     return "Destination mailbox address ambiguous"  
    elif code=="1.5" : 
     return "Destination mailbox address valid"  
    elif code=="1.6" : 
     return "Mailbox has moved"  
    elif code=="1.7" : 
     return "Bad sender's mailbox address syntax"  
    elif code=="1.8" : 
     return "Bad sender's system address"  
    elif code=="2.0" : 
     return "Other or undefined mailbox status"  
    elif code=="2.1" : 
     return "Mailbox disabled, not accepting messages"  
    elif code=="2.2" : 
     return "Mailbox full"  
    elif code=="2.3" : 
     return "Message length exceeds administrative limit."  
    elif code=="2.4" : 
     return "Mailing list expansion problem"  
    elif code=="3.0" : 
     return "Other or undefined mail system status"  
    elif code=="3.1" : 
     return "Mail system full"  
    elif code=="3.2" : 
     return "System not accepting network messages"  
    elif code=="3.3" : 
     return "System not capable of selected features"  
    elif code=="3.4" : 
     return "Message too big for system"  
    elif code=="4.0" : 
     return "Other or undefined network or routing status"  
    elif code=="4.1" : 
     return "No answer from host"  
    elif code=="4.2" : 
     return "Bad connection"  
    elif code=="4.3" : 
     return "Routing server failure"  
    elif code=="4.4" : 
     return "Unable to route"  
    elif code=="4.5" : 
     return "Network congestion"  
    elif code=="4.6" : 
     return "Routing loop detected"  
    elif code=="4.7" : 
     return "Delivery time expired"  
    elif code=="5.0" : 
     return "Other or undefined protocol status"  
    elif code=="5.1" : 
     return "Invalid command"  
    elif code=="5.2" : 
     return "Syntax error"  
    elif code=="5.3" : 
     return "Too many recipients"  
    elif code=="5.4" : 
     return "Invalid command arguments"  
    elif code=="5.5" : 
     return "Wrong protocol version"  
    elif code=="6.0" : 
     return "Other or undefined media error"  
    elif code=="6.1" : 
     return "Media not supported"  
    elif code=="6.2" : 
     return "Conversion required and prohibited"  
    elif code=="6.3" : 
     return "Conversion required but not supported"  
    elif code=="6.4" : 
     return "Conversion with loss performed"  
    elif code=="6.5" : 
     return "Conversion failed"  
    elif code=="7.0" : 
     return "Other or undefined security status"  
    elif code=="7.1" : 
     return "Delivery not authorized, message refused"  
    elif code=="7.2" : 
     return "Mailing list expansion prohibited"  
    elif code=="7.3" : 
     return "Security conversion required but not possible"  
    elif code=="7.4" : 
     return "Security features not supported"  
    elif code=="7.5" : 
     return "Cryptographic failure"  
    elif code=="7.6" : 
     return "Cryptographic algorithm not supported"  
    elif code=="7.7" : 
     return "Message integrity failure"  
    else : 
       return "Unknown"



def get_smtp_class(code):
    if code=="2" :
        return "Success"
    elif code=="4" : 
        return "Persistent Transient Failure"
    elif code=="5" : 
        return "Permanent Failure"
    else: 
        return "Unknown"
    
def get_smtp_date(line):
    if line is None:
        return None
    m = re.search(r'^(\w+ \d+ \d+:\d+:\d+)', line)
    if m is not None:
        mail_date  = "{0} {1}".format(m.group(1),time.strftime("%Y"))
        return  datetime.datetime.strptime(mail_date, "%b %d %H:%M:%S %Y")
    return None
    
def get_smtp_status(line):
    if line is None:
        return None
    m = re.search(r'stat=(.*): (.*)', line)
    if m is not None:
        stat = m.group(1)
        message = m.group(2)
        return  (stat,message)
    return None

def get_smtp_code(line):
    m = re.search(r'dsn=(\d+)\.(\d+)\.(\d+)', line)
    if m is not None:
        return (m.group(1),m.group(2),m.group(3))
    return (None,None,None)


def match_code(codemask,c,s,d):
    if c is None or s is None or d is None :
        return False
            
    m = re.search(r'(\w+)\.(\w+)\.(\w+)', codemask)
    if m is not None:
        m1 = m.group(1)
        m2 = m.group(2)
        m3 = m.group(3)
    
        if m1 == 'x' :
            m1='\d+'
        if m2 == 'x':
            m2='\d+'
        if m3 == 'x':
            m3='\d+'
    
#    print  "===> Mask: {0}\.{1}\.{2}".format(m1,m2,m3)
#    print  "===> code {0}.{1}.{2}".format(c,s,d) 
    
    a = re.compile("{0}\.{1}\.{2}".format(m1,m2,m3))
    if  a.match("{0}.{1}.{2}".format(c,s,d)) :
        return True
    return False
    
        
    

def parse_log_file(logfile,codemask,deltatime):
    end_date = datetime.datetime.now()
    start_date = datetime.datetime.now() - datetime.timedelta(seconds=int(deltatime))
    
    sum_lines = 0
    with open(logfile) as f:
     for line in f:
        smtp_date = get_smtp_date(line)
        if smtp_date > end_date:
            break;
                    
        if smtp_date < start_date : 
            continue

        c,s,d = get_smtp_code(line)
        if match_code(codemask,c,s,d) == True:
            sum_lines = sum_lines +1;
    return sum_lines


#############################
#
# main
#

def main(argv):
    delta_time = '600'
    smtp_code = '0.0.0'
    usage = 'check_mail_logs.py -t <time> -c <code>'
    try:
        opts, args = getopt.getopt(argv,"ht:c:",["time=","code="])
    except getopt.GetoptError:
        print usage
        sys.exit(2)

    for opt, arg in opts:
      if opt == '-h':
         print usage
         sys.exit()
      elif opt in ("-t", "--time"):
         delta_time = arg
      elif opt in ("-c", "--code"):
         smtp_code = arg
    
    print parse_log_file(logfile=logfile,codemask=smtp_code,deltatime=delta_time)
    

if __name__ == "__main__":
   main(sys.argv[1:])
   
   
   
