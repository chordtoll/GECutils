import re
sizedict={
    'uint8_t':1,
    'uint16_t':2,
    'uint32_t':4,
    'sup_t':4
}
def typ2siz(typ):
    if re.match("[a-zA-Z0-9_]*\[[0-9]*\]",typ):
        match=re.match("([a-zA-Z0-9_]*)\[([0-9]*)\]",typ)
        return sizedict[match.group(1)]*int(match.group(2))
    else:
        return sizedict[typ]

with open("structure.def",'r') as f:
    with open("structure.h",'w') as of:
        _,version=f.readline().split(':')
        of.write("#define PACKET_VERSION %s"%version)
        start=0
        of.write("struct __attribute__((packed)) s_packet_norm {\n")
        for line in f:
            name,typ,desc=[i.strip() for i in line.split('|')]
            siz=typ2siz(typ)
            of.write("\t%s %s; //%s\n"%(typ,name,desc))
            start+=siz
        of.write('};\n')