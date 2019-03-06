"""
   DWF Python Example 3
   Author:  Digilent, Inc.
   Revision: 10/17/2013

   Requires:                       
       Python 2.7
"""

from ctypes import *
from dwfconstants import *
import time
import sys

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()



rgdSamples = (c_double*4096)()

currOutput = 1.0

for each in range(len(rgdSamples)):
    if (each%64 == 0):
        currOutput = -1.0 * currOutput
    rgdSamples[each] = currOutput

channel = c_int(0)



rgdSamples2 = (c_double*4096)()

currOutput = 1.0

for each in range(len(rgdSamples2)):
    if (each%128 == 0):
        currOutput = -1.0 * currOutput
    rgdSamples2[each] = currOutput

channel2 = c_int(1)



#print DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print "DWF Version: "+version.value

#open device
"Opening first device..."
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    print "failed to open device"
    quit()

print "Generating custom waveform 1..."
dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel, AnalogOutNodeCarrier, funcCustom) 
dwf.FDwfAnalogOutNodeDataSet(hdwf, channel, AnalogOutNodeCarrier, rgdSamples, c_int(4096))
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel, AnalogOutNodeCarrier, c_double(10000.0)) 
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel, AnalogOutNodeCarrier, c_double(1)) 
dwf.FDwfAnalogOutConfigure(hdwf, channel, c_bool(True))

print "Generating custom waveform 2..."
dwf.FDwfAnalogOutNodeEnableSet(hdwf, channel2, AnalogOutNodeCarrier, c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, channel2, AnalogOutNodeCarrier, funcCustom) 
dwf.FDwfAnalogOutNodeDataSet(hdwf, channel2, AnalogOutNodeCarrier, rgdSamples2, c_int(4096))
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, channel2, AnalogOutNodeCarrier, c_double(10000.0)) 
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, channel2, AnalogOutNodeCarrier, c_double(1)) 
dwf.FDwfAnalogOutConfigure(hdwf, channel2, c_bool(True))

print "Generating waveform for 10 seconds..."
time.sleep(10)
print "done."
dwf.FDwfDeviceCloseAll() 
