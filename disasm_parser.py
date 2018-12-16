from waop import WasmOpcode
import re

read_types = {
    "Type":      "read_type",
    "Index":     "readu32_leb128",
    "S32Leb128": "reads32_leb128",
    "S64Leb128": "reads64_leb128",
    "U32Leb128": "readu32_leb128",
    "U64Leb128": "readu64_leb128",
    "F32":       "readf32_leb128",
    "F64":       "readf64_leb128",
    "V128":      "readu128_leb128",
    "U8":        "readu8"
}

header = '''

# -*- coding: utf-8 -*-
"""
Generated from wabt/src/binary-reader.cc
"""
from .waop import WasmOpcode
from .utils import State, SimBv

class WasmDisasm:
    opcode_handlers = {}

    @classmethod
    def disasm(cls, data, addr):
        op = WasmOpcode.get_by_bytes(data)
        if not op:
            return None
        handler = cls.get_handler(op.name)
        return handler.handle(data, addr)

    @classmethod
    def add_handler(cls, handler):
        cls.opcode_handlers[handler.mnem] = handler

    @classmethod
    def get_handler(cls, mnem):
        return cls.opcode_handlers[mnem]

class WasmDisasmHandler:
    def __init__(self, mnem, operands):
        self.mnem = mnem
        self.operands = operands

    def handle(self, data, addr):
        try:
            op = WasmOpcode.get_by_bytes(data)
            mnme = op.name
            if mnme != self.mnem:
                return None
            bv = SimBv(data)
            state = State(bv)
            op_length = WasmOpcode.get_op_length(data)
            size = op_length
            state.seek(op_length)
            res_operands = []
            for operand in self.operands:
                res_operand = operand.copy()
                res_operand['value'], n = eval("state." + operand['method'] + "(get_size=True)")
                res_operands.append(res_operand)
                size += n
            return WasmDisasmRes(self.mnem, res_operands, size)
        except:
            return None

class WasmDisasmRes:
    def __init__(self, mnem, operands, size):
        self.mnem = mnem
        self.operands = operands
        self.size = size

    def __str__(self):
        text = "{}	".format(self.mnem)
        operands_num = len(self.operands)
        for i in range(operands_num):
            operand = self.operands[i]
            text += str(operand['value'])
            if i != operands_num - 1:
                text += ", "
        return text

'''

handler_template = 'WasmDisasm.add_handler(WasmDisasmHandler(\n\t"{}", \n\t{}))'

def read_content(filename):
    with open(filename) as f:
        return f.read()

def write_content(filename, content):
    with open(filename, "w+") as f:
        f.write(content)

def get_func_range(content, start, end):
    decl_line = 'Result BinaryReader::ReadFunctionBody(Offset end_offset) {'
    ret_line = 'return Result::Ok;'
    func_start = content.find(decl_line)
    retrun_off = content.find(ret_line, func_start)
    func_end = content.find("}", retrun_off) + 1
    return func_start, func_end

def get_first_case_offset(content, start, end):
    return content.find("case", start, end)

def get_cases_block_range(content, start, end):
    first_case = content.find("case", start, end)
    break_off = content.find("break", start, end)
    block_end = break_off + len("break;")
    return first_case, block_end

def parse_opcode_names(content, start, end):
    pattern = re.compile(r"case\s+Opcode::(\w+)\s*:")
    names = []
    for sig in pattern.finditer(content[start: end]):
        sig = sig.group(1)
        name = WasmOpcode.get_by_sig(sig).name
        if not name:
            print("Invalid sig {}".format(sig))
            continue
        else:
            names.append(name)
    return names

def parse_opcode_operands(content, start, end):
    pattern = re.compile(r"Read(Type|Index|S32Leb128|S64Leb128|U32Leb128|U64Leb128|F32|F64|V128|U8)\(&(\w+)\s*,")
    operands = []
    for matcher in pattern.finditer(content[start: end]):
        read_type = matcher.group(1)
        attr_name = matcher.group(2)
        operand = {
            "type": read_type,
            "method": read_types.get(read_type),
            "attr_name": attr_name
        }
        operands.append(operand)
    return operands

def get_disasm_code(opcode_names, operands):
    pass 

def get_disasm_py_from(filename):
    content = read_content(filename)
    func_start, func_end = get_func_range(content, 0, len(content))
    block_start = get_first_case_offset(content, func_start, func_end)
    count = 0
    pycontent = header
    lines = []
    while True:
        block_start, block_end = get_cases_block_range(content, block_start, func_end)
        if block_start == -1:
            break
        count += 1
        opcode_names = parse_opcode_names(content, block_start, block_end)
        operands = parse_opcode_operands(content, block_start, block_end)
        for mnem in opcode_names:
            line = handler_template.format(mnem, operands)
            lines.append(line)
        block_start = block_end
    print("{} type of opcode parsed".format(count))
    return pycontent + '\n'.join(lines)

def main():
    pycontent = get_disasm_py_from("./binary-reader.cc")
    write_content("./disasm.py", pycontent)

if __name__ == "__main__":
    main()