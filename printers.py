#!/usr/bin/env python
# Output formatters (for printing info and data files)
#
# Copyright (C) 2014 Peter Wu <peter@lekensteyn.nl>

import math
from defs import info, data

# Python 2.7 compatibility
if b'' == '':
    import functools, itertools
    iterbytes = functools.partial(itertools.imap, ord)
else:
    iterbytes = iter

class BasePrinter(object):
    """Prints the info, data header or data in verbose form."""
    def __init__(self, filename):
        pass
    def print_info(self, t):
        print_namedtuple(t, info)
    def print_data_header(self, t):
        print_namedtuple(t, data)
    def print_data(self, t, date):
        print_namedtuple(t, data)

class RawPrinter(BasePrinter):
    """Prints raw bytes in hex form, possibly with headers."""
    def print_data(self, t, date):
        # Convert interpreted numbers back to bytes...
        all_bs = [data.pack_as_bytes(name, getattr(t, name))
            for name in data.names]
        # Convert bytes to hex and print them
        print(date + ' ' + ' '.join(
            ''.join('{0:02x}'.format(b) for b in iterbytes(bs))
                    for bs in all_bs))

class CSVPrinter(BasePrinter):
    """Prints data separated by a semicolon."""
    def __init__(self, filename, separator=','):
        self.separator = separator
        self.printed_header = False
    def print_data_header(self, t):
        pass
    def print_data(self, t, date):
        if not self.printed_header:
            print(self.separator.join(["timestamp"] + data.names))
            self.printed_header = True
        print('{1}{0}{2:5.1f}{0}{3:5.3f}{0}{4:5.3f}'
            .format(self.separator, date, *t))

class EffectivePowerPrinter(BasePrinter):
    """
    Prints the effective power in Watt, computed from voltage, current and the
    power factor.
    """
    def __init__(self, filename, separator=','):
        self.separator = separator
    def print_data_header(self, t):
        pass
    def print_data(self, t, date):
        effective_power = t.voltage * t.current * t.power_factor
        print('{1}{0}{2:.1f}'.format(self.separator, date, effective_power))

class ApparentPowerPrinter(BasePrinter):
    """Prints the calculated apparent power in VA."""
    def __init__(self, filename, separator=','):
        self.separator = separator
    def print_data_header(self, t):
        pass
    def print_data(self, t, date):
        apparent_power = t.voltage * t.current
        print('{1}{0}{2:.1f}'.format(self.separator, date, apparent_power))

def round_up(n, multiple):
    return int(math.ceil(1.0 * n / multiple) * multiple)

def print_namedtuple(t, formatter):
    # Align at columns of four chars with at least two spaces as separator
    name_width = round_up(max(len(name) for name in t._fields) + 2, 4)
    format = '{0:' + str(name_width) + '}{1}'

    for n, v in zip(t._fields, t):
        # Print literals in displayable characters
        if isinstance(v, bytes):
            v = repr(v)
        print(format.format(n, formatter.unitify(n, v)))

