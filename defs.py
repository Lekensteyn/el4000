#!/usr/bin/env python
# Definitions for Voltcraft Energy Logger binary files
#
# Copyright (C) 2014 Peter Wu <peter@lekensteyn.nl>

from Format import Format, Float10, Float100, Float1000, BCDFloat

# Specification is available at
# http://wiki.td-er.nl/index.php?title=Energy_Logger_3500
# http://www2.produktinfo.conrad.com/datenblaetter/125000-149999/125323-da-01-en-Datenprotokoll_SD_card_file_Formatv1_2.pdf

# common fields for Info and Setup
def _add_date_time_fields(formatter, prefix=''):
    formatter.add_number(1, prefix + 'time_hour',   values=range(0, 23))
    formatter.add_number(1, prefix + 'time_minute', values=range(0, 59))
    formatter.add_number(1, prefix + 'date_month',  values=range(1, 12))
    formatter.add_number(1, prefix + 'date_day',    values=range(1, 31))
    formatter.add_number(1, prefix + 'date_year',   values=range(0, 99))

info = Format('Info')
info.add_literal(b'INFO:', 'header_magic')
info.add_number(3, 'total_power_consumption',   type=Float1000, unit='kWh')
info.add_number(3, 'total_recorded_time',       type=Float100,  unit='h')
info.add_number(3, 'total_on_time',             type=Float100,  unit='h')
for day in range(0, 10):
    name = 'total_kwh_today_min_{0}'.format(day)
    info.add_number(3, name,                    type=Float1000, unit='kWh')
for day in range(0, 10):
    name = 'total_recorded_time_today_min_{0}'.format(day)
    info.add_number(2, name,                    type=Float100,  unit='h')
for day in range(0, 10):
    name = 'total_on_time_today_min_{0}'.format(day)
    info.add_number(2, name,                    type=Float100,  unit='h')
info.add_number(1, 'unit_id',                   values=range(0, 9))
info.add_number(4, 'tariff1',                   type=BCDFloat)
info.add_number(4, 'tariff2',                   type=BCDFloat)
_add_date_time_fields(info, 'init_')
info.add_literal(4 * b'\xFF', 'end_of_file_code')
info.build(102)


data_hdr = Format('DataHeader')
STARTCODE = b'\xe0\xc5\xea'
data_hdr.add_literal(STARTCODE, 'startcode')
# "Date of recording" MM/DD/YY
data_hdr.add_number(1, 'record_month',          values=range(1, 12))
data_hdr.add_number(1, 'record_day',            values=range(1, 31))
data_hdr.add_number(1, 'record_year',           values=range(0, 99))
# "Time of recording" HH:MM
data_hdr.add_number(1, 'record_hour',           values=range(0, 23))
data_hdr.add_number(1, 'record_minute',         values=range(0, 59))
data_hdr.build(8)


data = Format('Data')
# Average voltage, average current, power factor (cos(phi))
data.add_number(2, 'voltage',       type=Float10,   unit='V',
                # Arbitrary values for sanity.
                values=range(2100, 2500))
data.add_number(2, 'current',       type=Float1000, unit='A',
                # While permitted, 920 Watt is quite rare, so assume invalid.
                values=range(0, 4000))
data.add_number(1, 'power_factor',  type=Float100)
data.build(5)


# save as 'setupel3.bin' (lowercase)
setup = Format('Setup')
SETUP_MAGIC = b'\xb8\xad\xf2'
setup.add_literal(SETUP_MAGIC, 'header_magic')
setup.add_number(1, 'unit_id',      values=range(0, 9))
setup.add_number(1, 'hour_format',  values=[1, 2]) # 1 = 12h, 2 = 24h
setup.add_number(1, 'date_format',  values=[1, 2]) # 1 = mm/dd/yy, 2 = dd/mm/yy
_add_date_time_fields(setup)
setup.add_number(1, 'currency',     values=[1, 2, 4, 8]) # pound, SFr, dollar, euro
setup.add_number(4, 'tariff1',      type=BCDFloat)
setup.add_number(4, 'tariff2',      type=BCDFloat)
setup.build(20)

# Unused for now, it is supposed to interpret file names
def decode_filename(name):
    name = name.upper()
    if not (name[0] >= 'A' and name[0] <= 'J'):
        raise ValueError('Invalid name {0}'.format(name))
    unit_id = ord(name[0]) - 'A'
    # seconds since some time
    time_date = int(name[1:], 16)
    return name, time_date
