#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import threading
import urllib
import time
import serial
import sys
#import os
#import Queue

#import datetime

PORT_NUMBER = 8080

currStringNum = 0

serverSentStrings=[]
for each in range(256):
    serverSentStrings.append("")
    
serverGotStrings=[]
    
def slowSend(stringToSlowSend, serialPortToSendTo):
    for i in stringToSlowSend:
        serialPortToSendTo.write(i)
        time.sleep(0.01)
    
#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    #Handler for the GET requests
    def do_GET(self):
        global currStringNum
        self.send_response(200)
        self.end_headers()
        if self.path=='/':
            with open("RemoteBlock.html",'r') as indexPage:
                self.wfile.write(indexPage.read())
                #for each in range(100):
                #    time.sleep(1)
                #    self.wfile.write("This is howdy #" + str(each+2) + '!\n')
                
                
        elif self.path.startswith('/send'):
            stringToSerialSend = urllib.unquote(self.path.split('?=')[1])
            serverGotStrings.append(stringToSerialSend)
            
            
        elif self.path.startswith('/get'):
            stringNumToReturn = -1
            
            # #What's below is 'safe' by trying to int cast
            # #But might be more dangerous, since I can't see any exception
            #try:
            #    stringNumToReturn = int(self.path.split('?=')[1])
            #if(stringNumToReturn == -1):
            #    return
            stringNumToReturn = int(self.path.split('?=')[1]) #Dangerous way, just doing it
            
            if(stringNumToReturn == currStringNum):
                if (serverSentStrings[(stringNumToReturn)%256] == ""):
                    
                    #keepWaiting = True
                    #secondsToWait = 10
                    #closingTime = time.mktime(time.gmtime()) + secondsToWait
                    ##If the current string is empty, we can hold onto it for a while until something cool happens
                    #while(keepWaiting and (closingTime >= time.mktime(time.gmtime()))):
                    #    if(serverSentStrings[(stringNumToReturn)%256] != ""):
                    #        keepWaiting = False
                    pass
                    
                else:
                    serverSentStrings[((stringNumToReturn)+1)%256] = ""
                    currStringNum = ((stringNumToReturn)+1)%256
                print("stringNumToReturn: " + str(stringNumToReturn))
                print("String           : " + str(serverSentStrings[(stringNumToReturn)%256]))
                print("--------------------------------------------")
                self.wfile.write(serverSentStrings[(stringNumToReturn)%256])
                  
            else:
                #self.wfile.write(serverSentStrings[(stringNumToReturn)%256])  #Safe way, modulo'ing into the array
                self.wfile.write(serverSentStrings[stringNumToReturn])  #Dangerous way, jamming the biz into the array
                print("stringNumToReturn: " + str(stringNumToReturn))
                
                
        elif self.path.startswith('/next'):
            self.wfile.write(str(currStringNum))
                
        return

class serialRead(threading.Thread):
    def __init__(self,ser):
        threading.Thread.__init__(self)
        self.ser=ser
        self.keepGoing = True
    def run(self):
        while(self.keepGoing):
            thisReading = ser.read()
            if not (thisReading == ''):
                serverSentStrings[currStringNum] += thisReading
                
class serialWrite(threading.Thread):
    def __init__(self,ser):
        threading.Thread.__init__(self)
        self.ser=ser
        self.keepGoing = True
    def run(self):
        while(self.keepGoing):
            if len(serverGotStrings):
                self.send(serverGotStrings.pop(0))
            else:
                time.sleep(1)
    def send(self,msg):
        for i in msg:
            self.ser.write(i)
            time.sleep(0.01)
        
doRun=1

with serial.Serial(sys.argv[1], 19200, timeout=1) as ser:

    readThread = serialRead(ser)
    writeThread = serialWrite(ser)

    # Start new Threads
    readThread.start()
    writeThread.start()

    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER

        #Wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
        doRun=0
        readThread.keepGoing=False
        writeThread.keepGoing=False
