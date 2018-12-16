#-*- coding: utf-8 -*-
import json
import re

header = \
'''
# -*- coding: utf-8 -*-
"""
Generated from wabt/src/opcode.def
"""

# from binaryninja import 

def _u8(c):
    return ord(c)

class WasmOpcode:
    opcodes = {}
    val_opcodes = {}
    sig_opcodes = {}

    def __init__(self, name, tr, t1, t2, t3, m, prefix, code, signame):
        self.name = name
        self.tr = tr
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.m = m
        self.prefix = prefix
        self.code = code
        self.signame = signame

    def get_branch_type(self):
        return None

    @classmethod
    def add_opcode(cls, opcode):
        cls.opcodes[opcode.name] = opcode
        cls.val_opcodes[(opcode.prefix, opcode.prefix)] = opcode
        cls.sig_opcodes[opcode.signame] = opcode

    @classmethod
    def get_by_bytes(cls, data):
        if cls.get_op_length(data) == 2:
            first, second = _u8(data[0:1]), _u8(data[1:2])
            return cls.val_opcodes.get((first, second))
        else:
            first = _u8(data[0:1])
            return cls.val_opcodes.get((0, first))

    @classmethod
    def get_by_sig(cls, sig):
        return cls.sig_opcodes.get(sig)

    @classmethod
    def get_op_length(cls, data):
        first = _u8(data[0:1])
        if first >= 0xfc:
            return 2
        else:
            return 1

'''

type_pat = r'\s*(___|I32|I64|F32|F64|V128)\s*'
num_pat = r'\s*(?:0x)?([0-9a-fA-F]+)\s*'
str_pat = r'\s*([\w|/|:|.]+)\s*'
pattern = 'WABT_OPCODE\\({},{},{},{},{},{},{},{},\\s*\"{}\"\\)\\s*'.format(
        type_pat, type_pat, type_pat, type_pat, num_pat, num_pat, num_pat, str_pat, str_pat
    )
pattern = re.compile(pattern)

def valid_line(line):
    return line.startswith('WABT_OPCODE')

def do_parse_opcodes(reader):
    opcodes = []
    for line in reader:
        if not valid_line(line):
            continue
        opcode = get_opcode(line)
        opcodes.append(opcode)
    return opcodes

def parse_opcodes(filename):
    with open(filename, "r") as f:
        return do_parse_opcodes(f)

def get_type(s):
    if s == '___':
        return None
    else:
        return s

def get_opcode(line):
    line = line.strip()
    matcher = pattern.match(line)
    if not matcher:
        print("Parse error:{}".format(repr(line)))
        return None
    opcode = {
        "tr":   get_type(matcher.group(1).lower()),
        "t1":   get_type(matcher.group(2).lower()),
        "t2":   get_type(matcher.group(3).lower()),
        "t3":   get_type(matcher.group(4).lower()),
        "m":    int(matcher.group(5), 16),
        "prefix": int(matcher.group(6), 16),
        "code": int(matcher.group(7), 16),
        "name": matcher.group(9),
        "signame": matcher.group(8)
    }
    return opcode

def write_opcodes(filename, opcodes):
    pycontent = header
    max_len = max(map(lambda opcode: len(opcode['name']), opcodes))
    pycontent += 'max_mnem_length = {}\n'.format(max_len+1)
    pycontent += "#" + (len("WasmOpcode.add_opcode(WasmOpcode(") + int((max_len - 4) / 2)) * ' ' + \
        'name' + int(((max_len-4) / 2) + 4) * " " + "tr\t\tt1\t\tt2\t\tt3\t\tm\t\tprefix\tcode\tsigname\n"
    for opcode in opcodes:
        line = ("WasmOpcode.add_opcode(WasmOpcode({:"+str(max_len+2)+"s},\t{},\t{},\t{},\t{},\t{},\t{},\t{},\t{}))\n").format(
            repr(opcode['name']), repr(opcode['tr']), repr(opcode['t1']), repr(opcode['t2']), 
            repr(opcode['t3']), hex(opcode['m']), hex(opcode['prefix']), hex(opcode['code']),
            repr(opcode['signame'])
        )
        pycontent += line
    with open(filename, "w+") as f:
        f.write(pycontent)
    print("{} opcodes parsed".format(len(opcodes)))

if __name__ == "__main__":
    opcodes = parse_opcodes("./opcode.def")
    write_opcodes("./waop.py", opcodes)