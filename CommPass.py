#!/usr/bin/python
import serial
import time
import datetime
import sys
pay = serial.Serial(sys.argv[1], 19200, timeout = 0.005)
rock = serial.Serial(sys.argv[2], 19200, timeout = 0.005)
go = True
while(go):
  thisNow = datetime.datetime.now()
  min = thisNow.minute
  with open("paystring" + str(thisNow.minute) + ".txt", "wb") as payfile:
    with open("rockstring" + str(thisNow.minute) + ".txt", "wb") as rockfile:
      while(min == thisNow.minute):
        try:
          paystring = pay.read()
          rockstring = rock.read()
          rock.write(paystring)
          pay.write(rockstring)
          rockfile.write(rockstring)
          payfile.write(paystring)
          if len(rockstring) > 0:
            print(rockstring)
          thisNow = datetime.datetime.now()
        except:
          go = False
          rock.close()
          pay.close()
