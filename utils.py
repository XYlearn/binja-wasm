import struct
import ctypes
# from binaryninja import log_debug
from .definition import TypeOpcode

MASK7 = 0x7f
MASK8 = 0xff
MASK16 = 0xffff
MASK32 = 0xffffffff
MASK64 = 0xffffffffffffffff
MASK128 = 0xffffffffffffffffffffffffffffffff
LEB128_NEXT = 0x80

def u8(data):
    assert(len(data) >= 1)
    return struct.unpack("B", data[:1])[0]

def u16(data, little_endian=True):
    assert(len(data) >= 2)
    if little_endian:
        return struct.unpack("<H", data[:2])[0]
    else:
        return struct.unpack(">H", data[:2])[0]


def u32(data, little_endian=True):
    assert(len(data) >= 4)
    if little_endian:
        return struct.unpack("<I", data[:4])[0]
    else:
        return struct.unpack(">I", data[:4])[0]


def u64(data, little_endian=True):
    assert(len(data) >= 8)
    if little_endian:
        return struct.unpack("<Q", data[:4])[0]
    else:
        return struct.unpack(">Q", data[:4])[0]


def p16(data, little_endian=True):
    if little_endian:
        return struct.pack("<H", data)
    else:
        return struct.pack(">H", data)


def p32(data, little_endian=True):
    if little_endian:
        return struct.pack("<I", data)
    else:
        return struct.pack(">I", data)


def p64(data, little_endian=True):
    if little_endian:
        return struct.pack("<Q", data)
    else:
        return struct.pack(">Q", data)

class State:
    def __init__(self, bv):
        self.bv = bv
        self.off = 0
        self.size = len(bv)

    def left_data(self):
        left = self.size - self.size
        if left <= 0:
            return 0
        else:
            return left

    def read(self, off, size):
        return self.bv.read(off, size)

    def read_next(self, n):
        if n > self.size - self.off:
            n = self.size - self.off
        nbytes = self.read(self.off, n)
        self.off += n
        return nbytes

    def seek(self, off):
        if off < self.size and off >= 0:
            self.off = off
            return True
        else:
            return False

    def seek_plus(self, plus):
        new_off = self.off + plus
        if new_off < self.size and new_off >= 0:
            self.off = new_off
            return True
        else:
            return False

    def read_leb128(self):
        val = 0
        n = 0
        while n + self.off < self.size:
            tmp = u8(self.read(self.off + n, 1))
            val |= tmp << (7 * n)
            n += 1
            if tmp & 0x80 == 0:
                break
        self.off += n
        return val, n
        

    def read_leb128n(self, n):
        assert(n < 20 and n > 0)
        
        if n == 1:
            tmp = u8(self.read_next(1))
            return tmp & MASK7, tmp & LEB128_NEXT
        else:
            tmp, flag = self.read_leb128n(n - 1)
            if flag == LEB128_NEXT:
                cur = u8(self.read_next(1))
                return (cur & MASK7) << ((n - 1) * 7) | tmp, cur & LEB128_NEXT
            else:
                # n is too large
                if not flag:
                    flag = n - 1
                return tmp, flag

    def readu32_leb128(self, get_size=False):
        val, n = self.read_leb128n(5)
        val = val & MASK32
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 5
            return val, n

    def readu64_leb128(self, get_size=False):
        val, n = self.read_leb128n(10)
        val = val & MASK64
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 10
            return val, n

    def readu128_leb128(self, get_size=False):
        val, n = self.read_leb128n(19)
        val = val & MASK128
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 19
            return val, n

    def reads32_leb128(self, get_size=False):
        val, n = self.read_leb128n(5)
        val &= MASK32
        sign_bit = 0x40 << (n - 1) * 7
        if val & sign_bit:
            val = ~val + 1
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 5
            return val, n
        
    def reads64_leb128(self, get_size=False):
        val, n = self.read_leb128n(10)
        val &= MASK64
        if n & LEB128_NEXT:
            n = 10
        sign_bit = 0x40 << (n - 1) * 7
        if val & sign_bit:
            val = ~val + 1
        if not get_size:
            return val
        else:
            return val, n

    def readf32_leb128(self, get_size=False):
        val, n = self.read_leb128n(5)
        val &= MASK32
        c_float = ctypes.cast(
            (ctypes.c_uint * 1)(val), 
            ctypes.POINTER(ctypes.c_float)
            ).contents
        val = c_float.value
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 5
            return val, n

    def readf64_leb128(self, get_size=False):
        val, n = self.read_leb128n(10)
        val &= MASK64
        c_double = ctypes.cast(
            (ctypes.c_ulong * 1)(val), 
            ctypes.POINTER(ctypes.c_double)
            ).contents
        val = c_double.value
        if not get_size:
            return val
        else:
            if n & LEB128_NEXT:
                n = 10
            return val, n

    def readu7_leb128(self, get_size=False):
        val, _ = self.read_leb128n(1)
        val &= MASK7
        if not get_size:
            return val
        else:
            return 1

    def readu1_leb128(self, get_size=False):
        val, _ = self.read_leb128n(1)
        val = val & 1
        if not get_size:
            return val
        else:
            return 1

    def readu8(self, get_size=False):
        val, _ = self.read_next(1)
        val = u8(val)
        if not get_size:
            return val
        else:
            return 1

    def read_until(self, end_bytes, drop=False):
        cur_start = 0
        step = 0x40
        bytes_read = b''
        while True:
            cur_bytes = self.read(self.off + cur_start, step)
            idx = cur_bytes.find(end_bytes)
            if idx < 0:
                cur_start += step
                bytes_read += cur_bytes
            else:
                break
        if drop:
            tail = cur_bytes[:idx]
        else:
            tail = cur_bytes[:idx + len(end_bytes)]
        bytes_read += tail
        return bytes_read

    def read_type(self, expected=None):
        type_op, _ = self.read_leb128n(1)
        type_str = TypeOpcode.get(type_op)
        if expected and type_str != expected:
            # log_debug("Expect type {} found type {}(0x{:02x}) at 0x{:x}".format(
            #     expected, type_str, type_op, state.off-1))
            type_str = expected
        return type_str

    def __len__(self):
        return len(self.bv)

class SimBv:
    def __init__(self, data):
        self.data = data

    def read(self, addr, size):
        data_len = len(self.data)
        if addr >= data_len or addr < 0:
            return b''
        exceed = addr + size - data_len
        if exceed > 0:
            return self.data[addr:]
        else:
            return self.data[addr: addr + size]

    def __len__(self):
        return len(self.data)