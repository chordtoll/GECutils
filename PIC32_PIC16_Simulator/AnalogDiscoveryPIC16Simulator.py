"""
   DWF Python Example 8
   Author:  Digilent, Inc.
   Revision: 10/17/2013

   Requires:                       
       Python 2.7
"""




"""
      PIC16  <->  PIC32         - FUNCTION

pin9  | RC7   -> pin5   | RE7   - PIC16_DATA1
pin8  | RC6   -> pin4   | RE6   - PIC16_DATA0
pin7  | RC3   -> pin99  | RE3   - PIC16_TxEnable
pin6  | RC4  <-  pin100 | RE4   - PIC32_CLK0
pin5  | RC5  <-  pin3   | RE5   - PIC32_CLK1
pin14 | RC2  <-  pin98  | RE2   - PIC32_TxEnable
pin15 | RC1  <-  pin94  | RE1   - PIC32_DATA1
pin16 | RC0  <-  pin93  | RE0   - PIC32_DATA0

            CLOCK (NOT CURRENTLY USED)
pin17 | RA2  <->  pin18  | RE8
"""




from ctypes import *
from dwfconstants import *
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
dwRead = c_uint32()

#print DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print "DWF Version: "+version.value

#open device
print "Opening first device"
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print szerr.value
    print "failed to open device"
    quit()

print "Preparing to read Digital IO pins..."

# enable output/mask on:
    #      PIC16  <->  PIC32         - FUNCTION
    #      
    #      pin9  | RC7   -> pin5   | RE7   - PIC16_DATA1
    #      pin8  | RC6   -> pin4   | RE6   - PIC16_DATA0
    #      pin7  | RC3   -> pin99  | RE3   - PIC16_TxEnable
    
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x00C8))

try:
    while True:
        # fetch digital IO information from the device 
        dwf.FDwfDigitalIOStatus(hdwf) 
        # read state of all pins, regardless of output enable
        dwf.FDwfDigitalIOInputStatus(hdwf, byref(dwRead))
        
        
        
        
except:
    print "We done now."




# set value on enabled IO pins
dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x12)) 


#print dwRead as bitfield (32 digits, removing 0b at the front)
print "Digital IO Pins:  " + bin(dwRead.value)[2:].zfill(32)

dwf.FDwfDeviceClose(hdwf)



