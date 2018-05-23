import sys

def ddm2dd(ddm):
    ddm=float(ddm)
    d=int(ddm/100)
    dm=ddm-d*100
    return d+dm/60.0

with open(sys.argv[1],'rU') as f:
    for line in f:
        if line[0]!='\xca' and line!='\n':
            sentence=line.split(':')[4].rstrip().split(',')
            if sentence[0]=="$GPGGA":
                time=sentence[1]
                lat=ddm2dd(sentence[2])*(1 if sentence[3]=='N' else -1)
                lon=ddm2dd(sentence[4])*(1 if sentence[5]=='E' else -1)
            elif sentence[0]=='$GPRMC':
                time=sentence[1]
                lat=ddm2dd(sentence[3])*(1 if sentence[4]=='N' else -1)
                lon=ddm2dd(sentence[5])*(1 if sentence[6]=='E' else -1)
            print '%f, %f <default-dot>'%(lat,lon)
