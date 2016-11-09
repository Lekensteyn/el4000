# Energy Logger 4000 utility

This project provides a utility which can be used to read info and binary logs
from the Voltcraft Energy Logger 4000 as [sold by Conrad][conrad]. A setup file
(setupel3.bin) can also be read and written, this allows you to configure the
device via the SD card.

## Requirements

To use this program, you will need the following:

 - A Python interpreter (version 2 or 3). Almost all Linux distributions have
   this already installed. For Mac OS X and Windows users, see [Pythons download
   page][python].
 - (Recommended) A SecureDigital card to communicate with the EL4000. The EL4000
   manual recommends a 4 GB card which which works fine for me.
 - (Recommended) A Voltcraft Energy Logger 4000. It should also work with a
   EL3500 since it has the same file format, but I could not test this.

This program has been tested with a Voltcraft Energy Logger 4000F (with a French
power plug and a German adapter, bought via eBay) on a Dutch energy network.

## Usage

Since this program is a console application, you need to open a terminal (or
cmd) first. Available options:

    $ python el4000.py --help
    usage: el4000.py [-h] [-p {raw,base,watt,va,csv}] [-d DELIMITER] [-v]
                     [-s [key=value [key=value ...]]] [-o]
                     binfile [binfile ...]

    Energy Logger 4000 utility

    positional arguments:
      binfile               info or data files (.bin) from SD card. If --setup is
                            given, then this is the output file (and input for
                            defaults). The order of files are significant when a
                            timestamp is involved

    optional arguments:
      -h, --help            show this help message and exit
      -p {raw,base,watt,va,csv}, --printer {raw,base,watt,va,csv}
                            Output formatter (default 'base')
      -d DELIMITER, --delimiter DELIMITER
                            Output delimiter for CSV output (default ',')
      -v, --verbose         Increase logging level (twice for extra verbose)
      -s [key=value [key=value ...]], --setup [key=value [key=value ...]]
                            Process a setupel3.bin file. Optional parameters can
                            be given to set a field (-s unit_id=1 for example). If
                            no parameters are given, the current values are
                            printed

### Example: print time and watt as CSV

Given a data file `A0810702.BIN`, you can write a `results.csv` file with:

    $ python el4000.py -p csv A0810702.BIN > results.csv

Its content may look like:

    timestamp,voltage,current,power_factor
    2014-06-27 13:13,237.1,0.215,0.420
    2014-06-27 13:14,236.5,0.206,0.420
    2014-06-27 13:15,235.7,0.199,0.420
    2014-06-27 13:16,237.3,0.204,0.420
    ...

If you happen to see "1970-01-01" as timestamp, be sure to include the info
files (102 bytes) before others (and use `--data-only` to hide the contents of
this info file). Compare:

    $ python el4000.py -p csv A07EF88B.BIN
    timestamp,voltage,current,power_factor
    1970-01-01 00:00,238.5,0.000,0.000
    1970-01-01 00:01,239.5,0.000,0.000
    ...
    $ python el4000.py -p csv --data-only A07EF88A.BIN A07EF88B.BIN
    timestamp,voltage,current,power_factor
    2014-06-25 16:53,238.5,0.000,0.000
    2014-06-25 16:54,239.5,0.000,0.000
    ...

### Example: show information file

The information file is 102 bytes, its contents can be examined just like a data
file:

    $ python el4000.py A0810701.BIN
    header_magic                        b'INFO:'
    total_power_consumption             0.534 kWh
    total_recorded_time                 2119h 04m
    total_on_time                       2115h 15m
    total_kwh_today_min_0               0.1 kWh
    ...
    total_kwh_today_min_9               0.0 kWh
    total_recorded_time_today_min_0     3h 42m
    ...
    total_recorded_time_today_min_9     0h 00m
    total_on_time_today_min_0           3h 42m
    ...
    total_on_time_today_min_9           0h 00m
    unit_id                             0
    tariff1                             0.221
    tariff2                             0.227
    init_time_hour                      16
    init_time_minute                    53
    init_date_month                     6
    init_date_day                       25
    init_date_year                      14
    end_of_file_code                    b'\xff\xff\xff\xff'

### Example: configure setup file

The available setup options and values can be displayed with the the `--setup`
option (or its abbreviation, `-s`). Example:

    $ python el4000.py setupel3.bin --setup
    header_magic    b'\x00\x00\x00'
    unit_id         0
    hour_format     0
    date_format     0
    time_hour       0
    time_minute     0
    date_month      0
    date_day        0
    date_year       0
    currency        0
    tariff1         0.0
    tariff2         0.0

To actually set values, specify one or more options to `--setup`. Definitions
can be found in the file [defs.py](defs.py). Overview of options:

 - `unit_id`: ranges from 0 to 9.
 - `hour_format`: 1 for 12h format, 2 for 24h format.
 - `date_format`: 1 for mm/dd/yy, 2 for dd/mm/yy display.
 - `time_*` and `date_*`: set the initial clock. Note that `date_year` is in
   abbreviated form. Instead of `2014`, use `14`.
 - `currency`: 1 for `£`, 2 for Sfr, 4 for `$` and 8 for `€`
 - `tariff`, `tariff2`: ranges from 0.000 to 9.999.

To modify (or create) the `setupel3.bin` file for a 24h clock, dd/mm/yy date
format and euros, use:

    $ ./el4000.py setupel3.bin -s hour_format=2 date_format=2 currency=8
    Changing hour_format from 0 to 2
    Changing date_format from 0 to 2
    Changing currency from 0 to 8
    WARNING:Format:Invalid value 0 for name date_month
    WARNING:Format:Invalid value 0 for name date_day
    Setup file:  setupel3.bin
    header_magic    b'\xb8\xad\xf2'
    unit_id         0
    hour_format     2
    date_format     2
    time_hour       0
    time_minute     0
    date_month      0
    date_day        0
    date_year       0
    currency        8
    tariff1         0.0
    tariff2         0.0

## Contact

If you have issues, questions, ideas or suggestions, feel free to contact me at
peter@lekensteyn.nl or open a ticket at https://github.com/Lekensteyn/el4000/.
Pull requests are also welcome.

## Copyright

Copyright (C) 2014 Peter Wu

Energy Logger 4000 utility is licensed under the MIT license. See the LICENSE
file for more details.

## Links

 - References for EL3500: http://wiki.td-er.nl/index.php?title=Energy_Logger_3500
 - Energy Logger 4000 User manual (German, English and Dutch):
   http://www.produktinfo.conrad.com/datenblaetter/125000-149999/125444-an-01-ml-VOLTCRAFT_ENERGY_LOGGER_4000EKM_de_en_nl.pdf
 - File format documentation:
   http://www2.produktinfo.conrad.com/datenblaetter/125000-149999/125323-da-01-en-Datenprotokoll_SD_card_file_Formatv1_2.pdf

 [conrad]: http://www.conrad.com/ce/en/product/125444/VOLTCRAFT-ENERGY-LOGGER-4000-4320-hrs
 [python]: https://www.python.org/download/
