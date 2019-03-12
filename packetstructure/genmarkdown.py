# -*- coding: utf-8 -*-

import re
sizedict={
    'uint8_t':1,
    'uint16_t':2,
    'uint32_t':4,
    'sup_t':4
}

def tocircle(num):
    circ=u"⓪①②③④⑤⑥⑦⑧⑨"
    s=""
    while num:
        s=circ[num%10]+s
        num/=10
    return s


def typ2siz(typ):
    if re.match("[a-zA-Z0-9_]*\[[0-9]*\]",typ):
        match=re.match("([a-zA-Z0-9_]*)\[([0-9]*)\]",typ)
        return sizedict[match.group(1)]*int(match.group(2))
    else:
        return sizedict[typ]

with open("structure.def",'r') as f:
    with open("structure.md",'w') as of:
        _,version=f.readline().split(':')
        of.write("# **Packet version:%s**\n"%(tocircle(int(version))).encode('utf-8'))
        start=0
        of.write("name | type | start | size | description\n")
        of.write("-----|------|-------|------|---------------\n")
        for line in f:
            name,typ,desc=[i.strip() for i in line.split('|')]
            siz=typ2siz(typ)
            of.write("%s | %s | %s | %s | %s\n"%(name,typ,start,siz,desc))
            start+=siz