#!/usr/bin/env python
# Helpers for interpreting binary data
#
# Copyright (C) 2014 Peter Wu <peter@lekensteyn.nl>

import struct
from collections import namedtuple
import logging

_logger = logging.getLogger(__name__)

class Format(object):
    """
    Helper around struct that provides named fields, conversion possibilities
    (by specifying a type) and validation possibilities.
    """
    def __init__(self, label):
        self.label = label
        self.struct = None
        self.names = []
        self.units = {}
        self.fmt = '!'
        self.field_structs = {}
        # Type that provides encoding and decoding methods
        self.value_types = {}
        # Names of fields which must be converted from byte to int
        self.int3s = []
        self.literals = {}
        # If a name exists, it is the complete set of allowed values (after
        # unpacking from file, but before type conversion)
        self.valid_values = {}

    def _add_field(self, name, field):
        if self.struct:
            raise RuntimeError('Already initialized')
        if name in self.names:
            raise ValueError('Duplicate field key {0}'.format(name))
        self.names.append(name)
        self.fmt += field
        self.field_structs[name] = struct.Struct('!' + field)

    def add_literal(self, data, name):
        field = '{0}s'.format(len(data))
        self._add_field(name, field)
        self.literals[name] = data

    def add_number(self, size, name, type=None, unit='', values=None):
        int_types = ['B', 'H', '3s', 'I']
        self._add_field(name, int_types[size - 1])
        if size == 3:
            self.int3s.append(name)
        if type:
            self.value_types[name] = type
        self.units[name] = unit if unit else ''
        if values:
            self.valid_values[name] = values

    def build(self, asserted_size):
        if self.struct:
            raise RuntimeError('Already initialized')
        new_struct = struct.Struct(self.fmt)
        if asserted_size != new_struct.size:
            raise RuntimeError('Size mismatch: {0} != {1}'
                .format(asserted_size, new_struct.size))
        # struct is passes the specification, save it!
        self.struct = new_struct
        self.factory = namedtuple(self.label, ' '.join(self.names))

    def unitify(self, name, value):
        if not self.struct:
            raise RuntimeError('Not initialized yet')
        if name in self.units:
            unit = self.units[name]
            if unit == 'h':
                mins = int((value % 1.0) * 60)
                return '{0}h {1:02}m'.format(int(value), mins)
            elif unit:
                return '{0} {1}'.format(value, unit)
        return str(value)

    def unpack_field(self, name, val, validate=True):
        # Handle ints made from 3 bytes
        if name in self.int3s:
            val, = struct.unpack('!I', b'\x00' + val)
        if validate:
            # Literals must exactly match
            if name in self.literals:
                if self.literals[name] != val:
                    raise RuntimeError('Literal mismatch: {0} != {1}'
                        .format(repr(self.literals[name]), val))
            # When reading from file, just warn
            if name in self.valid_values:
                if not val in self.valid_values[name]:
                    _logger.info('Garbage value found for {0}.{1}: {2}'
                        .format(self.label, name, val))
        # Convert value according to its type
        if name in self.value_types:
            val = self.value_types[name].decode(val)
        return val

    def pack_field(self, name, val):
        # Convert value according to its type
        if name in self.value_types:
            val = self.value_types[name].encode(val)

        # Literals must match exactly, ignore given value
        if name in self.literals:
            val = self.literals[name]
        else:
            # pack works with integers, not floats.
            val = int(val)

        # Validate new data
        if name in self.valid_values:
            if not val in self.valid_values[name]:
                _logger.warn('Invalid value {0} for name {1}'
                    .format(val, name))

        # Numbers of 3 bytes are stored as bytes
        if name in self.int3s:
            val = struct.pack('!I', val)[-3:]
        return val

    def pack_as_bytes(self, name, val):
        num = self.pack_field(name, val)
        return self.field_structs[name].pack(num)

    def unpack(self, data, validate=True):
        """
        Interprets the data according to this format, optionally with data
        validation.
        """
        if not self.struct:
            raise RuntimeError('Not initialized yet')

        res = self.struct.unpack(data)
        unpacked_bytes = []
        for name, val in zip(self.names, res):
            unpacked_bytes.append(self.unpack_field(name, val, validate))

        return self.factory._make(unpacked_bytes)

    def pack(self, t):
        """
        Formats the contents of a named tuple or dict according to this format.
        """
        if not self.struct:
            raise RuntimeError('Not initialized yet')

        vals = []
        for name in self.names:
            if isinstance(t, dict):
                val = t[name]
            else:
                val = getattr(t, name)
            vals.append(self.pack_field(name, val))

        return self.struct.pack(*vals)

    def parse_from_file(self, f):
        data = f.read(self.size())
        if not data:
            return None
        if len(data) != self.size():
            raise RuntimeError('Short data read: ' + len(data))
        return self.unpack(data)

    def size(self):
        if not self.struct:
            raise RuntimeError('Not initialized yet')
        return self.struct.size

# Types that reinterprets data for display.
# decode: file -> display; encode: display -> file
class Float10(object):
    """Interprets the number 1234 (read from file) as 123.4."""
    _factor = 10.0

    @classmethod
    def encode(cls, value):
        return int(value * cls._factor)

    @classmethod
    def decode(cls, value):
        return value / cls._factor

class Float100(Float10):
    """Interprets the number 1234 (read from file) as 12.34."""
    _factor = 100.0

class Float1000(Float10):
    """Interprets the number 1234 (read from file) as 1.234."""
    _factor = 1000.0

class BCDFloat(object):
    """Interprets the number 0x01020304 (read from file) as 1.234."""
    @staticmethod
    def encode(value):
        n = 0
        for i in range(0, 4):
            n += int(value / (10 ** -i) % 10) << (8 * (3 - i))
        return n

    @staticmethod
    def decode(value):
        n = 0
        for i in range(0, 4):
            n += ((value >> 8 * (3 - i)) & 0xFF) * (10 ** -i)
        return n
