#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import threading
import time
import serial
import sys
import Queue
PORT_NUMBER = 8080


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
                print msg
                thread1.putmsg(msg)
            self.wfile.write("""
            <head>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
                <script>
                    function reloadmsg () {
                        $("#messages").load("messages.txt");
                        $('#messages').scrollTop($('#messages')[0].scrollHeight);

                    }
                </script>
            </head>
            <body onload="setInterval(reloadmsg,1000)">
            <textarea cols=80 rows=15 id="messages">Messages</textarea>
            <form action="/" method="get"><input type="text"name="message"/><input type="submit"/></form>
            </body>
            """)
        if self.path=='/messages.txt':
            for i in thread1.txes:
                self.wfile.write(i+'\n')
        return

doRun=1

class rbthread(threading.Thread):
    def __init__(self,ser):
        threading.Thread.__init__(self)
        self.ser=ser
        self.messages=Queue.Queue()
        self.txes=[]
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
                        print hex(csum)
                        print txbuf
                        state=0
                        continue
            if state==0:
                if c=='\r':
                    self.send("\r\n")
                    if cmd=='ATE1':
                        print "Echo on"
                        echo=True
                        self.send("OK\r\n")
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
                        time.sleep(5)
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
                            self.txes.append(txbuf)
                            txbuf=""
                    elif cmd=='AT+SBDRB':
                        print "Read RX buffer"
                        self.send(chr(len(rxbuf)/256))
                        self.send(chr(len(rxbuf)%256))
                        self.send(rxbuf)
                        csum=sum([ord(i) for i in rxbuf])
                        self.send(chr((csum/256)%256))
                        self.send(chr(csum%256))
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
        self.ser.write(msg)
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