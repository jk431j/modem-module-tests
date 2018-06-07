#!/usr/bin/python
import serial
import time as tm
import re
import sys
import string
from platform import system

sep = ','
waitsec = 60

if system() == 'Windows':
   port = 'COM30'
else:
   port = '/dev/ttyUSB1'

try:
   SK = serial.Serial(port, baudrate = 115200, timeout = 1)
except serial.serialutil.SerialException:
   print('Could not open {}'.format(port))
   sys.exit()

SK.write(b'ATE0\r\n')
status = SK.readlines()


SK.write(b'AT+CMEE=2\r\n')
status = SK.readlines()

print('Time,PLMN,EARFCN,RSRP,RSSI,RSRQ,TAC,TXPWR,DRX,MM,RRC,CID,IMSI,NetName,SD,ABND,SINR,DNSResp,DNSIP,DNSTime')

try:
   failures = 0

   while True:
      startsec = tm.time()

      SK.timeout = 10
      SK.write(b'AT#QDNS=www.att.com\r\n')

      startdns = tm.time()
      dnsgot = SK.read(1)
      if len(dnsgot) > 0:
         dnstime = tm.time() - startdns
      else:
         dnstime = -1

      dns = SK.readlines()

      SK.timeout = 1
      SK.write(b'AT#RFSTS\r\n')
      netstat = SK.readlines()

      try:
          netstat_str = netstat[1][8:-2]
          dns_str = dns[1][:-2]
          failures = 0
      except:
          netstat_str = ''
          dns_str = ''
          print dns, netstat
          failures += 1
          if failures > 5:
              print "Too many failures, reopening serial port"
              SK.close()
              tm.sleep(5)
              SK.open()

      print(sep.join([tm.strftime('%Y-%m-%d %H:%M:%S'), netstat_str, dns_str,'{:.2f}'.format(dnstime)]))

      sys.stdout.flush()

      sleepsec = startsec + waitsec - tm.time()
      if sleepsec > 0:
         tm.sleep(sleepsec)
except KeyboardInterrupt:
   sys.exit()
