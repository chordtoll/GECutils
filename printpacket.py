start=0
sizedict={'uint8_t':1,'uint16_t':2,'uint32_t':4,'sup_t':4}

with open("packet.format",'r') as f:
    for line in f:
        line=line.lstrip().rstrip().rstrip(';')
        line=line.rstrip(';')
        type,rem=line.split(' ')
        name,ar=(rem.split('[') if '[' in rem else (rem,'1]'))
        ar=int(ar.rstrip(']'))
        size=sizedict[type]*ar
        print name,'|',type+('[%d]'%ar if ar>1 else ''),'|',start,'|',size
        start+=size
