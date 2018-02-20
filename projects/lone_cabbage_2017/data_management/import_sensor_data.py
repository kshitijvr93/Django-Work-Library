'''
import_sensor_data.py

This code drops and creates the table water_observations from scratch,
then reads all the sensor data and re-imports it.

A more sophisticated version will probably be developed that will
read the data readings and try to insert each one, and affably fail
if there is a duplicate sensor-datetime error, meaning the same data
row is being read twice.

The import files may grow over time, so upon re-reads the larger portion
of beginning rows will be tried and fail until the reader gets to the
very end where it starts trying to read new rows.

Some pre-coordination of the import files may be advisable to speed up
this process.


Python 3.6+ code

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

#### Sqlalchemy
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column,
  Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )

from sqlalchemy.schema import CreateTable
from sqlalchemy_tools.podengo_db_engine_by_name import get_db_engine_by_name

import sqlalchemy.sql.sqltypes
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy_tools.core.utils import drop_if_exists

#import regex
import re

'''
General notes- context about the Oyster files.

Assumptions: the output table receives only sensor data and is just inserted
into, and has already been created.

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
       \s*(?P<conductivity_mS_cm>.*)\s*""", re.VERBOSE
    )

----------------
sample sensor data line to date, time and 3 floats for

(1)pressure_cm, (2)temperature_c, (3)conductivity_mS_cm
2017/08/11 12:00:00.0     1106.592      29.100       1.472

----------------

'''
#end def table_water_observation_create

class OysterProject():
    def __init__(self, engine=None, log_file=None):
        # Initialize some central data, later read some from db
        if engine is None:
            raise ValueError("Missing engine parameter")
        self.engine = engine

        self.sa_metadata = MetaData()
        # If given set study_end_date_time, to use it to limit water_observations.
        # But maybe not useful?

        # Get engine table object for water_observation
        self.table_water_observation = Table('water_observation',
            self.sa_metadata, autoload=True, autoload_with=engine)

        if log_file is None:
            self.log_file = sys.stdout
        else:
            self.log_file = log_file

        return
    # end def __init__

    def get_location_by_sensor(self,sensor_id=None):
        # todo: Later, get from db table sensor_location or sensor_event
        # or events...
        # using today's date as one param
        location_id = sensor_id

        return location_id
    # end def get_location_by_sensor
#end class Oyster

'''
class Diver():

Note: on 20180218 the current sub-folders with sample diver files are:
[ 'LC-WQ1','LC-WQ3' ]

'''

class Diver():

    '''
    From the self.project.engine, get the sensor metadata, including
    sensor serial numbers and matching locations for the Diver sensors.
    The goal is to assign sensor id and sensor location given the sensor
    serial number in the header file section for
    each dated reading (set of 1 date-time and 3 measurements per reading),
    because the sensor location can move around.

    Initially, we hard-code the d_serial_sensor data
    But we will get this from the database in a future phase.
    '''

    def get_metadata(self):
        engine_read = self.project.engine
        # Initial implementation just return a hard coded table
        # Later can read this from a database

        # Key is 'serial number' from a raw sensor file, a string really.
        # Value is the db inter id value of the sensor
        self.d_serial_sensor = {
            '..02-V5602  317.' : 1,  #loc 1 implied by folder name 20180218
            '..00-V6916  317.' : 3,  #loc 3 was implied by folder name 20180218
        }

        return

    def __init__(self,project=None,input_file_folders=None,
        input_file_globs=None, engine=None, log_file=None):

        if project is None:
            # eg an instance of the OysterProject() class
            raise ValueError("project not given")

        self.project = project
        self.log_file = project.log_file

        self.input_file_folders = input_file_folders

        if input_file_globs is None:
            self.input_file_globs = ['**/*.MON']
        else:
            self.input_file_globs = input_file_globs

        self.get_metadata()
        if engine is None:
            self.engine = self.project.engine
            engine = self.engine
        else:
            self.engine = engine

        # Example:'2017/12/21 21:00:00.0     1110.675      20.263      12.508'
        self.rx_data_reading = (
                 r"(?P<y4>.*)/(?P<mm>.*)/(?P<dd>.*)"
                 r"\s\s*(?P<hr>.*):(?P<min>.*):(?P<sec>(\d+(\.\d*)))"
                 r"\s*(?P<pressure_cm>(\d+(\.\d*)))\s*(?P<temperature_c>\d+(\.\d*))"
                 r"\s*(?P<conductivity_mS_cm>\d+(\.\d*))"
                 )
        self.rx_serial_number = r"\s*Serial number\s*=(?P<serial_number>.*)"
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

                    n_rows = self.import_file(input_file_name=input_file_name
                        ,verbosity=verbosity)

                    total_lines_inserted += n_rows
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
            print("{}:Processed total_files_count={} input files."
               .format(me, total_files_count), flush=True, file=log_file)
        return total_files_count

    def import_file(self, input_file_name=None, verbosity=1):

        me='import_file'
        log_file = self.log_file
        l_rows = []
        #rx_data_reading = self.d_name_rx['data_reading']
        rx_data_reading = self.rx_data_reading
        if verbosity > 1:
            print("rx_data_reading='{}',\nand line='{}'"
                .format(rx_data_reading,line), file=log_file)

        with open(input_file_name, 'r', encoding='latin1') as ifile:
            for line_index, line in enumerate(ifile, start = 1):
                # Nip pesky ending newline
                line = line[:len(line)-1]
                if verbosity > 1:
                    print("Parsing line {} ='{}'".format(line_index,line)
                        ,file=log_file, flush=True)
                if line.startswith('END OF') :
                    # Expected end of data LINES
                    break

                if line_index == 13:
                    #rx = self.d_name_rx['serial_number']
                    rx_serial_number = (
                      r'Serial number           =(?P<serial_number>.*)')
                    match = re.search(rx_serial_number,line)
                    # Check the serial number of this diver sensor device
                    try:
                        serial_number = match.group("serial_number")
                        serial_number = match.group(1)
                    except Exception as ex:
                        msg=("rx_serial_number={}, line={}, no serial part"
                        .format(rx_serial_number,line))
                        print(msg)
                        raise ValueError(msg)

                    d_serial_sensor = self.d_serial_sensor
                    if serial_number not in d_serial_sensor.keys():
                        msg=("Input_file_name: {}\n"
                             "Found serial number '{}' not in '{}'"
                            .format(input_file_name,serial_number,
                            d_serial_sensor.keys()))
                        raise ValueError(msg)

                    sensor_id = d_serial_sensor[serial_number]
                    location_id = self.project.get_location_by_sensor(sensor_id)

                    if verbosity > 0:
                        msg=("Input file '{}',\n line13='{},'\n"
                            " serial={}, sensor={}, location={}"
                            .format(input_file_name,line,serial_number, sensor_id,
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
                d_row['sensor_id'] = sensor_id
                d_row['location_id'] = location_id

                try:
                    data_match = re.search(rx_data_reading, line)
                except Exception as ex:
                    msg=('line={}data reading fails'.format(line_index))
                    raise ValueError(msg)

                y4 = data_match.group("y4")
                mm = data_match.group("mm")
                dd = data_match.group("dd")
                hr = data_match.group("hr")
                minute = data_match.group("min")
                sec = data_match.group("sec")
                #frac = data_match.group("frac")
                date_str="{}-{}-{} {}:{}:{}".format(y4,mm,dd,hr,minute,sec)
                d_row['observation_datetime'] = date_str

                pressure_cm = temperature_c = conductivity_mS_cm = 'tbd'
                #pressure_cm = data_match.group('pressure_cm')
                #temperature_c = data_match.group('temperature_c')
                #conductivity_mS_cm = data_match.group('conductivity_mS_cm')

                if verbosity > 1:
                  print("{}: input line {}='{}'"
                        .format(me,line_index,line),flush=True)

                if verbosity > 1:
                    d_row['date_str'] = date_str
                    print("pressure_cm='{}'".format(pressure_cm))
                    print("temperature_c='{}'".format(temperature_c))
                    print("conductivity_mS_cm='{}'".format(conductivity_mS_cm))
                # NOTE: field_names match columns in table_water_observation
                for field_name in ['pressure_cm','temperature_c','conductivity_mS_cm']:
                    value = data_match.group(field_name)
                    if verbosity > 1:
                        print("Field_name='{}', value='{}'".format(field_name,value))
                    d_row[field_name] = value
            # end line in input file
        # end with open.. input file_name

        # Insert rows to table water_observation from this input file
        for row in l_rows:
          self.project.engine.execute(
              self.project.table_water_observation.insert(), row)

        if verbosity > 0:
            print("{}:Parsed file {},\n and found {} rows:"
                .format(me,input_file_name, line_index-1))
            for count,d_row in enumerate(l_rows, start=1):
                print("{}\t{}".format(count,d_row),flush=True)

        return len(l_rows)
    # end def import_file()
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
    '''
    Line 19+: sample(Tab delimiters in raw file)
    1	26.10.2017 10:20:00	17.98	0.01	0.00	1475.31

        rx_line18_data_reading = (
        )
        rx_line19_data_reading = (
                 # Date components
                 r"(/d<sn>)\t(?P<dd>\d+).(?P<mm>\d+).(?P<y4>\d+)"
                 r"\t(?P<hr>\d+):(?P<min>\d+.*):(?P<sec>(\d+(\.\d*)))"

                 # Readings
                 r"\t(?P<temperature_c>(\d+(\.\d*)))"
                 r"\t(?P<salinity_psu>(\d+(\.\d*)))"
                 r"\t(?P<conductivity_mS_cm>\d+(\.\d*))"
                 r"\t(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
                 )


    '''
    def import_file(self, input_file_name=None, verbosity=1):

        me='import_file'
        log_file = self.log_file
        l_rows = []
        rx_line19_data_reading = (
             # Date components
             r"(/d<sn>)\t(?P<dd>\d+).(?P<mm>\d+).(?P<y4>\d+)"
             r"\t(?P<hr>\d+):(?P<min>\d+.*):(?P<sec>(\d+(\.\d*)))"

             # Readings
             r"\t(?P<temperature_c>(\d+(\.\d*)))"
             r"\t(?P<salinity_psu>(\d+(\.\d*)))"
             r"\t(?P<conductivity_mS_cm>\d+(\.\d*))"
             r"\t(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
             )

        #rx_data_reading = self.d_name_rx['data_reading']
        #rx_data_reading = self.rx_data_reading

        if verbosity > 1:
            print("rx_data_reading='{}',\nand line='{}'"
                .format(rx_data_reading,line), file=log_file)

        with open(input_file_name, 'r', encoding='latin1') as ifile:
            for line_index, line in enumerate(ifile, start = 1):
                # Nip pesky ending newline
                line = line[:len(line)-1]
                if verbosity > 1:
                    print("Parsing line {} ='{}'".format(line_index,line)
                        ,file=log_file, flush=True)
                if line.startswith('END OF') :
                    # Expected end of data LINES
                    break

                if line_index == -13:
                    #rx = self.d_name_rx['serial_number']
                    rx_serial_number = (
                      r'Serial number           =(?P<serial_number>.*)')
                    match = re.search(rx_serial_number,line)
                    # Check the serial number of this diver sensor device
                    try:
                        serial_number = match.group("serial_number")
                        serial_number = match.group(1)
                    except Exception as ex:
                        msg=("rx_serial_number={}, line={}, no serial part"
                        .format(rx_serial_number,line))
                        print(msg)
                        raise ValueError(msg)

                    d_serial_sensor = self.d_serial_sensor
                    if serial_number not in d_serial_sensor.keys():
                        msg=("Input_file_name: {}\n"
                             "Found serial number '{}' not in '{}'"
                            .format(input_file_name,serial_number,
                            d_serial_sensor.keys()))
                        raise ValueError(msg)

                    sensor_id = d_serial_sensor[serial_number]
                    location_id = self.project.get_location_by_sensor(sensor_id)

                    if verbosity > 0:
                        msg=("Input file '{}',\n line13='{},'\n"
                            " serial={}, sensor={}, location={}"
                            .format(input_file_name,line,serial_number, sensor_id,
                            location_id))
                        print(msg, file=log_file)

                    if serial_number not in self.d_serial_sensor.keys():
                        msg=("Got serial number '{}', not in '{}'"
                          .format(serial_number, serial_numbers))
                        raise ValueError(msg)

                if line_index < 18:
                    #Skip constant sensor header information
                    # later, do read line 18 too
                    continue

                # We will parse a data row...
                # later, parse out sensor_id and location_id too
                sensor_id = 9
                location_id = 9

                d_row = {}
                l_rows.append(d_row)
                d_row['sensor_id'] = sensor_id
                d_row['location_id'] = location_id

                try:
                if line_index == 18:
                    #later parse this line separately
                    continue;

                # Line 19 and greater - regular-formatted data lines
                # read and parse this data line and create output d_row
                try:
                    data_match = re.search(rx_line19_data_reading, line)
                except Exception as ex:
                    msg=('line={} data reading fails'.format(line_index))
                    raise ValueError(msg)

                y4 = data_match.group("y4")
                mm = data_match.group("mm")
                dd = data_match.group("dd")
                hr = data_match.group("hr")
                minute = data_match.group("min")
                sec = data_match.group("sec")
                #frac = data_match.group("frac")
                date_str="{}-{}-{} {}:{}:{}".format(y4,mm,dd,hr,minute,sec)
                d_row['observation_datetime'] = date_str

                pressure_cm = temperature_c = conductivity_mS_cm = 'tbd'
                #pressure_cm = data_match.group('pressure_cm')
                #temperature_c = data_match.group('temperature_c')
                #conductivity_mS_cm = data_match.group('conductivity_mS_cm')

                if verbosity > 1:
                  print("{}: input line {}='{}'"
                        .format(me,line_index,line),flush=True)

                if verbosity > 1:
                    d_row['date_str'] = date_str
                    print("temperature_c='{}'".format(temperature_c))
                    print("salinity_psu='{}'".format(salinity_psu))
                    print("conductivity_mS_cm='{}'".format(conductivity_mS_cm))
                    print("sound_velocity_m_sec='{}'".format(sound_velocity_m_sec))

                # NOTE: field_names match columns in table_water_observation
                for field_name in ['pressure_cm','salinity_psu',
                    'conductivity_mS_cm', 'sound_velocity_m_sec']:

                    value = data_match.group(field_name)
                    if verbosity > 1:
                        print("Field_name='{}', value='{}'".format(field_name,value))
                    d_row[field_name] = value
            # end line in input file
        # end with open.. input file_name

        # Insert rows to table water_observation from this input file
        for row in l_rows:
          self.project.engine.execute(
              self.project.table_water_observation.insert(), row)

        if verbosity > 0:
            print("{}:Parsed file {},\n and found {} rows:"
                .format(me,input_file_name, line_index-1))
            for count,d_row in enumerate(l_rows, start=1):
                print("{}\t{}".format(count,d_row),flush=True)

        return len(l_rows)
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
          'U:\\data\\oyster_sensor\\2017\\' )
        print("Using 'uf' input folder='{}'"
           .format(input_folder), flush=True)
        engine_nick_name = 'uf_local_mysql_lcroyster1'
    else:
        input_folder=(
          '/home/robert/data/oyster_sensor/2017/' )
        print("Using 'home' input folder='{}'"
           .format(input_folder), flush=True)

        engine_nick_name = 'hp_psql_lcroyster1'
        engine_nick_name = 'hp_mysql_lcroyster1'

    engine = get_db_engine_by_name(name=engine_nick_name)

    log_file_name="{}/log_import.txt".format(input_folder)
    log_file = open(log_file_name, mode='w')

    oyster_project = OysterProject(engine=engine, log_file=sys.stdout)

    # Create various sensor instances
    # for now, each class defines a glob to identify its files
    # and NO other sensor files.
    # This program ASSUMES/requires doordination/pre-enforecement
    # in file naming. All "Diver" raw sensor file names must
    # end in MON and each Star raw sensor file name must end
    # in WQn, where N is a digit [0-9]
    # See the class code for exact 'glob' syntax used.

    input_file_folders = [input_folder]

    diver = Diver(project=oyster_project, input_file_folders=input_file_folders,
        input_file_globs = ['**/*.MON'])

    diver.parse_files()

    # star = Star(input_folders=input_folder,
    #    input_file_globs = ['**/Star*WQ[0-9]'])

#end def run()

testme = 1
if testme == 1:

    env = 'home'
    env = 'uf'

    run(env=env, verbosity=1)
    print("Done",flush=True)

#END FILE
