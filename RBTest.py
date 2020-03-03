#!/usr/bin/python
import serial
import sys
import time
import datetime

def SendMessage(ser, msg):
  ser.write(msg)
  print(msg)

def WaitForResponse(ser, prt):
  resp = ''
  while(not '\n' in resp):
    resp = resp + ser.read()
  resp = ''
  while(not '\n' in resp):
    resp = resp + ser.read()
  if prt:
    print(resp)
  
  
def Transact(ser, msg):
  SendMessage(ser, msg)
  WaitForResponse(ser, 1)
  
def main():
  RB = serial.Serial(sys.argv[1], 19200, timeout = 2)
  checksum = 0
  Transact(RB, 'AT\r')
  Transact(RB, 'AT&K0\r')
  Transact(RB, 'AT+SBDWB=340\r')
  for i in range(340):
    checksum = checksum + (i%255)
    SendMessage(RB, chr(i%255))
  SendMessage(RB, chr((checksum & 0xFF00) >> 8))
  SendMessage(RB, chr(checksum & 0xFF))
  Transact(RB, '\r')
  WaitForResponse(RB, 1)
  Transact(RB, 'AT+SBDIX\r')
  #Transact(RB, 'AT+SBDD0\r')

while(1):
  now = datetime.datetime.now()
  realnow = datetime.datetime.now()
  noop = 0
  main()
  while(now.minute == realnow.minute):
    realnow = datetime.datetime.now()
  
# This one:
# AT\r
# AT&K0\r
# AT+SBDWB=340\r
# Send Message
# AT+SBDIX\r
# AT+SBDD0\r
#
# Payload:
# ONCE
# ATE0\r
# AT&K0\r
# AT&D0\r
# AT+SBDMTA=0\r
# AT+SBDD0\r
# AT+CGSN\r
# 
# SENDING MESSAGE
# AT+SBDWB=340\r
# Send Message
# AT+SBDIX\r
# if message in buffer
# AT+SBDRB\r
# otherwise
# AT\r
