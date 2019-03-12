import re
sizedict={
    'uint8_t':1,
    'uint16_t':2,
    'uint32_t':4,
    'sup_t':4
}

strdict={
    'uint8_t':'B',
    'uint16_t':'H',
    'uint32_t':'I',
    'sup_t':'4B'
}
def typ2siz(typ):
    if re.match("[a-zA-Z0-9_]*\[[0-9]*\]",typ):
        match=re.match("([a-zA-Z0-9_]*)\[([0-9]*)\]",typ)
        return sizedict[match.group(1)]*int(match.group(2))
    else:
        return sizedict[typ]

def typ2str(typ):
    if re.match("[a-zA-Z0-9_]*\[[0-9]*\]",typ):
        match=re.match("([a-zA-Z0-9_]*)\[([0-9]*)\]",typ)
        return match.group(2)+strdict[match.group(1)]
    else:
        return strdict[typ]    

with open("structure.def",'r') as f:
    with open("structure.py",'w') as of:
        _,version=f.readline().split(':')
        of.write("PACKET_VERSION=%s\n"%version.strip())
        start=0
        of.write("def unpack(f):\n")
        of.write("    values={}\n")
        for line in f:
            name,typ,desc=[i.strip() for i in line.split('|')]
            siz=typ2siz(typ)
            styp=typ2str(typ)
            of.write("    values['%s']=struct.unpack('<%s',f.read(%s))\n"%(name,styp,siz))
            start+=siz
        of.write('    return values\n')