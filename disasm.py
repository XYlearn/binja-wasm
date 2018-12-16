

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

WasmDisasm.add_handler(WasmDisasmHandler(
	"unreachable", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"block", 
	[{'attr_name': 'sig_type', 'type': 'Type', 'method': 'read_type'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"loop", 
	[{'attr_name': 'sig_type', 'type': 'Type', 'method': 'read_type'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"if", 
	[{'attr_name': 'sig_type', 'type': 'Type', 'method': 'read_type'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"else", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"select", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"br", 
	[{'attr_name': 'depth', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"br_if", 
	[{'attr_name': 'depth', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"br_table", 
	[{'attr_name': 'num_targets', 'type': 'Index', 'method': 'readu32_leb128'}, {'attr_name': 'target_depth', 'type': 'Index', 'method': 'readu32_leb128'}, {'attr_name': 'default_target_depth', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"return", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"nop", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"drop", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"end", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.const", 
	[{'attr_name': 'value', 'type': 'S32Leb128', 'method': 'reads32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.const", 
	[{'attr_name': 'value', 'type': 'S64Leb128', 'method': 'reads64_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.const", 
	[{'attr_name': 'value_bits', 'type': 'F32', 'method': 'readf32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.const", 
	[{'attr_name': 'value_bits', 'type': 'F64', 'method': 'readf64_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.const", 
	[{'attr_name': 'value_bits', 'type': 'V128', 'method': 'readu128_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"get_global", 
	[{'attr_name': 'global_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"get_local", 
	[{'attr_name': 'local_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"set_global", 
	[{'attr_name': 'global_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"set_local", 
	[{'attr_name': 'local_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"call", 
	[{'attr_name': 'func_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"call_indirect", 
	[{'attr_name': 'sig_index', 'type': 'Index', 'method': 'readu32_leb128'}, {'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"return_call", 
	[{'attr_name': 'func_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"return_call_indirect", 
	[{'attr_name': 'sig_index', 'type': 'Index', 'method': 'readu32_leb128'}, {'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"tee_local", 
	[{'attr_name': 'local_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.load8_s", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.load8_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.load16_s", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.load16_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load8_s", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load8_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load16_s", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load16_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load32_s", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load32_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.store8", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.store16", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.store8", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.store16", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.store32", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.size", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.grow", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.div_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.div_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.rem_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.rem_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.and", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.or", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.xor", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.rotr", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.rotl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.div_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.div_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.rem_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.rem_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.and", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.or", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.xor", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.rotr", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.rotl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.div", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.min", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.max", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.copysign", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.div", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.min", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.max", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.copysign", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.add_saturate_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.add_saturate_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.add_saturate_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.add_saturate_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.sub_saturate_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.sub_saturate_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.sub_saturate_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.sub_saturate_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.shl", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.shr_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.shr_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.and", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.or", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.xor", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.min", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.min", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.max", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.max", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.add", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.sub", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.div", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.div", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.mul", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.lt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.le_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.lt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.le_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.gt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.ge_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.gt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.ge_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.lt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.le_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.lt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.le_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.gt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.ge_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.gt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.ge_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.lt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.le", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.gt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.ge", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.lt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.le", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.gt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.ge", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.eq", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.ne", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.lt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.lt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.lt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.lt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.lt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.lt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.lt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.lt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.le_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.le_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.le_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.le_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.le_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.le_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.le", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.le", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.gt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.gt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.gt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.gt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.gt_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.gt_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.gt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.gt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.ge_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.ge_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.ge_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.ge_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.ge_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.ge_u", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.ge", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.ge", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.clz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.ctz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.popcnt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.clz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.ctz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.popcnt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.abs", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.ceil", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.floor", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.trunc", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.nearest", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.sqrt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.abs", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.ceil", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.floor", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.trunc", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.nearest", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.sqrt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.splat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.not", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.any_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.any_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.any_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.any_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.all_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.all_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.all_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.all_true", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.neg", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.abs", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.abs", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.sqrt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.sqrt", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v128.bitselect", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.extract_lane_s", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.extract_lane_u", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.extract_lane_s", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.extract_lane_u", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.extract_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.extract_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.extract_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.extract_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i8x16.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i16x8.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.replace_lane", 
	[{'attr_name': 'lane_val', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"v8x16.shuffle", 
	[{'attr_name': 'value', 'type': 'V128', 'method': 'readu128_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_s/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_s/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_u/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_u/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.wrap/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_s/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_s/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_u/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_u/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.extend_s/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.extend_u/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.convert_s/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.convert_u/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.convert_s/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.convert_u/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.demote/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32.reinterpret/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.convert_s/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.convert_u/i32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.convert_s/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.convert_u/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.promote/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64.reinterpret/i64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.reinterpret/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.reinterpret/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.eqz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.eqz", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.convert_s/i32x4", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f32x4.convert_u/i32x4", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.convert_s/i64x2", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"f64x2.convert_u/i64x2", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.trunc_s/f32x4:sat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32x4.trunc_u/f32x4:sat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.trunc_s/f64x2:sat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64x2.trunc_u/f64x2:sat", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"try", 
	[{'attr_name': 'sig_type', 'type': 'Type', 'method': 'read_type'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"catch", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"rethrow", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"throw", 
	[{'attr_name': 'index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"if_except", 
	[{'attr_name': 'sig_type', 'type': 'Type', 'method': 'read_type'}, {'attr_name': 'except_index', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.extend8_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.extend16_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.extend8_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.extend16_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.extend32_s", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_s:sat/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_u:sat/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_s:sat/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.trunc_u:sat/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_s:sat/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_u:sat/f32", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_s:sat/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.trunc_u:sat/f64", 
	[]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"atomic.wake", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.wait", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.wait", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.load8_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.load16_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.load8_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.load16_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.load32_u", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.load", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.store8", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.store16", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.store8", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.store16", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.store32", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.store", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.add", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.sub", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.and", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.or", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.xor", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.xchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw8_u.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i32.atomic.rmw16_u.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw8_u.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw16_u.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"i64.atomic.rmw32_u.cmpxchg", 
	[{'attr_name': 'alignment_log2', 'type': 'U32Leb128', 'method': 'readu32_leb128'}, {'attr_name': 'offset', 'type': 'U32Leb128', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"table.init", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}, {'attr_name': 'segment', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.init", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}, {'attr_name': 'segment', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.drop", 
	[{'attr_name': 'segment', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"table.drop", 
	[{'attr_name': 'segment', 'type': 'Index', 'method': 'readu32_leb128'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.copy", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"memory.fill", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))
WasmDisasm.add_handler(WasmDisasmHandler(
	"table.copy", 
	[{'attr_name': 'reserved', 'type': 'U8', 'method': 'readu8'}]))