import logging
import binaryninja
from binaryninja.log import *
from binaryninja import SegmentFlag, SectionSemantics
from .utils import *
from .definition import *

class WamsLoader:
    versions = [1]
    MAX_SECTION_COUNT = 12

    SEC_ID_NAME = 0
    SEC_ID_TYPE = 1
    SEC_ID_IMPORT = 2
    SEC_ID_FUNCTION = 3
    SEC_ID_TABLE = 4
    SEC_ID_MEMORY = 5
    SEC_ID_GLOBAL = 6
    SEC_ID_EXPORT = 7
    SEC_ID_START = 8
    SEC_ID_ELEM = 9
    SEC_ID_CODE = 10
    SEC_ID_DATA = 11
    SEC_ID_INVALID = 12

    def __init__(self, bv):
        self.bv = bv
        self.state = State(bv)
        self.version = 1
        self.meta = {}

    def load(self):
        state = self.state
        return self._load_modules(state)

    def _load_modules(self, state):
        if not self.is_valid_for_data(state):
            return False
        self.bv.add_auto_segment(
            0, len(state), 
            0, len(state),
            SegmentFlag.SegmentExecutable | SegmentFlag.SegmentReadable
        )
        self.version = u32(state.read(4, 4))
        state.seek(8)
        return self._load_sections(state)

    def _load_sections(self, state):
        while state.off < state.size:
            sec_id, _ = state.read_leb128n(1)
            if sec_id > self.MAX_SECTION_COUNT:
                log_info("Invalid Section id")
            if sec_id == self.SEC_ID_NAME:
                if state.read(state.off, 4) == b'name':
                    self._load_name_section(state)
                else:
                    log_info("Invalid name section")
            sec_size, _ = state.read_leb128n(5)
            sec_size &= MASK32
            if sec_size == 0:
                break
            elif sec_size > state.size:
                log_info("Section Size is too large")
            if sec_id == self.SEC_ID_TYPE:
                self._load_type_section(state, sec_size)
            elif sec_id == self.SEC_ID_IMPORT:
            	self._load_import_section(state, sec_size)
            elif sec_id == self.SEC_ID_FUNCTION:
                self._load_function_section(state, sec_size)
            elif sec_id == self.SEC_ID_TABLE:
                self._load_table_section(state, sec_size)
            elif sec_id == self.SEC_ID_MEMORY:
                self._load_memory_section(state, sec_size)
            elif sec_id == self.SEC_ID_GLOBAL:
                self._load_global_section(state, sec_size)
            elif sec_id == self.SEC_ID_EXPORT:
                self._load_export_section(state, sec_size)
            elif sec_id == self.SEC_ID_START:
                self._load_start_section(state, sec_size)
            elif sec_id == self.SEC_ID_ELEM:
                self._load_elem_section(state, sec_size)
            elif sec_id == self.SEC_ID_CODE:
                self._load_code_section(state, sec_size)
            elif sec_id == self.SEC_ID_DATA:
                self._load_data_section(state, sec_size)
            else:
                log_info("Invalid section")

    def _load_type_section(self, state, size):
        log_info("Load Type Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        signature_count = state.readu32_leb128()
        signatures = []
        for _ in range(signature_count):
            state.read_type('func')
            param_count = state.readu32_leb128()
            param_types = []
            for _ in range(param_count):
                param_types.append(self._read_type(state))
            return_count, _ = state.read_leb128n(1)
            if return_count:
                return_type = self._read_type(state)
            else:
                return_type = 'void'
            signature = {
                'param_count': param_count,
                'param_types': param_types,
                'return_count': return_count,
                'return_type': return_type
            }
            signatures.append(signature)
        self.meta['type_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'signature_count': signature_count,
            'signatures': signatures
        }
        log_info(str(self.meta['type_section']))
        state.seek(sec_end)
        self._do_load_type_section(self.meta)

    def _load_import_section(self, state, size):
        log_info("Load Import Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        entry_count = state.readu32_leb128()
        entries = []
        for _ in range(entry_count):
            module_len = state.readu32_leb128()
            module_str = state.read_next(module_len).decode('utf-8')
            field_len = state.readu32_leb128()
            field_str = state.read_next(field_len).decode('utf-8')
            kind = ExternalKind.get(state.read_next(1)[0])
            entry = {
                'module_len': module_len,
                'module_str': module_str,
                'field_len': field_len,
                'field_str': field_str,
                'kind': kind
            }
            entries.append(entry)
        self.meta['import_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'entry_count': entry_count,
            'entries': entries
        }
        log_info(str(self.meta['import_section']))
        state.seek(sec_end)
        self._do_load_import_section(self.meta)

    def _load_function_section(self, state, size):
        log_info("Load Function Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        function_count = state.readu32_leb128()
        functions = []
        function_count = state.readu32_leb128()
        for i in range(function_count):
            function = {
                'function_index': i + 1,
                'signature_index': state.readu32_leb128()
            }
            functions.append(function)
        self.meta['function_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'function_count': function_count,
            'functions': functions
        }
        log_info(str(self.meta['function_section']))
        state.seek(sec_end)
        self._do_load_function_section(self.meta)

    def _load_table_section(self, state, size):
        log_info("Load Table Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        entry_count = state.readu32_leb128()
        entries = []
        for _ in range(entry_count):
            element_type = self._read_type(state)
            limit_flag = state.readu1_leb128()
            initial = state.readu32_leb128()
            if limit_flag:
                maximum = state.readu32_leb128()
            else:
                maximum = -1 & MASK32
            limits = {
                "flag": limit_flag,
                "initial": initial,
                "maximum": maximum
            }
            entry = {
                "element_type": element_type,
                "limits": limits
            }
            entries.append(entry)
        self.meta['table_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'entry_count': entry_count,
            'entries': entries
        }
        log_info(str(self.meta['table_section']))
        state.seek(sec_end)
        self._do_load_table_section(self.meta)

    def _load_memory_section(self, state, size):
        log_info("Load Memory Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        entry_count = state.readu32_leb128()
        entries = []
        for _ in range(entry_count):
            limit_flag = state.readu1_leb128()
            initial = state.readu32_leb128()
            if limit_flag:
                maximum = state.readu32_leb128()
            else:
                maximum = -1 & MASK32
            limits = {
                "flag": limit_flag,
                "initial": initial,
                "maximum": maximum
            }
            entry = {
                "limits": limits
            }
            entries.append(entry)
        self.meta['memory_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'entry_count': entry_count,
            'entries': entries
        }
        log_info(str(self.meta['memory_section']))
        state.seek(sec_end)
        self._do_load_memory_section(self.meta)

    def _load_global_section(self, state, size):
        log_info("Load Global Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        global_count = state.readu32_leb128()
        entries = []
        for _ in range(global_count):
            content_type = self._read_type(state)
            mutabilaty = state.readu1_leb128()
            global_type = {
                "content_type": content_type,
                "mutabilaty": mutabilaty
            }
            init_expr = self._read_init_expr(state)
            entry = {
                "global_type": global_type,
                "init_expr": init_expr
            }
            entries.append(entry)
        self.meta['global_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'global_count': global_count,
            'globals': entries
        }
        log_info(str(self.meta['global_section']))
        state.seek(sec_end)
        self._do_load_global_section(self.meta)

    def _load_export_section(self, state, size):
        log_info("Load Export Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        export_count = state.readu32_leb128()
        entries = []
        for _ in range(export_count):
            field_len = state.readu32_leb128()
            field_str = state.read_next(field_len).decode('utf-8')
            kind = ExternalKind.get(state.read_next(1)[0])
            index = state.readu32_leb128()
            entry = {
                "field_len": field_len,
                "field_str": field_str,
                "kind": kind,
                "index": index
            }
            entries.append(entry)
        self.meta['export_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            "entry_count": export_count,
            "entries": entries
        }
        log_info(str(self.meta['export_section']))
        state.seek(sec_end)
        self._do_load_export_section(self.meta)

    def _load_start_section(self, state, size):
        log_info("Load Start Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        index = state.readu32_leb128()
        self.meta['start_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            "index": index
        }
        log_info(str(self.meta['start_section']))
        state.seek(sec_end)
        self._do_load_start_section(self.meta)

    def _load_elem_section(self, state, size):
        log_info("Load Elem Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        entry_count = state.readu32_leb128()
        entries = []
        for _ in range(entry_count):
            # parse elements
            index = state.readu32_leb128()
            offset = self._read_init_expr(state)
            num_ele = state.readu32_leb128()
            elems = []
            for _ in range(num_ele):
                elems.append(state.readu32_leb128())
            entry = {
                "index": index,       # the table index (0 in the MVP)
                "offset": offset,     # an i32 initializer expression that 
                                      # computes the offset at which to place 
                                      # the elements
                "num_ele": num_ele,
                "elems": elems
            }
            entries.append(entry)
        self.meta['elem_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            'entry_count': entry_count,
            "entries": entries
        }
        log_info(str(self.meta['elem_section']))
        state.seek(sec_end)
        self._do_load_elem_section(self.meta)
    
    def _load_code_section(self, state, size):
        log_info("Load Code Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        function_count = state.readu32_leb128()
        funcs = []
        for i in range(function_count):
            body_size = state.readu32_leb128()
            body_start = state.off
            body_end = state.off + body_size
            local_count = state.readu32_leb128()
            local_types = []
            total_count = 0
            while total_count < local_count:
                count = state.readu32_leb128()
                local_type = self._read_type(state)
                local = {
                    "count": count,
                    "type": local_type
                }
                local_types.append(local)
                total_count += count
            code = state.read_until(b'\x0b')
            func = {
                "size": body_size,
                "start": body_start,
                "end": body_end,
                'local_count': local_count,
                "locals": local_types,
                # "code": code
            }
            funcs.append(func)
        self.meta['code_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            "count": function_count,
            "funcs": funcs
        }
        log_info(str(self.meta['code_section']))
        state.seek(sec_end)
        self._do_load_code_section(self.meta)

    def _load_data_section(self, state, size):
        log_info("Load Data Section (size:{})".format(hex(size)))
        sec_start = state.off
        sec_end = state.off + size
        entry_count = state.readu32_leb128()
        entries = []
        for _ in range(entry_count):
            index = state.readu32_leb128()
            offset = self._read_init_expr(state)
            size = state.readu32_leb128()
            # data = state.read_next(size)[0]
            entry = {
                "index": index,
                "offset": offset,
                "size": size,
                # "data": data
            }
            entries.append(entry)
        self.meta['data_section'] = {
            'start': sec_start,
            'end': sec_end,
            'size': size,
            "count": entry_count,
            "entries": entries
        }
        log_info(str(self.meta['data_section']))
        state.seek(sec_end)
        self._do_load_data_section(self.meta)

    def _load_name_section(self, state):
        log_info("Load Type Section")
        sec_start = state.off
        name_sec = {
            'start': sec_start,
            'module': None,
            'function': None,
            'local': None
        }
        for i in range(3):
            if state.off >= state.size:
                break
            name_type = state.readu7_leb128()
            if name_type != i:
                info_log("Unexpted name subsection id {}".format(i))
            else:
                sub_size = state.readu32_leb128()
                if name_type == 0:
                    name_sec['module'] = \
                        self._load_module_name_subsection(state, sub_size)
                elif name_type == 1:
                    name_sec['function'] = \
                        self._load_function_name_subsection(state, sub_size)
                else:
                    name_sec['local'] = \
                        self._load_local_name_subsection(state, sub_size)
        log_info(str(self.meta['name_section']))
        self.meta['name_section'] = name_sec
        self._do_load_name_section(self.meta)

    def _load_module_name_subsection(self, state, size):
        name_len = state.readu32_leb128()
        name_str = state.read_next(name_len).decode('utf-8')
        module_name = {
            'name_len': name_len,
            "name_str": name_str
        }
        return module_name

    def _load_function_name_subsection(self, state, size):
        count = state.readu32_leb128()
        names = []
        for _ in range(count):
            index = state.readu32_leb128()
            name_len = state.readu32_leb128()
            name_str = state.read_next(name_len).decode('utf-8')
            name = {
                "index": index,
                "name_len": name_len,
                "name_str": name_str
            }
            names.append(name)
        function_names = {
            "count": count,
            "names": names
        }
        return function_names

    def _load_local_name_subsection(self, state, size):
        count = state.readu32_leb128()
        funcs = []
        for _ in range(count):
            function_index = state.readu32_leb128()
            local_count = state.readu32_leb128()
            names = []
            for _ in range(local_count):
                local_index = state.readu32_leb128()
                name_len = state.readu32_leb128()
                name_str = state.read_next(name_len).decode('utf-8')
                name = {
                    "index": local_index,
                    "name_len": name_len,
                    "name_str": name_str
                }
                names.append(name)
            local_map = {
                'count': local_count,
                'names': names
            }
            func = {
                "index": function_index,
                "local_map": local_map
            }
            funcs.append(func)
        local_names = {
            'count': count,
            "funcs": funcs
        }
        return local_names

    def _do_load_type_section(self, meta):
        sec_name = "type"
        sec_meta = meta['type_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_import_section(self, meta):
        sec_name = 'import'
        sec_meta = meta['import_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_function_section(self, meta):
        sec_name = 'function'
        sec_meta = meta['function_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_table_section(self, meta):
        sec_name = 'table'
        sec_meta = meta['table_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)
        
    def _do_load_memory_section(self, meta):
        sec_name = 'memory'
        sec_meta = meta['memory_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_global_section(self, meta):
        sec_name = 'global'
        sec_meta = meta['global_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_export_section(self, meta):
        sec_name = 'export'
        sec_meta = meta['export_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)
    
    def _do_load_start_section(self, meta):
        sec_name = 'start'
        sec_meta = meta['start_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)
        
    def _do_load_elem_section(self, meta):
        sec_name = 'elem'
        sec_meta = meta['elem_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_code_section(self, meta):
        sec_name = 'code'
        sec_meta = meta['code_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_data_section(self, meta):
        sec_name = 'data'
        sec_meta = meta['data_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _do_load_name_section(self, meta):
        sec_name = 'name'
        sec_meta = meta['name_section']
        start = sec_meta['start']
        length = sec_meta['size']
        self.bv.add_auto_section(sec_name, start, length)

    def _read_type(self, state, expected=None):
        type_op, _ = state.read_leb128n(1)
        type_str = TypeOpcode.get(type_op)
        if expected and type_str != expected:
            log_info("Expect type {} found type {}(0x{:02x}) at 0x{:x}".format(
                expected, type_str, type_op, state.off-1))
            type_str = expected
        return type_str

    def _read_init_expr(self, state):
        opcode = state.readu7_leb128()
        opcode = InitExprOp.get(opcode)
        dont_check_end = False
        if opcode == 'i32.const':
            value = state.readu32_leb128()
        elif opcode == 'i64.const':
            value = state.readu64_leb128()
        elif opcode == 'f32.const':
            value = state.readf32_leb128()
        elif opcode == 'f64.const':
            value = state.readf64_leb128()
        elif opcode == 'v128.const':
            value = state.readu128_leb128()
        elif opcode == 'get_global':
            value = state.readu32_leb128()
        elif opcode == 'end':
            value = None
            dont_check_end = True
        else:
            value = None
            dont_check_end = True
        init_expr = {
            'opcode': opcode,
            "value": value
        }
        if dont_check_end:
            return init_expr
        end_opcode = state.readu7_leb128()
        end_opcode = InitExprOp.get(end_opcode)
        if end_opcode != "end":
            log_info("Invalid end opcode {}".format(end_opcode))
        return init_expr

    

    @classmethod
    def is_valid_for_data(cls, state_or_bv):
        magic_bytes = state_or_bv.read(0, 4)
        if len(magic_bytes) < 4:
            return False
        if magic_bytes != b'\0asm':
            return False
        version_bytes = state_or_bv.read(4, 4)
        if len(version_bytes) < 4:
            return False
        version = u32(version_bytes)
        if version not in cls.versions:
            return False
        return True
        