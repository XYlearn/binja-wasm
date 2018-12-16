#-*- coding: utf-8 -*-

class ValueDefinition:
    str_val_dict = {}
    val_str_dict = {}
    @classmethod
    def get(cls, data):
        if not cls.val_str_dict:
            cls.val_str_dict = dict(zip(cls.str_val_dict.values(), cls.str_val_dict.keys()))
        if type(data) == str:
            return cls.str_val_dict.get(data)
        else:
            return cls.val_str_dict.get(data)

class SectionType(ValueDefinition):
    str_val_dict = {
        "name_section" : 0,
        "type_section" : 1,
        "import_section" : 2,
        "function_section" : 3,
        "table_section" : 4,
        "memory_section" : 5,
        "global_section" : 6,
        "export_section" : 7,
        "start_section" : 8,
        "elem_section" : 9,
        "code_section" : 10,
        "data_section" : 11,
        "invalid_section" : 12
    }

class TypeOpcode(ValueDefinition):
    str_val_dict = {
        "i32": 0x7f,
        'i64': 0x7e,
        'f32': 0x7d,
        'f64': 0x7c,
        'anyfunc': 0x70,
        'func': 0x60,
        'empty_block_type': 0x40
    }

class ExternalKind(ValueDefinition):
    str_val_dict = {
        "Function": 0,
        'Table': 1,
        'Memory': 2,
        'Global': 3
    }

class InitExprOp(ValueDefinition):
    str_val_dict = {
        "i32.const": 0x41,
        "i64.const": 0x42,
        "f32.const": 0x43,
        "f64.const": 0x44,
        "v128.const": 0xfd,
        "get_global": 0x23,
        "end": 0x0b
    }

class NameType(ValueDefinition):
    str_val_dict = {
        'module': 0,
        'function': 1,
        'local': 2
    }