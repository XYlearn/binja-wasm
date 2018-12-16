import binaryninja
import struct
from .loader import WamsLoader
from .utils import *
from .waop import WasmOpcode, max_mnem_length
from .disasm import WasmDisasm

class Wasm(binaryninja.Architecture):
    name = "wasm"

    regs = {
        "sp": binaryninja.RegisterInfo('sp', 4)
    }

    max_instr_length = 2 + 19 * 3

    stack_pointer = 'sp'


    # def assemble(self, code, addr=0):
    #     pass

    def get_instruction_info(self, data, addr):
        instr = WasmDisasm.disasm(data, addr)
        ins_info = binaryninja.InstructionInfo()
        ins_info.length = instr.size
        return ins_info

    def get_instruction_text(self, data, addr):
        instr = WasmDisasm.disasm(data, addr)
        mnem = instr.mnem + " " * max_mnem_length
        operands = list(map(lambda operand: hex(operand['value']), instr.operands))
        return [mnem].extend(operands), instr.size

    # def get_instruction_low_level_il(self, data, addr, il):
    #     return None

    def is_never_branch_patch_available(self, data, addr):
        return False

    def is_always_branch_patch_available(self, data, addr):
        return False

    def is_invert_branch_patch_available(self, data, addr):
        return False

    def is_skip_and_return_zero_patch_available(self, data, addr):
        return False

    def is_skip_and_return_value_patch_available(self, data, addr):
        return False

    # def convert_to_nop(self, data, addr):
    #     pass

    # def always_branch(self, data, addr):
    #     pass

    # def invert_branch(self, data, addr):
    #     pass

    # def skip_and_return_value(self, data, addr, value):
    #     pass


class WasmBinaryView(binaryninja.BinaryView):
    name = 'wasm'
    long_name = "wasm Binary View"

    def __init__(self, data):
        binaryninja.BinaryView.__init__(self, parent_view=data, file_metadata=data.file)
        self.loader = None
        self.arch = binaryninja.Architecture['wasm']
        self.platform = binaryninja.Architecture['wasm'].standalone_platform
        data.arch = binaryninja.Architecture['wasm']
        data.platform = binaryninja.Architecture['wasm'].standalone_platform
        self.loader = WamsLoader(data)

    def init(self):
        self.loader.load()

    def is_executable(self):
        return True

    @classmethod
    def is_valid_for_data(self, data):
        return WamsLoader.is_valid_for_data(data)
        
Wasm.register()
WasmBinaryView.register()
