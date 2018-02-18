'''
vei_mon_file_reader.py


Python 3.6+ code


imports ....

# Summary:  From input_file_name of type 'mon', validate
# the data and import into connection's table 'water_quality'
# We will have a similar method for each input file type.
# RETURN: 3-tuple of dictionaries
#(d_header, d_log, d_data) -
# d_header is header parameter names and col_values
# d_log is parsing info,warnings,errors
# d_data is data parameter names and values


def mon_file_parse(connection=None, input_file_name=None):

    # Here we assume the line counts are constant for all
    # .MON text data files. Other code might do some pre-parsing
    # to determin the line counts or other parsing clue values,
    # here line counts is just an example.
    # Some other parsing technigues can be designed as we
    # constrain/assess the variety of input file types
    # possible or set requirements on the types we support.
    dict_clues = {}
    dict_clues['header_lines'] = some_count
    dict_clues['serial_number_line']  = some_count
    ...

    # Parse and return the header info, parsing log,
    # and input file handle for the input file
    # Parser will balk at bad data, bad units,
    # errors, and issue warnings as apt.

    d_header, d_log, input_file = parse_mon_header(
        dict_clues, input_file_name)

    if d_header is None:
        # We have some error conditions in the parsing log,
        # so we will return None and let caller write the log.
        close(input_file)
        return None, d_log, None

    #continue to parse and register valid data
    d_data, d_log = parse_mon_data(input_file)

    close(input_file)

    if d_data is None:
        # parse_mon_data found bad data not within prescribed
        # ranges or other error messages
        return None, d_log, None

    # data is OK
    return d_header, d_data
#end mon_file_parse

def mon_file_dispose(connection, input_file_names):
    for input_file in input_file_names:
        d_header, d_log, d_data = (
         mon_file_parse(file_name) )
        if d_header is None or d_data is None:
            #we had some errors, so output log to error make_home_relative_folder
            write_to_error_folder(input_file_name,d_log)
        else:
            #File parsed OK, so insert to table water_quality:
            result = water_quality_insert_mon(connection, d_header, d_data)
            write_to_processed_folder(input_file_name,d_log)

def import_files():
    #
    connection = xyz --- connection to db call
    root_folder =  (parent folder of folders import, errors,
        procesed)

    # find files in import folder for each file type

    #First look for and dispose mon files
    input_file_names = find_mon_import_file_names(root_folder)

    # Do the right thing with these files
    mon_files_dispose(connection,input_file_names)

    #For other input file types zzz, also find and dispose

    input_file_names = find_xxx_import (root_folder)
    xxx_files_dispose(connection,input_file_names)

    input_file_names = find_yyy_import (root_folder)
    yyy_files_dispose(connection,input_file_names)

    ...

    input_file_names = find_zzz_import (root_folder)
    zzz_files_dispose(connection,input_file_names)

# end import_files()

'''
import sys, os, os.path, platform


def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = '/home/robert/'
        #raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()

import etl
from pathlib import Path
from collections import OrderedDict
import re

'''
<summary name='mon_file_parse'>

Assumptions: the output table receives only sensor data and is just inserted into, and has already
been created.

The given file is a 'diver sensor' file of readings data, which
adheres to the strict format expected here.

The header provides the sensor id and the channel/axis/column data names,
and they are in order, in both the [Logger settings] section and
the [Series settings] section as: PRESSSURE (in cm), TEMPERATURE, CONDUCTIVITY.

Other header values are ignored, not checked, until and if use
cases arise and are required and implemented that require
them being checked.


Also the sensor location is NOT authoritative, because
UF WEC registers location in external files or logs and does
not practice updating the sensors to always accurately have the
sensor headers display where
they are placed.

THe MON file is a text file with latin1 encoding.

The  [Data] has a line after it with a single integer that is ignored.
Subsequent lines in the data section each conform to this format:

(Date)4 digit year, slash(forward), 2 digit month, 2 digit day of month,
space:
(Time) 2 digit milatary time hour of day, colon, 2 digit minute, colon,
2 digit second, period, 1 digit of seconds precision
one or more spaces,
(first measurement): a string of decimal digits followed by a period,
  followed by 3 digits of precision.
(second measurement): a string of decimal digits followed by a period,
followed by 3 digits of precision:
(third measurement): a string of decimal digits followed by a period,
followed by 3 digits of precision:
(or or more spaces followed by end of line)

The last line in the file is a sentinel line with the text:
END OF DATA FILE OF DATALOGGER FOR WINDOWS


Each data line is used to insert a row in an output water_observations
table. That table has a unique index on the composite (sensor_id, date, time)
if a MON file row duplicates those values, it is skipped and not inserted,
though a log file line is issued to log any consecutive range of line numbers
within the input MON file that has the duplcate (already inserted data)

</summary>

regular expression for float:

float_rx = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'

float_pattern = re.compile(float_rx)

regular expression for sensor data line:
also see: https://stackoverflow.com/questions/6260777/python-regex-to-parse-string-and-return-tuple#6260945

data_line_pattern = re.compile(
    r"""\s*(?P<y4>.*?)\s*(?P<mm>.*?)\s*(?P<dd>.*?)
       \s*(?P<pressure_cm>.*)
       \s*(?P<temperature_c>.*)
       \s*(?P<condictivity_mS_cm>.*)\s*""", re.VERBOSE
    )

----------------
sample sensor data line to date, time and 3 floats for

(1)pressure_cm, (2)temperature_c, (3)conductivity_mS_cm
2017/08/11 12:00:00.0     1106.592      29.100       1.472

r''

----------------

'''
import re

def diver_reading_pattern():
    pattern = re.compile(
        r"""\s*(?P<y4>.*?)\s*(?P<mm>.*?)\s*(?P<dd>.*?)
           \s*(?P<pressure_cm>.*)
           \s*(?P<temperature_c>.*)
           \s*(?P<conductivity_mS_cm>.*)\s*""", re.VERBOSE
        )
    return pattern

'''
<summary name='extract_diver_reading'>
</summary>
<param name=pattern></param>
A pattern produced by re.compile of a regular expression
<param name='input_string'></param>
A string with which to match the pattern.
<param></param>
'''
def extract_diver_reading(pattern=None,input_line=None):
    if pattern is None:
        pattern = diver_reading_pattern()
    match = pattern.match(input_string)
    y4 = match.group("y4")
    mm = match.group("mm")
    dd = match.group("dd")
    pressure_cm = match.group('pressure_cm')
    temperature_c = match.group('temperature_c')
    conductivity_mS_cm = match.group('conductivity_mS_cm')

    values = ['y4','mm','dd','pressure_cm','temperature_c',
              'conductivity_mS_cm']

    if not all(values):
        msg = ("Input string '{}' has not all values of {}"
            .input_string, values)
        raise ValueError(msg)

    return("{}-{}-{}".format(y4,mm,dd),
           pressure_cm,
           temperature_c,
           conductivity_mS_cm)
# end def_extract_diver_reading

def mon_file_parse0(engine_write=None, input_file_name=None,log_file=None,
    verbosity=1):

    me='mon_file_parse0'
    rx_floats = r"(?<![a-zA-Z:])[-+]?\d*\.?\d+"
    rp_floats = re.compile(rx_floats)
    float_names = ['pressure_cm', 'temperature_c', 'conductivity_mS_cm']
    l_rows = []
    with open(input_file_name, 'r', encoding='latin1') as ifile:
        for line_index, line in enumerate(ifile, start = 1):
            line = line[:len(line)-1]
            if line.startswith('END OF') :
                # Expected end of data LINES
                break
            if line_index < 66:

                #Skip constant sensor header information
                continue

            d_row = {}
            l_rows.append(d_row)
            if verbosity > 0:
              print("{}: input line {}='{}'"
                    .format(me,line_index,line),flush=True)
            fields = line.split(' ');
            date_str = fields[0]
            time_str = fields[1]
            d_row['date_str'] = date_str
            d_row['time_str'] = time_str
            floats_str = ' '.join(fields[2:])
            #d_row['time_str'] = time_str
            if verbosity > 0:
                print("{}: got date='{}', time='{}', floats='{}'"
                    .format(me,date_str,time_str,floats_str))

            l_matches = rp_floats.findall(floats_str)
            n_readings = len(l_matches)
            if len(l_matches) != 3:
                msg=("{}: file={}, line {} has {} readings, Not 3."
                    .format(me,input_file_name,line_index,n_readings))
                print("Error {}:".format(msg), flush=True)
                raise ValueError(msg)
            for float_index,m in enumerate(l_matches, start=0):
                #ms = m.group() #method group() returns the match string
                if verbosity > 1:
                    print("Got match ='{}'".format(m),flush=True)
                d_row[float_names[float_index]] = float(m)
        # end line in input file
    # end with open.. input file_name
    if verbosity > 0:
        print("{}:Parsed file {},returning {} rows:"
            .format(me,input_file_name, line_index-1))
        for d_row in l_rows:
            print("{}".format(d_row),flush=True)
    return l_rows

#end def mon_file_parse0()

'''
The diver files are like windows 'ini' files, so use python 3.6
package configparser

Note: on 20180218 the 'Diver' folders are
[
'LC-WQ1','LC-WQ3'
]
'''
import configparser

class Diver():

    '''
    From the engine_read, get the sensor metadata, including
    sensor serial numbers and matching locations for the Diver sensors.
    The goal is to assign sensor id and sensor location given the sensor_id
    and date of each reading, as the sensor location can move around.

    Initially, we hard-code the d_serial_sensor and d_sensor_location data
    But we will get this from the database in a future phase.
    '''

    def get_metadata(self,engine_read=None):

        # initial implementation just return a hard coded table
        # Later can read this from a database
        if engine_read is None:
            # Key is 'serial number' from a raw sensor file, a string really.
            # Value is the db inter id value of the sensor
            self.d_serial_sensor = {
                '..02-V5602  317.' : 1,  #loc 1 implied by folder name 20180218
                '..00-V6916  317.' : 3,  #loc 3 was implied by folder name 20180218
            }
            # Hard code - assume for now that sensor id value happens to match
            # its location id value, but later it will be in a db table
            # Key is the sensor id and value is the location id
            self.d_sensor_location = {
                1 : 1,
                3 : 3,
            }
        else:
            raise ValueError("Not implemented")

        return

    def __init__(self,input_file_folders=None,
        input_file_globs=None, engine=None, log_file=None):

        self.input_file_folders = input_file_folders

        if input_file_globs is None:
            self.input_file_globs = ['**/*.MON']
        else:
            self.input_file_globs = input_file_globs

        if log_file is None:
            self.log_file = sys.stdout
        else:
            log_file = sys.stdout
        self.get_metadata()

        self.d_name_rx = {

            #The rx for line 13, serial number extraction
            'serial_number': (
                 r"""\s*Serial number\s*=(?P<serial_number>.*?)"""
                 ),
# Example:'  Serial number           =..02-V5602  317.'

            'data_reading' : (
                 r"""\s*(?P<y4>.*?)/(?P<mm>.*?)/(?P<dd>.*?)
                 \s*(?P<hr>.*?):(?P<min>.*?):(?P<sec>.*?).(?P<frac>.*?)
                 \s*(?P<pressure_cm>.*)
                 \s*(?P<temperature_c>.*)
                 \s*(?P<condictivity_mS_cm>.*)\s*""",
                 )
# Example:'2017/12/21 21:00:00.0     1110.675      20.263      12.508'
        }

    #end def __init__


    def parse_files(self, verbosity=1):
        me = 'parse_files'
        total_files_count = 0
        total_lines_inserted = 0
        log_file = self.log_file

        for input_folder in self.input_file_folders:
            if verbosity > 0:
                print
            for glob in self.input_file_globs:
                input_path_list = list(
                    Path(input_folder).glob(glob))
                for count,path in enumerate(input_path_list, start=1):
                    input_file_name = "{}{}".format(input_folder,path.name)
                    input_file_name = path.resolve()
                    total_files_count += 1
                    if verbosity > 0:
                        print("{}: for glob='{}',parsing input file '{}'"
                            .format(me,glob,input_file_name),flush=True
                            , file=log_file )

                    l_rows = self.parse_file(engine_write=None,
                        input_file_name=input_file_name
                        ,verbosity=verbosity)

                    total_lines_inserted += len(l_rows)
                    #l_rows = ['one']
                    if verbosity > 5:
                        print(
                           "{}: Parsed file {}={} with {} reading rows"
                          .format(me, count, input_file_name,len(l_rows))
                          ,file=log_file)
                # end for path in input_path_list
            #end for glob in star_globs
        #end for input_folder in input_folders

        if verbosity > 0:
            print("{}:Processed count={} input files."
               .format(me, count), flush=True, file=log_file)
        return total_files_count

    def parse_file(self,engine_write=None, input_file_name=None,
         verbosity=1):

        me='parse_file'
        log_file = self.log_file
        l_rows = []

        with open(input_file_name, 'r', encoding='latin1') as ifile:
            for line_index, line in enumerate(ifile, start = 1):
                # Nip pesky ending newline
                line = line[:len(line)-1]
                if verbosity > 0:
                    print("Parsing line {} = {}".format(line_index,line)
                        ,file=log_file, flush=True)
                if line.startswith('END OF') :
                    # Expected end of data LINES
                    break

                if line_index == 13:
                    rx = self.d_name_rx['serial_number']
                    match = re.search(rx,line)
                    # Check the serial number of this diver sensor device
                    try:
                        serial_number = match.group("serial_number")
                    except Exception as ex:
                        msg=("rx={}, line={}, no serial part"
                        .format(rx,line))
                        print(msg)
                        raise ValueError(msg)


                    if serial_number not in d_serial_sensor.keys():
                        msg=("Found serial number {} not in {}"
                            .format(serial_number, d_serial_location.keys()))
                        raise ValueError(msg)
                    sensor_id = d_serial_sensor[serial_number]
                    location_id = d_sensor_location[sensor_id]

                    if verbosity > 10:
                        msg=("Input file '{}' serial={}, sensor={}, location={}"
                            .format(input_file,serial_number, sensor_id,
                            location_id))
                        print(msg, file=log_file)

                    if serial_number not in self.d_serial_sensor.keys():
                        msg=("Got serial number '{}', not in '{}'"
                          .format(serial_number, serial_numbers))
                        raise ValueError(msg)

                if line_index < 67:
                    #Skip constant sensor header information
                    continue


                # Now read and parse this data line and create output d_row
                d_row = {}
                l_rows.append(d_row)

                try:
                    rx = self.d_name_rx['data_reading']
                    match = re.search(rx, line)
                except Exception as ex:
                    msg=('line={}data reading fails'.format(line_index))
                    raise ValueError(msg)

                y4 = match.group("y4")
                mm = match.group("mm")
                dd = match.group("dd")
                date_str="{}-{}-{} {}:{}:{}.{}".format(y4,mm,dd,hr,min,sec,frac)

                if verbosity > 1:
                  print("{}: input line {}='{}'"
                        .format(me,line_index,line),flush=True)

                d_row['date_str'] = date_str
                for field_name in ['pressure_cm','temperature_c','conductivity_mS_cm']:
                    d_row[field_name] = float(match.group(field_name))

            # end line in input file
        # end with open.. input file_name
        if verbosity > 0:
            print("{}:Parsed file {},returning {} rows:"
                .format(me,input_file_name, line_index-1))
            for count,d_row in enumerate(l_rows, start=1):
                print("{}\t{}".format(count,d_row),flush=True)
        return l_rows
    # end def parse_file()
#end class Diver()

'''
However, this software is not dependent on that, though it
may facilitate locating test data to test modifications to this
program.
'''

class Star():
    def __init__(input_file_folders=None,
        input_file_globs=None, d_serial_location=None):

        rx_serial = ''  #tbd

        # Later can read this from a database
        if d_serial_location is None:
            self.d_serial_location = {
                # Diver sensors as of 20171222
                '..02-V5602  317.' : 1, #loc 1 per folder name 20180218
                '..00-V6916  317.' : 3,  #loc 3 per folder name 20180218
                # Star ODDI sensors as of 20171222
                'DST CTD 8814' : 2,
                'DST CTD 9058' : 4, # LC-WQ4 folder on 20180218
                'DST CTD 9060' : 5, # LC-WQ5 folder on 20180218
                'DST CTD 9061' : 6, # LC-WQ6 folder on 20180218
                'DST CTD 9035' : 7, # LC-WQ7 folder on 20180218
                'DST CTD 9062' : 8, # LC-WQ8 folder on 20180218
                'DST CTD 9036' : 9, # LC-WQ9 folder on 20180218
            }
        else:
            self.serial_location = d_serial_location

        if input_file_globs is None:
            self.input_file_globs = ['**/Star*WQ[0-9]']
        else:
            self.input_file_globs = input_file_globs

    #end def __init__
#end class Star

'''
May not need class Oyster_Sensor as we can do parsing with the
Diver and Star classes, but if add more fixed sensor classes
later, this class might be useful to serve some management
functions.

Leave this code here as a stub for possible later implementation.

'''
class Oyster_Sensor():
    def __init__(d_serial_location=None):

        if d_serial_location is None:
            self.d_serial_location = {
                'DST CTD 8814' : 2,
                'DST CTD 9058' : 4, # LC-WQ4 folder on 20180218
                'DST CTD 9060' : 5, # LC-WQ5 folder on 20180218
                'DST CTD 9061' : 6, # LC-WQ6 folder on 20180218
                'DST CTD 9035' : 7, # LC-WQ7 folder on 20180218
                'DST CTD 9062' : 8, # LC-WQ8 folder on 20180218
                'DST CTD 9036' : 9, # LC-WQ9 folder on 20180218
            }
        else:
            self.serial_location = d_serial_location

        # Populate the location-indicator input folder names
        # for now manually by examining the input files Mel Moreno
        # made for Robert 2/14/2018 or so
        # Note: if an input file is found under a folder not
        # whose sensor-location association does not
        # match this folder, a warning should be issued.
        self.d_folder_location_20180216 = {
            'LC-WQ1' : 1 ,
            'LC-WQ2' : 2,
            'LC-WQ3' : 3,
            'LC-WQ4' : 4,
            'LC-WQ5' : 5,
            'LC-WQ6' : 6,
            'LC-WQ7' : 7,
            'LC-WQ8' : 8,
            'LC-WQ9' : 9,
        }
        self.l_sensor_serial_numbers = [
            '..02-V5602  317.',
            ''
        ]
        self.diver_glob = ['**/*.MON']
        self.star_globs = ['**/Star*WQ[0-9]']
        #Populate the valid sensor serial numbers (may read from db
        # later if needed)

        self.sensor_serial_numbers = [

        ]

        return
#end class Oyster_Sensor

'''

Note: the input files to use were identified in an email from Mel
Moreno to Robert Phillips 2018-02-12.

'''

def run(env=None,verbosity=1):
    me='run'

    if env == 'uf':
        input_folder=(
          'U:\\rvp\\data\\oyster_sensor\\2017\\' )
        print("Using 'uf' input folder='{}'"
           .format(input_folder), flush=True)
    else:
        input_folder=(
          '/home/robert/data/oyster_sensor/2017/' )
        print("Using 'home' input folder='{}'"
           .format(input_folder), flush=True)

    # Create various sensor instances
    # for now, each class defines a glob to identify its files
    # and NO other sensor files.
    # This program ASSUMES/requires doordination/pre-enforecement
    # in file naming. All "Diver" raw sensor file names must
    # end in MON and each Star raw sensor file name must end
    # in WQn, where N is a digit [0-9]
    # See the class code for exact 'glob' syntax used.

    input_file_folders = [input_folder]

    diver = Diver(input_file_folders=input_file_folders,
        input_file_globs = ['**/*.MON'])

    diver.parse_files()

    #star = Star(input_folders=input_folder,
    #    input_file_globs = ['**/Star*WQ[0-9]'])


#end def run()

testme = 1
if testme == 1:

    env = 'home'

    run(env=env, verbosity=1)
    print("Done",flush=True)
else:
    config = configparser.ConfigParser()
    config.sections()
