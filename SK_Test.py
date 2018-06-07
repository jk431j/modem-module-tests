#!/usr/bin/python
import serial
import time as tm
import re
import sys
import string as str
from platform import system

junk = re.compile('(OK)?\r\n|\%NOTIFYEV\:')
codes = re.compile('\s?(\+(CREG|CSQ|COPS)\:\s)?')
pingtime = re.compile('time=(\d+\.\d+)\sms')
sep = ';'
waitsec = 60

def NoJunk(line):
   return junk.match(line) == None

if system() == 'Windows':
   port = 'COM30'
else:
   port = '/dev/ttyACM0'

try:
   SK = serial.Serial(port, timeout = 1)
except serial.serialutil.SerialException:
   print('Could not open {}'.format(port))
   sys.exit()

SK.write(b'ATE0\nAT+CREG=1\n')
SK.readlines()

SK.write(b'AT%EXE="sed -i.bk s/attempts:1/attempts:3/ /etc/resolv.conf"\n')
status = SK.readlines()
print(status)

try:
   while True:
      startsec = tm.time()

      SK.write(b'AT+CREG?\nAT+CSQ\nAT+COPS?\n')
      status = SK.readlines()

      SK.write(b'AT@dnsresvdon="www.att.com"\n')
      tm.sleep(20)
      dns = SK.readlines()

      SK.write(b'AT%EXE="ping -c 1 8.8.8.8"\n')
      tm.sleep(10)
      ping = SK.readlines()
      pingfound = pingtime.search(''.join(ping))
      if pingfound != None:
         ping = [ pingfound.group(1) ]
      else:
         ping = []

      print(tm.strftime('%Y-%m-%d %H:%M:%S') + ';' +
	                                                                  re.sub(codes, '',     # 4. remove response codes
	                                 sep.join(                                              # 2. join into string
	    filter(NoJunk, status + dns) + ping                                                 # 1. filter junk
	                                         ).replace('\r\n', '')))                        # 3. remove CRLF
      sys.stdout.flush()


      sleepsec = startsec + waitsec - tm.time()
      if sleepsec > 0:
         tm.sleep(sleepsec)
except KeyboardInterrupt:
   sys.exit()

