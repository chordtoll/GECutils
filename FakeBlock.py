#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import threading
import urllib
import time
import serial
import sys
import os
import Queue

import requests

from selenium import webdriver

import datetime
#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import threading
import urllib
import time
import serial
import sys
import os
import Queue

import requests

from selenium import webdriver

import datetime

driver=webdriver.Chrome()
driver.set_page_load_timeout(60)

PORT_NUMBER = 8080

def o16(s):
    return ord(s[0])+ord(s[1])*256

def s16(s):
    os=o16(s)
    if os&0x8000:
        os=-(0x10000-os)
    return os

def o32(s):
    return ord(s[0])+ord(s[1])*256+ord(s[2])*256*256+ord(s[3])*256*256*256

def gpst(s):
    os=o32(s)
    h=os/10000
    m=(os/100)%100
    s=os%100
    return "%02d:%02d:%02d"%(h,m,s)
def gpsla(s):
    os=o32(s)
    n=False
    if os&0x80000000:
        n=True
    os&=0x7FFFFFFF
    d=os/1000000
    m=((os%1000000)/10000.0)/60
    print d,m
    return (d+m)*(-1 if n else 1)
def gpslo(s):
    os=o32(s)
    n=False
    if os&0x80000000:
        n=True
    os&=0x7FFFFFFF
    d=os/1000000
    m=((os%1000000)/10000.0)/60
    print d,m
    return (d+m)*(-1 if n else 1)
def gpsa(s):
    return o32(s)/10.0

def sanitize(s):
    o=""
    for i in xrange(len(s)):
        if s[i]=='\r':
            o=o+'\xEF\xBC\xB2'
        elif s[i]=='\n':
            o=o+'\xEF\xBC\xAE'
        elif ord(s[i])<32:
            o=o+'\xEF\xBC\x8A'
        else:
            o=o+s[i]
    return o

#rbdebug='\x00\x04\xf0\x9f\x8e\x88\x02\xa5'
rbdebug=''

thread1=None
#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path=='/' or self.path.startswith('/?message='):
            if self.path.startswith('/?message='):
                msg=self.path.split('=')[1]
                msg=urllib.unquote(msg)
                print msg
                thread1.putmsg(msg)
            self.wfile.write("""
            <head>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
                <script>
                    function reloadmsg () {
                        $("#messages").load("messages.txt");
                        $('#messages').scrollTop($('#messages')[0].scrollHeight);
                        $("#messagesh").load("messages.hex");
                        $('#messagesh').scrollTop($('#messagesh')[0].scrollHeight);
                    }
                </script>
            </head>
            <body onload="setInterval(reloadmsg,1000)">
            <form accept-charset="UTF-8"><textarea cols=80 rows=30 id="messages">Messages</textarea><textarea cols=120 rows=30 id="messagesh">Messages</textarea></form>
            <form accept-charset="UTF-8" action="/" method="get"><input type="text"name="message"/><input type="submit"/></form>
            </body>
            """)
            
            
        #h2 does not work
        #v1 does not work
        #v2 does not work
        if self.path=='/messages.txt':
            for i,Eee in zip(thread1.txes,thread1.txTimes):
                self.wfile.write("V:%02x Y:%02x S:%04x\n"%(ord(i[0]),ord(i[1]),o16(i[2:4])))
                self.wfile.write("T:%08x L:%08x L:%08x A:%08x\n"%(o32(i[4:8]),o32(i[8:12]),o32(i[12:16]),o32(i[16:20])))
                self.wfile.write("h1:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[20+n*2:22+n*2]))
                self.wfile.write("\n")
                self.wfile.write("h2:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[44+n*2:46+n*2]))
                self.wfile.write("\n")
                self.wfile.write("hD:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[68+n*2:70+n*2]))
                self.wfile.write("\n")
               
                if sys.argv[2] == "2":
                  self.wfile.write("v1:%04x v2:%04x vD:%04x\n"%(o16(i[92:94]),o16(i[94:96]),o16(i[96:98])))
                  self.wfile.write("cX:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[98+n*2:100+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cY:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[122+n*2:124+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CH:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[146+n*2:148+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CL:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[176+n*2:178+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("SUP:%08x\n"%(o32(i[206:210])))
                  self.wfile.write("BALL:%02x\n"%(ord(i[210])));
                  self.wfile.write("CUT:%02x\n"%(ord(i[211])));
                  self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                if sys.argv[2] == "3" or sys.argv[2] == "4":
                  self.wfile.write("v1:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[92+n*2:94+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("v2:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[116+n*2:118+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("vD:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[140+n*2:142+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cX:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[164+n*2:166+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cY:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[188+n*2:190+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cZ:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[212+n*2:214+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CH:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[236+n*2:238+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CL:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[266+n*2:268+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("SUP:%08x\n"%(o32(i[296:300])))
                  self.wfile.write("BALL:%02x\n"%(ord(i[300])));
                  self.wfile.write("CUT:%02x\n"%(ord(i[301])));
                  self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                
        if self.path=='/messages.hex':
            for i,Eee in zip(thread1.txes,thread1.txTimes):
                for j in xrange(0,len(i),24):
                    for k in i[j:j+24]:
                        self.wfile.write("%2x"%ord(k))
                    self.wfile.write('\n')
                self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                
        return

doRun=1

class rbthread(threading.Thread):
    def __init__(self,ser):
        threading.Thread.__init__(self)
        self.ser=ser
        self.messages=Queue.Queue()
        self.txes=[]
        self.txTimes=[]
    def run(self):
        cmd=""
        echo=False
        momsn=0
        mtmsn=0
        rxbuf=""
        txbuf=""
        state=0
        tmblen=0
        while doRun:
            c=self.ser.read()
            if c:
                print str(repr(c))[1:-1],
            if echo:
                self.ser.write(c)
            if state==1:
                if c:
                    tmblen-=1
                    if tmblen>1:
                        txbuf=txbuf+c
                    elif tmblen==1:
                        csum=ord(c)<<8
                    elif tmblen==0:
                        csum|=ord(c)
                        print repr(txbuf)
                        print "Calculated:",hex(sum([ord(i) for i in txbuf]))
                        print "Received:",hex(csum)
                        self.send("OK\r\n")
                        state=0
                        continue
            if state==0:
                if c=='\r':
                    self.send("\r\n")
                    if cmd=='!Init\'d':
                        #raw_input('========BREAK========');
                        print
                    elif len(cmd)>0 and cmd[0]=='!':
                        print
                        pass
                    if cmd=='ATE1':
                        print "Echo on"
                        echo=True
                        self.send("OK\r\n")
                    if cmd=='ATE0':
                        print "Echo off"
                        echo=False
                        self.send("OK\r\n")
                        self.txes.append('\xEE'*340)
                        
                        
                        thisNow = datetime.datetime.now()
                        hour = thisNow.hour
                        min = thisNow.minute
                        sec = thisNow.second
                        timeStr = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
                        
                        
                        self.txTimes.append(timeStr)
                    elif cmd=='AT&K0':
                        print "Flow control off"
                        self.send("OK\r\n")
                    elif cmd=='AT':
                        print "AT command"
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDMTA=0':
                        print "Ringer off"
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDD0':
                        print "RX buffer clear"
                        self.rxbuf=""
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDIX':
                        print "Transaction running"
                        time.sleep(1)
                        self.send("+SBDIX,0,")
                        self.send(str(momsn))
                        self.send(",")
                        try:
                            rxbuf=self.messages.get(False)
                            self.send("1,")
                            self.send(str(mtmsn))
                            self.send(',')
                            self.send(str(len(rxbuf)))
                            self.send(',')
                            self.send(str(self.messages.qsize()))
                            self.send('\r\n')
                            mtmsn+=1
                        except Queue.Empty:
                            self.send("0,0,0,0\r\n")
                        self.send("OK\r\n")
                        momsn+=1

                        if txbuf:
                            hecksPacket = "".join(["{:02x}".format(ord(c)) for c in txbuf])
                            try:
                              r = requests.post("http://gec.calamityconductor.com/post/", data={'data': hecksPacket, 'transmit_time' : time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()), 'iridium_latitude' : 47.6887, 'iridium_longitude' : -122.1501, 'imei' : 999999999999999, 'momsn' : momsn, 'iridium_cep' : 0.0, 'transmitted_via_satellite' : False})
                              #r = requests.post("http://172.17.0.2:8000/post/", data={'data': hecksPacket, 'transmit_time' : time.strftime("%Y-%m-%dT%H:%M:%SZ UTC",time.gmtime())})

                              print(r.status_code, r.reason)
                            except:
                              pass
                        
                            try:
                              with open(os.path.join("packets","packet.%d.%d.bin"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                f.write(txbuf)
                              try:
                                with open(os.path.join("packets","packetHTML.%d.%d.html"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                  f.write(r.text)
                              except:
                                pass
                            except:
                              os.mkdir("packets")
                              with open(os.path.join("packets","packet.%d.%d.bin"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                f.write(txbuf)
                              try:
                                with open(os.path.join("packets","packetHTML.%d.%d.html"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                  f.write(r.text)
                              except:
                                pass
                            with open("packets.csv",'a') as f:
                                f.write('%f,%d,%d,%d,'%(time.time(),ord(txbuf[0]),ord(txbuf[1]),o16(txbuf[2:4])))
                                f.write('%s,%f,%f,%f,'%(gpst(txbuf[4:8]),gpsla(txbuf[8:12]),gpslo(txbuf[12:16]),gpsa(txbuf[16:20])))
                                f.write('%d,%d,%d,%d\n'%(o16(txbuf[92:94]),o16(txbuf[94:96]),o16(txbuf[96:98]),o32(txbuf[206:210])))
                            with open("meas.csv",'a') as f:
                                for n in xrange(12):
                                    f.write("%f,%d,%d,"%(time.time(),o16(txbuf[2:4]),n))
                                    f.write("%d,"%o16(txbuf[20+n*2:22+n*2]))
                                    f.write("%d,"%o16(txbuf[44+n*2:46+n*2]))
                                    f.write("%d,"%o16(txbuf[68+n*2:70+n*2]))
                                    f.write("%d,"%s16(txbuf[98+n*2:100+n*2]))
                                    f.write("%d\n"%s16(txbuf[122+n*2:124+n*2]))
                            with open("cond.csv",'a') as f:
                                for n in xrange(15):
                                    f.write("%f,%d,%d,"%(time.time(),o16(txbuf[2:4]),n))
                                    f.write("%d,"%o16(txbuf[146+n*2:148+n*2]))
                                    f.write("%d\n"%o16(txbuf[176+n*2:178+n*2]))
                            driver.get("https://www.google.com/maps/?q=%f,%f"%(gpsla(txbuf[8:12]),gpslo(txbuf[12:16])))
                            self.txes.append(txbuf)
                        
                        
                            thisNow = datetime.datetime.now()
                            hour = thisNow.hour
                            min = thisNow.minute
                            sec = thisNow.second
                            timeStr = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
                        
                        
                            self.txTimes.append(timeStr)
                            txbuf=""
                    elif cmd=='AT+SBDRB':
                        print "Read RX buffer",
                        #self.send(chr(len(rxbuf)/256))
                        #self.send(chr(len(rxbuf)%256))
                        self.send(rxbuf)
                        csum=sum([ord(i) for i in rxbuf])
                        self.send(chr((csum&0xFF00)>>8))
                        self.send(chr(csum&0xFF))
                        self.send("\r\nOK\r\n")
                    elif cmd.startswith('AT+SBDWB='):
                        print "Write TX buffer (bin)"
                        tmblen=int(cmd.split('=')[1])+2
                        state=1
                        self.send("READY\r\n")
                    elif cmd.startswith('AT+SBDWT='):
                        print "Write TX buffer (text)"
                        txbuf=cmd[cmd.index('=')+1:]
                        self.send("OK\r\n")
                    cmd=""
                else:
                    cmd=cmd+c
    def send(self,msg):
        for i in msg:
            self.ser.write(i)
            time.sleep(0.01)
    def putmsg(self,msg):
        self.messages.put(msg)

with serial.Serial(sys.argv[1], 19200, timeout=1) as ser:

    thread1 = rbthread(ser)

    # Start new Threads
    thread1.start()

    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
        doRun=0

driver=webdriver.Chrome()
driver.set_page_load_timeout(60)

PORT_NUMBER = 8080

def o16(s):
    return ord(s[0])+ord(s[1])*256

def s16(s):
    os=o16(s)
    if os&0x8000:
        os=-(0x10000-os)
    return os

def o32(s):
    return ord(s[0])+ord(s[1])*256+ord(s[2])*256*256+ord(s[3])*256*256*256

def gpst(s):
    os=o32(s)
    h=os/10000
    m=(os/100)%100
    s=os%100
    return "%02d:%02d:%02d"%(h,m,s)
def gpsla(s):
    os=o32(s)
    n=False
    if os&0x80000000:
        n=True
    os&=0x7FFFFFFF
    d=os/1000000
    m=((os%1000000)/10000.0)/60
    print d,m
    return (d+m)*(-1 if n else 1)
def gpslo(s):
    os=o32(s)
    n=False
    if os&0x80000000:
        n=True
    os&=0x7FFFFFFF
    d=os/1000000
    m=((os%1000000)/10000.0)/60
    print d,m
    return (d+m)*(-1 if n else 1)
def gpsa(s):
    return o32(s)/10.0

def sanitize(s):
    o=""
    for i in xrange(len(s)):
        if s[i]=='\r':
            o=o+'\xEF\xBC\xB2'
        elif s[i]=='\n':
            o=o+'\xEF\xBC\xAE'
        elif ord(s[i])<32:
            o=o+'\xEF\xBC\x8A'
        else:
            o=o+s[i]
    return o

#rbdebug='\x00\x04\xf0\x9f\x8e\x88\x02\xa5'
rbdebug=''

thread1=None
#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if self.path=='/' or self.path.startswith('/?message='):
            if self.path.startswith('/?message='):
                msg=self.path.split('=')[1]
                msg=urllib.unquote(msg)
                print msg
                thread1.putmsg(msg)
            self.wfile.write("""
            <head>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
                <script>
                    function reloadmsg () {
                        $("#messages").load("messages.txt");
                        $('#messages').scrollTop($('#messages')[0].scrollHeight);
                        $("#messagesh").load("messages.hex");
                        $('#messagesh').scrollTop($('#messagesh')[0].scrollHeight);
                    }
                </script>
            </head>
            <body onload="setInterval(reloadmsg,1000)">
            <form accept-charset="UTF-8"><textarea cols=80 rows=30 id="messages">Messages</textarea><textarea cols=120 rows=30 id="messagesh">Messages</textarea></form>
            <form accept-charset="UTF-8" action="/" method="get"><input type="text"name="message"/><input type="submit"/></form>
            </body>
            """)
            
            
        #h2 does not work
        #v1 does not work
        #v2 does not work
        if self.path=='/messages.txt':
            for i,Eee in zip(thread1.txes,thread1.txTimes):
                self.wfile.write("V:%02x Y:%02x S:%04x\n"%(ord(i[0]),ord(i[1]),o16(i[2:4])))
                self.wfile.write("T:%08x L:%08x L:%08x A:%08x\n"%(o32(i[4:8]),o32(i[8:12]),o32(i[12:16]),o32(i[16:20])))
                self.wfile.write("h1:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[20+n*2:22+n*2]))
                self.wfile.write("\n")
                self.wfile.write("h2:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[44+n*2:46+n*2]))
                self.wfile.write("\n")
                self.wfile.write("hD:")
                for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[68+n*2:70+n*2]))
                self.wfile.write("\n")
               
                if sys.argv[2] == "2":
                  self.wfile.write("v1:%04x v2:%04x vD:%04x\n"%(o16(i[92:94]),o16(i[94:96]),o16(i[96:98])))
                  self.wfile.write("cX:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[98+n*2:100+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cY:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[122+n*2:124+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CH:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[146+n*2:148+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CL:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[176+n*2:178+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("SUP:%08x\n"%(o32(i[206:210])))
                  self.wfile.write("BALL:%02x\n"%(ord(i[210])));
                  self.wfile.write("CUT:%02x\n"%(ord(i[211])));
                  self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                if sys.argv[2] == "3" or sys.argv[2] == "4":
                  self.wfile.write("v1:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[92+n*2:94+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("v2:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[116+n*2:118+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("vD:")
                  for n in xrange(12):
                    self.wfile.write("%04x,"%o16(i[140+n*2:142+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cX:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[164+n*2:166+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cY:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[188+n*2:190+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("cZ:")
                  for n in xrange(12):
                      self.wfile.write("%04x,"%o16(i[212+n*2:214+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CH:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[236+n*2:238+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("CL:")
                  for n in xrange(15):
                      self.wfile.write("%04x,"%o16(i[266+n*2:268+n*2]))
                  self.wfile.write("\n")
                  self.wfile.write("SUP:%08x\n"%(o32(i[296:300])))
                  self.wfile.write("BALL:%02x\n"%(ord(i[300])));
                  self.wfile.write("CUT:%02x\n"%(ord(i[301])));
                  self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                
        if self.path=='/messages.hex':
            for i,Eee in zip(thread1.txes,thread1.txTimes):
                for j in xrange(0,len(i),24):
                    for k in i[j:j+24]:
                        self.wfile.write("%2x"%ord(k))
                    self.wfile.write('\n')
                self.wfile.write(Eee+'-'*((24*4)-8)+'\n')
                
                
        return

doRun=1

class rbthread(threading.Thread):
    def __init__(self,ser):
        threading.Thread.__init__(self)
        self.ser=ser
        self.messages=Queue.Queue()
        self.txes=[]
        self.txTimes=[]
    def run(self):
        cmd=""
        echo=False
        momsn=0
        mtmsn=0
        rxbuf=""
        txbuf=""
        state=0
        tmblen=0
        while doRun:
            c=self.ser.read()
            if c:
                print str(repr(c))[1:-1],
            if echo:
                self.ser.write(c)
            if state==1:
                if c:
                    tmblen-=1
                    if tmblen>1:
                        txbuf=txbuf+c
                    elif tmblen==1:
                        csum=ord(c)<<8
                    elif tmblen==0:
                        csum|=ord(c)
                        print repr(txbuf)
                        print "Calculated:",hex(sum([ord(i) for i in txbuf]))
                        print "Received:",hex(csum)
                        self.send("OK\r\n")
                        state=0
                        continue
            if state==0:
                if c=='\r':
                    self.send("\r\n")
                    if cmd=='!Init\'d':
                        #raw_input('========BREAK========');
                        print
                    elif len(cmd)>0 and cmd[0]=='!':
                        print
                        pass
                    if cmd=='ATE1':
                        print "Echo on"
                        echo=True
                        self.send("OK\r\n")
                    if cmd=='ATE0':
                        print "Echo off"
                        echo=False
                        self.send("OK\r\n")
                        self.txes.append('\xEE'*340)
                        
                        
                        thisNow = datetime.datetime.now()
                        hour = thisNow.hour
                        min = thisNow.minute
                        sec = thisNow.second
                        timeStr = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
                        
                        
                        self.txTimes.append(timeStr)
                    elif cmd=='AT&K0':
                        print "Flow control off"
                        self.send("OK\r\n")
                    elif cmd=='AT':
                        print "AT command"
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDMTA=0':
                        print "Ringer off"
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDD0':
                        print "RX buffer clear"
                        self.rxbuf=""
                        self.send("OK\r\n")
                    elif cmd=='AT+SBDIX':
                        print "Transaction running"
                        time.sleep(1)
                        self.send("+SBDIX,0,")
                        self.send(str(momsn))
                        self.send(",")
                        try:
                            rxbuf=self.messages.get(False)
                            self.send("1,")
                            self.send(str(mtmsn))
                            self.send(',')
                            self.send(str(len(rxbuf)))
                            self.send(',')
                            self.send(str(self.messages.qsize()))
                            self.send('\r\n')
                            mtmsn+=1
                        except Queue.Empty:
                            self.send("0,0,0,0\r\n")
                        self.send("OK\r\n")
                        momsn+=1

                        if txbuf:
                            hecksPacket = "".join(["{:02x}".format(ord(c)) for c in txbuf])
                            try:
                              r = requests.post("http://gec.calamityconductor.com/post/", data={'data': hecksPacket ,'transmit_time' : '19-12-12 12:12:12', 'imei' : 999999999999999, 'momsn' : momsn, 'iridium_latitude' : 47.3867, 'iridium_longitude' : -122.1501, 'iridium_cep' : 0.0})
                              print(r.status_code, r.reason)
                            except:
                              pass
                        
                            try:
                              with open(os.path.join("packets","packet.%d.%d.bin"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                f.write(txbuf)
                              try:
                                with open(os.path.join("packets","packetHTML.%d.%d.html"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                  f.write(r.text)
                              except:
                                pass
                            except:
                              os.mkdir("packets")
                              with open(os.path.join("packets","packet.%d.%d.bin"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                f.write(txbuf)
                              try:
                                with open(os.path.join("packets","packetHTML.%d.%d.html"%(time.time(),o16(txbuf[2:4]))),'wb') as f:
                                  f.write(r.text)
                              except:
                                pass
                            with open("packets.csv",'a') as f:
                                f.write('%f,%d,%d,%d,'%(time.time(),ord(txbuf[0]),ord(txbuf[1]),o16(txbuf[2:4])))
                                f.write('%s,%f,%f,%f,'%(gpst(txbuf[4:8]),gpsla(txbuf[8:12]),gpslo(txbuf[12:16]),gpsa(txbuf[16:20])))
                                f.write('%d,%d,%d,%d\n'%(o16(txbuf[92:94]),o16(txbuf[94:96]),o16(txbuf[96:98]),o32(txbuf[206:210])))
                            with open("meas.csv",'a') as f:
                                for n in xrange(12):
                                    f.write("%f,%d,%d,"%(time.time(),o16(txbuf[2:4]),n))
                                    f.write("%d,"%o16(txbuf[20+n*2:22+n*2]))
                                    f.write("%d,"%o16(txbuf[44+n*2:46+n*2]))
                                    f.write("%d,"%o16(txbuf[68+n*2:70+n*2]))
                                    f.write("%d,"%s16(txbuf[98+n*2:100+n*2]))
                                    f.write("%d\n"%s16(txbuf[122+n*2:124+n*2]))
                            with open("cond.csv",'a') as f:
                                for n in xrange(15):
                                    f.write("%f,%d,%d,"%(time.time(),o16(txbuf[2:4]),n))
                                    f.write("%d,"%o16(txbuf[146+n*2:148+n*2]))
                                    f.write("%d\n"%o16(txbuf[176+n*2:178+n*2]))
                            driver.get("https://www.google.com/maps/?q=%f,%f"%(gpsla(txbuf[8:12]),gpslo(txbuf[12:16])))
                            self.txes.append(txbuf)
                        
                        
                            thisNow = datetime.datetime.now()
                            hour = thisNow.hour
                            min = thisNow.minute
                            sec = thisNow.second
                            timeStr = str(hour).zfill(2) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
                        
                        
                            self.txTimes.append(timeStr)
                            txbuf=""
                    elif cmd=='AT+SBDRB':
                        print "Read RX buffer",
                        #self.send(chr(len(rxbuf)/256))
                        #self.send(chr(len(rxbuf)%256))
                        self.send(rxbuf)
                        csum=sum([ord(i) for i in rxbuf])
                        self.send(chr((csum&0xFF00)>>8))
                        self.send(chr(csum&0xFF))
                        self.send("\r\nOK\r\n")
                    elif cmd.startswith('AT+SBDWB='):
                        print "Write TX buffer (bin)"
                        tmblen=int(cmd.split('=')[1])+2
                        state=1
                        self.send("READY\r\n")
                    elif cmd.startswith('AT+SBDWT='):
                        print "Write TX buffer (text)"
                        txbuf=cmd[cmd.index('=')+1:]
                        self.send("OK\r\n")
                    cmd=""
                else:
                    cmd=cmd+c
    def send(self,msg):
        for i in msg:
            self.ser.write(i)
            time.sleep(0.01)
    def putmsg(self,msg):
        self.messages.put(msg)

with serial.Serial(sys.argv[1], 19200, timeout=1) as ser:

    thread1 = rbthread(ser)

    # Start new Threads
    thread1.start()

    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print 'Started httpserver on port ' , PORT_NUMBER

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
        doRun=0
