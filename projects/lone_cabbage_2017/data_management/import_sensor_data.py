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
def table_water_observation_create(metadata=None):
    table_name = 'water_observation'
    me = '{}_create'.format(table_name)

    # NOTE: we break from convention and use observation_id
    table_object =  Table(table_name, metadata,
      Column('{}_id'.format(table_name), Integer,
          # NOTE do NOT use Sequence here for mysql?
          #Sequence('{}_id_seq'.format(table_name), metadata=metadata),
          primary_key=True, autoincrement=True,
          comment='Automatically incremented row id.'),
      UniqueConstraint('{}_id'.format(table_name),
          name='uq1_{}'.format(table_name) ),
      Column('sensor_id', Integer),
      Column('observation_datetime', DateTime),
      UniqueConstraint('sensor_id','observation_datetime',
          name='uq2_{}'.format(table_name) ),
      # location_id can be derived, maybe no need to populate via imports?
      Column('location_id', Integer, default=1),
      Column('phosphorus_ug', Float),
      Column('nitrogen_ug', Float),
      Column('chlorophyll_ug', Float),
      Column('secchi_ft', Float),
      Column('color_pt_co', Float),
      Column('specific_conductance_us_cm_25c', Float),
      Column('specific_conductance_ms_cm_25c', Float),
      Column('salinity_g_kg', Float),
      Column('temperature_c', Float),
      Column('pressure_psi', Float),
      Column('pressure_cm', Float),
      Column('conductivity_mS_cm', Float),
      Column('sound_velocity_m_s', Float),
      Column('note', String(20),
             comment='Short note on observation'),
      ForeignKeyConstraint(
        ['sensor_id'], ['sensor.sensor_id'],
        name='fk_{}_sensor_id'.format(table_name)),
      ForeignKeyConstraint(
        ['location_id'], ['location.location_id'],
        name='fk_{}_location_id'.format(table_name)),
      )

    return table_object
#end def table_water_observation_create

class OysterProject():
    def __init__(self, engine=None):
        # initialize some central data, later read from db
        metadata = MetaData()
        table_water_observation_create(metadata=metadata)
        d_name_table =
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
    From the engine_read, get the sensor metadata, including
    sensor serial numbers and matching locations for the Diver sensors.
    The goal is to assign sensor id and sensor location given the sensor
    serial number in the header file section for
    each dated reading (set of 1 date-time and 3 measurements per reading),
    because the sensor location can move around.

    Initially, we hard-code the d_serial_sensor data
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
        else:
            raise ValueError("Not implemented")

        return

    def __init__(self,project=None,input_file_folders=None,
        input_file_globs=None, engine=None, log_file=None):

        if project is None:
            # eg an instance of the OysterProject() class
            raise ValueError(project not given)

        self.project = project
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
                 r"\s*Serial number\s*=(?P<serial_number>.*)"
                 ),
# Example:'  Serial number           =..02-V5602  317.'
            # orig
            'orig_reading_orig' : (
                 r"\s*(?P<y4>.*)/(?P<mm>.*)/(?P<dd>.*)"
                 r"\s*(?P<hr>.*):(?P<min>.*):(?P<sec>.*)\.(?P<frac>.*)"
                 r"\s*(?P<pressure_cm>.*)\s*(?P<temperature_c>.*)"
                 r"\s*(?P<conductivity_mS_cm>.*)\s*"
                 ),













            'data_reading' : (
                 r"(?P<y4>.*)/(?P<mm>.*)/(?P<dd>.*)"
                 r"\s\s*(?P<hr>.*):(?P<min>.*):(?P<sec>(\d+(\.\d*)))"
                 r"\s*(?P<pressure_cm>(\d+(\.\d*)))\s*(?P<temperature_c>\d+(\.\d*))"
                 r"\s*(?P<conductivity_mS_cm>\d+(\.\d*))"
                 )
# Example:'2017/12/21 21:00:00.0     1110.675      20.263      12.508'
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
            print("{}:Processed total_files_count={} input files."
               .format(me, total_files_count), flush=True, file=log_file)
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
                if verbosity > 1:
                    print("Parsing line {} ='{}'".format(line_index,line)
                        ,file=log_file, flush=True)
                if line.startswith('END OF') :
                    # Expected end of data LINES
                    break

                if line_index == 13:
                    #rx = self.d_name_rx['serial_number']
                    rx = r'''Serial number           =(?P<serial_number>.*)'''
                    match = re.search(rx,line)
                    # Check the serial number of this diver sensor device
                    try:
                        serial_number = match.group("serial_number")
                        serial_number = match.group(1)
                    except Exception as ex:
                        msg=("rx={}, line={}, no serial part"
                        .format(rx,line))
                        print(msg)
                        raise ValueError(msg)

                    d_serial_sensor = self.d_serial_sensor
                    if serial_number not in d_serial_sensor.keys():
                        msg=("Found serial number '{}' not in '{}'"
                            .format(serial_number, d_serial_sensor.keys()))
                        raise ValueError(msg)
                    sensor_id = d_serial_sensor[serial_number]
                    location_id = project.get_location_by_sensor(sensor_id)

                    if verbosity > 0:
                        msg=("Input file '{}',\n line13='{},' serial={}, sensor={}, location={}"
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

                try:
                    rx = self.d_name_rx['data_reading']
                    if verbosity > 1:
                        print("rx='{}',\nand line='{}'".format(rx,line),
                              file=log_file)

                    data_match = re.search(rx, line)
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

                for field_name in ['pressure_cm','temperature_c','conductivity_mS_cm']:
                    value = data_match.group(field_name)
                    if verbosity > 1:
                        print("Field_name='{}', value='{}'".format(field_name,value))
                    d_row[field_name] = value
            # end line in input file
        # end with open.. input file_name

        if verbosity > 0:
            print("{}:Parsed file {},\n and returning {} rows:"
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
          'U:\\data\\oyster_sensor\\2017\\' )
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

    if env == 'uf':
        #something all messet up.. THIS works for UF! using env of uf...
        engine_nick_name = 'uf_local_mysql_marshal1'
        engine_nick_name = 'uf_local_mysql_lcroyster1'
        # sqlite FAIL: "SQLite does not support autoincrement for
        #   composite primary keys"
        # engine_nick_name = 'uf_local_sqlite_lcroyster1'
    else:
        engine_nick_name = 'hp_mysql_lcroyster1'
        engine_nick_name = 'hp_psql_lcroyster1'
        engine_nick_name = 'hp_mysql_lcroyster1'

    engine = get_db_engine_by_name(name=engine_nick_name)
    // resume here... to call method to create water obs table..


    input_file_folders = [input_folder]

    diver = Diver(input_file_folders=input_file_folders,
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
