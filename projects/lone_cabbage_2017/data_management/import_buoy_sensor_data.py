'''
import_sensor_data.py

This reads sensor data from a root directory in specific sensor formats
Now two formats are supported (1) van Essen "Diver" sensor native
files and (2) Star-ODDI sensor native files.

This code might be modified to optionally drop and recreate the output table,
named lcroyster_buoyobservation before importing the data from the input files.
However, mysql workbench can be used to delete rows from the table.

By not dropping the current database table, this allows the user to keep
the current data in the table while importing the input files. However,
if any sensor readings in the input files are duplicates of readings already
in the database, the log will present warning messages that the duplicates
were not inserted, and this will also significantly slow down execution
time of the total import process.
It may be easier and faster to drop the database table and always
import all the data than to jocky potential input files around in your file
space to ensure only the 'new readings' will be included.
If there are no duplicate readings, this import process should import
about 15,000 readings/rows per minute.

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
    sys.path.append('{}'.format(modules_root))
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return platform_name

#platform_name=register_modules()

import os, sys, os.path
MY_SECRETS_FOLDER = os.environ['MY_SECRETS_FOLDER']

print("Using MY_SECRETS_FOLDER={}".format(MY_SECRETS_FOLDER))

sys.path.append(os.path.abspath(MY_SECRETS_FOLDER))
print("Using system.path={}".format(sys.path))

#from etl import sequence_paths
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
#from my_secrets.settings_sqlalchemy import get_engine_spec_by_name

from sqlalchemy.sql import select
import sqlalchemy.sql.sqltypes
from sqlalchemy.dialects.postgresql import ARRAY
#from sqlalchemy_tools.core.utils import drop_if_exists

#import regex
import re
import datetime
import math

'''
General notes- context about the Oyster files.

Assumptions: From this import process, the output table receives only sensor
data and the table has already been created, so it is just inserted into.

Each given file is either a 'diver sensor' or a 'oddi star sensor'
text file of readings data, which adheres to the strict format expected here.

The header lines of a sensor data file provides the
sensor id and the channel/axis/column data names,
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

Each data line is used to insert a row in an observations table.
That table must have a unique index on the composite (sensor_id, date, time)
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
'''Class SalinityPsuCalculatorDouglass2010

Calculate salinity with params, with formulae and constant value Defaults
given by spreadsheet uf-emailed from Joe Aufmuth 20180510.

'''
class SalinityPsuCalculatorDouglass2010():
    '''

    '''
    def __init__(self,standard=42.9, verbosity=0):
        self.me = 'SalinityPsuCalculatorDouglass2010'
        self.verbosity = verbosity
        #  may make a param later - resusing referenced cell names as var
        # names here too
        self.temperature_c = None  # can be set from a10 value later
        self.conductivity_mS_cm= None  # can be set from b10 value later

        self.c10 = standard
        self.ref_cond_at_35psu_15c = self.c10


        if verbosity > 0:
            print("{}: Initializing salinity_calculator:"
              .format(self.me))
        #end if
    # End def __init__

    def from_temperature_c_conductivity_mS_cm(self,temperature_c=None,
        conductivity_mS_cm=None
    ):
        # Calculate and return salinity in Practical Salinity Unit value
        # First calculate sub-terms to clarify the formula
        temperature_c = float(temperature_c)
        conductivity_mS_cm = float(conductivity_mS_cm)
        self.a10 = temperature_c
        self.b10 = conductivity_mS_cm

        #conductivity_ratio is measured conductivity/reference conductivity
        self.d10 = self.b10/self.c10

        #self.g10 is rt calculation based on a10
        self.g10 = ( 0.6766097 + 0.0200564*self.a10
          + 0.0001104259 * self.a10 ** 2
          + (-6.9698*10**-7) * self.a10**3
          + (1.0031*10**-9) * self.a10**4
        )

        # self.e10 is Conductivity ratio/rt
        self.e10 = self.d10/self.g10

        #self.f10 is dS
        self.f10 = (
          ((self.a10 -15)/(1 + 0.0162 * (self.a10-15)))
          * (0.0005
            + (-0.0056) * self.e10**0.5
            + (-0.0066) * self.e10
            + (-0.0375) * self.e10**1.5
            + (0.0636)  * self.e10**2
            + (-0.0144) * self.e10**2.5
          )
        )

        #self.h10 is calculated salnity in psu (practical salinity units)
        self.h10 = ( 0.008
          + (-0.1692  * self.e10**0.5)
          + 25.3851   * self.e10
          + 14.0941   * self.e10**1.5
          + (-7.0261) * self.e10**2
          + 2.7081    * self.e10**2.5
          + self.f10
        )
        return self.h10
    # end def from_temperature_c_conductivity_mS_cm
# end class salinity_calculator1

def sequence_paths(input_folders=None, input_path_globs=None, verbosity=0):
    # NOTE: I changed arg input_path_glob to input_path_globs
    # apologies to callers that need to adapt
    me = 'sequence_paths'
    if (input_folders is None or input_path_globs is None):
        msg = "Missing param input_folders or input_path_glob"
        raise ValueError(msg)

    # compose input_path_list over multiple input_folders
    for input_folder in input_folders:
        for input_path_glob in input_path_globs:
            paths = list(Path(input_folder).glob(input_path_glob))
            if (verbosity > 0):
                print("{}: Found {} files in input_folder='{}'"
                   " that match {}\n"
                  .format(me, len(paths), input_folder, input_path_glob))

            #input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))
            for path in paths:
                yield path
            # end for path
        #end for input_path_glob
    # end for input folder
# end def sequence_paths

class OysterProject():
    ''' Get  sensor serial numbers into useful list
        Future: create a generator function to take engine and table name
        and create a generator of rows, and use that.
    '''
    def get_d_serial_sensor(self, table_name='lcroyster_sensor'):
        me = 'get_d_serial_sensor'
        metadata = MetaData()
        engine = self.engine
        verbosity = self.verbosity
        log_file = self.log_file
        table_deploy = Table(table_name, metadata, autoload=True,
            autoload_with=engine)
        s = select([table_deploy])
        conn = engine.connect()
        result = conn.execute(s)
        self.d_serial_sensor = {}

        for row in result:
            self.d_serial_sensor[row['serial_number']] = row['sensor_id']
            if verbosity > 0:
                msg=("Got sensor serial_number '{}' with sensor_id {}"
                  .format(row['serial_number'], row['sensor_id']))
        return
    # end def get_d_serial_sensor


    ''' Get  sensor deployments into useful dictionary
    '''
    def get_d_sensor_deployment(self):
        me = 'get_d_sensor_deployment'
        metadata = MetaData()
        engine = self.engine
        verbosity = self.verbosity
        log_file = self.log_file
        table_deploy = Table('lcroyster_sensordeploy', metadata, autoload=True,
            autoload_with=engine)
        s = select([table_deploy])
        conn = engine.connect()
        result = conn.execute(s)

        l_rows = []
        if verbosity > 1 or 1 ==1:
            print("{}: Showing lcroyster_sensordeploy rows:".format(me),
              file=log_file)
            for count,row in enumerate(result):
                print ("Got row='{}'".format(row),file=log_file)
                l_row = {
                    'sensor_id': row['sensor_id'],
                    'event_date': row['deploy_datetime'],
                    'location_id': row['location_id'],
                    }
                print("Got l_row = {}".format(l_row),file=log_file)
                l_rows.append(l_row)

        # d_sensor_deployment{} key is sensor, value is dict keyed by unique
        # dates, each with a location id (deployment location) value.
        d_sensor_deployment = {}
        for d_row in l_rows:
            if self.verbosity > 0:
                print("Sensor deployment: Using d_row='{}'".format(d_row)
                    ,file=self.log_file)
            sensor_id = d_row['sensor_id']
            if d_sensor_deployment.get(sensor_id, None) is None:
                d_sensor_deployment[sensor_id] = dict()
            d_date_loc = d_sensor_deployment[sensor_id];

            #dt = datetime.datetime.strptime(d_row['event_date'],"%Y-%m-%d %H:%M:%S")
            dt = d_row['event_date']

            if dt in d_date_loc.keys():
                raise ValueError(
                 "Sensor {} has duplicate sensor datetime {}"
                 .format(sensor_id, repr(dt)))

            d_date_loc[dt] = d_row['location_id']

        # Replace each d_date_loc with an orderedDict to
        # support faster downstream processes
        for sensor_id, d_date_loc in d_sensor_deployment.items():
            # Sort each sensor_deployment dict by date keys
            d_sensor_deployment[sensor_id] = OrderedDict(
              { key:d_date_loc[key] for key in sorted(d_date_loc.keys()) })

        if self.verbosity > 1:
            print("Got final d_sensor_deployment = {}"
                .format(repr(d_sensor_deployment)),file=self.log_file)

        self.d_sensor_deployment = d_sensor_deployment
        return
    #end def get_d_sensor_deployment

    '''
    get_in_service_location():
    Potential speedup:
    Put the increasing times in a list rather than a dict so they can be
    indexed and return the index of deployed so the caller can state it as
    a param on a successive call to save time.. because the caller's inputs
    are sorted such that the time is always increasing within a file.
    '''

    def get_in_service_location(
        self,sensor_id=None, observation_datetime=None):
        # Return True if this observation falls in a period of a valid
        # deployment to a project location
        try:
            od_datetime_loc = self.d_sensor_deployment[sensor_id]
        except:
            msg=("\n*********************\n"
                 "FATAL ERROR: Sensor_id '{}' has raw data but no deployments."
                 "\n*********************\n"
              .format(repr(sensor_id)))
            print(msg, file=self.log_file)

            # NOTE: log file output shows newlines, but ValueError shows \n
            raise ValueError("**** FATAL ERROR: See log_file={}"
              .format(self.log_file.name))
        #Find whether this date is covered by a valid deployment
        in_service = 0
        location_id = 0
        for deployed, location_id in od_datetime_loc.items():
            if deployed > observation_datetime:
                #This deployment is in the future beyond this observation,
                #so just break with the current in_service_value
                break;
            if observation_datetime >= deployed and location_id != 0:
                # 0 is the 'unknown' or invalid location
                in_service = 1
        return in_service, location_id

    #end def get_in_service() of class OysterProject

    #class OysterProject
    def __init__(self, engine=None, observations_table_name=None,
        log_file=None, verbosity=1, max_exception_logs_per_file=10):
        me='OysterProject.__init__'
        # Initialize some central data, later read some from db


        if verbosity > 0:
            print("{}: starting".format(me), file=log_file)
        self.verbosity = verbosity
        self.SalinityPsuCalculator = SalinityPsuCalculatorDouglass2010(verbosity=1)
        if verbosity > 0:
            print("{}: Back from constructing SalinityPsuCalculator"
               .format(me), file=log_file)

        if engine is None:
            raise ValueError("Missing engine parameter")
        self.engine = engine
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.max_exception_logs_per_file = max_exception_logs_per_file
        self.log_file = log_file

        self.sa_metadata = MetaData()

        # Get engine table object for water_observation
        self.observations_table = Table(observations_table_name,
            self.sa_metadata, autoload=True, autoload_with=engine)

        if log_file is None:
            self.log_file = sys.stdout
        else:
            self.log_file = log_file

        #Get some reference database table data
        self.get_d_serial_sensor()
        self.get_d_sensor_deployment()
        #print("Test print to log file.", file=log_file)

        return
    # end def __init__
#end class OysterProject

'''
class Diver():

This class represents water quality sensors of type "Diver".

Note: on 20180218 the current sub-folders with sample diver files are:
[ 'LC-WQ1','LC-WQ3' ]

'''

class Diver():

    # class Diver():
    def __init__(self,project=None,input_file_folders=None,
        input_file_globs=None, engine=None, log_file=None):

        if project is None:
            # eg an instance of the OysterProject() class
            raise ValueError("project not given")

        self.project = project
        self.max_exception_logs_per_file = project.max_exception_logs_per_file
        self.log_file = log_file if log_file is not None else project.log_file

        self.input_file_folders = input_file_folders

        if input_file_globs is None:
            self.input_file_globs = ['**/*.MON']
        else:
            self.input_file_globs = input_file_globs

        # We require that all sensors, regardless of sensor type, maintain
        # unique sensor serial_number ids, so we can use project
        # level sensor dictionary here.
        self.d_serial_sensor = project.d_serial_sensor

        if engine is None:
            self.engine = self.project.engine
            engine = self.engine
        else:
            self.engine = engine

        # Example:'2017/12/21 21:00:00.0     1110.675      20.263      12.508'
        self.rx_diver_reading = (
                 r"(?P<y4>.*)/(?P<mm>.*)/(?P<dd>.*)"
                 r"\s\s*(?P<hr>.*):(?P<min>.*):(?P<sec>(\d+))\.\d*"
                 r"\s*(?P<pressure_cm>(\d+(\.\d*)))\s*(?P<temperature_c>\d+(\.\d*))"
                 r"\s*(?P<conductivity_mS_cm>\d+(\.\d*))"
                 )
        # rx based on Dr. Pine's group, implied by the IDs they manually record.
        #self.rx_serial_number = r"\s*Serial number\s*.*-(?P<serial_number>.*)  .*"

        self.rx_serial_number = (
          r"\s*Serial number[^-]*-(?P<serial_number>[^\s]*)\s*.*")
    #end def __init__ for class Diver()

    #class Diver
    def parse_files(self, verbosity=1):
        me = 'parse_files'
        file_count = 0

        total_file_rows = 0
        log_file = self.log_file

        gpaths = sequence_paths(input_folders=self.input_file_folders,
            input_path_globs=self.input_file_globs)

        paths = []
        total_inserts = 0
        total_exceptions = 0
        for path in gpaths:
            if path in paths:
                # gpaths could have duplicates when mulitple globs
                # were used to generate the gpaths, so skip dups
                # If carefully chosen to guarantee the globs have no dups,
                # one can bypass this checking
                continue
            #Store this path to reject future duplicates in the sequence
            paths.append(path)

            file_count += 1

            input_file_name = path.resolve()
            if verbosity > 0:
                print("{}: parsing input file '{}'"
                    .format(me, input_file_name),flush=True
                    , file=log_file )

            n_rows, n_inserts, n_exceptions = self.import_file(
                input_file_name=input_file_name ,verbosity=verbosity)

            total_file_rows += n_rows
            total_inserts += n_inserts
            total_exceptions += n_exceptions
            #l_rows = ['one']
            if verbosity > 0:
                print(
                   "{}: Parsed file {}={} with {} 'readings' rows"
                  .format(me, file_count, input_file_name, n_rows)
                  ,file=log_file)

        # end for path in paths

        if verbosity > 0:
            print("{}:Diver Files - Ending with {} files found and parsed.".format(me,file_count),
                file=log_file)

        return file_count, total_file_rows, total_inserts, total_exceptions
    # end def parse_files

    ''' Diver class: def import_file'''
    def import_file(self, input_file_name=None, verbosity=1):

        me='import_file'
        log_file = self.log_file
        l_rows = []
        #rx_diver_reading = self.d_name_rx['data_reading']
        rx_diver_reading = self.rx_diver_reading
        if verbosity > 1:
            print("rx_diver_reading='{}',\nand line='{}'"
                .format(rx_diver_reading,line), file=log_file)

        with open(input_file_name, 'r', encoding='latin1') as ifile:
            for line_count, line in enumerate(ifile, start = 1):
                # Nip pesky ending newline
                line = line[:len(line)-1]
                if verbosity > 1:
                    print("Parsing line {} ='{}'".format(line_count,line)
                        ,file=log_file)
                if line.startswith('END OF') :
                    # Expected end of data LINES
                    break

                if line_count == 13:
                    #rx = self.d_name_rx['serial_number']
                    #r'Serial number           =(?P<serial_number>.*)'
                    rx_serial_number = (
                      r'Serial number[^-]*-(?P<serial_number>[^\s]*).*'
                      )
                    match = re.search(rx_serial_number,line)
                    # Check the serial number of this diver sensor device
                    try:
                        serial_number = match.group("serial_number")
                        serial_number = match.group(1)
                    except Exception as ex:
                        msg=("rx_serial_number={}, line={}, no serial part"
                        .format(rx_serial_number,line))
                        print(msg, file=log_file)
                        raise ValueError(msg)

                    d_serial_sensor = self.d_serial_sensor
                    if serial_number not in d_serial_sensor.keys():
                        msg=("Input_file_name: {}\n"
                             "Found serial number '{}' not in '{}'"
                            .format(input_file_name, serial_number,
                            repr(d_serial_sensor.keys())))
                        raise ValueError(msg)

                    sensor_id = d_serial_sensor[serial_number]

                    if verbosity > 0:
                        msg=("Diver input file '{}',\n line13='{}',\n"
                            " serial_number='{}', sensor_id='{}'"
                            .format(input_file_name, line,
                              serial_number, sensor_id))
                        print(msg, file=log_file)

                if line_count < 67:
                    #Skip constant sensor header information
                    continue

                # Now read and parse this data line and create output d_row
                d_row = {}
                l_rows.append(d_row)
                d_row['sensor_id'] = sensor_id

                try:
                    data_match = re.search(rx_diver_reading, line)
                except Exception as ex:
                    msg=('line={}, data reading fails'.format(line_count))
                    raise ValueError(msg)

                y4 = data_match.group("y4")
                mm = data_match.group("mm")
                dd = data_match.group("dd")
                hr = data_match.group("hr")
                minute = data_match.group("min")
                sec = data_match.group("sec")
                #frac = data_match.group("frac")
                date_str = "{}-{}-{} {}:{}:{}".format(y4,mm,dd,hr,minute,sec)
                d_row['observation_datetime'] = date_str

                obs_dt = datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")
                # May check for None obs_dt here and skip?

                in_service, location_id = self.project.get_in_service_location(
                    sensor_id=sensor_id, observation_datetime=obs_dt)

                d_row['in_service'] = in_service
                d_row['location_id'] = location_id

                if verbosity > 1:
                  print("{}: input line {}='{}'"
                        .format(me, line_count, line),file=log_file)

                if verbosity > 2:
                    d_row['date_str'] = date_str
                    print("date_str='{}'".format(date_str))
                    print("in_service='{}'".format(in_service))
                    print("location_id='{}'".format(location_id))

                # NOTE: field_names match columns in observations_table_name
                d_row['pressure_cm'] = data_match.group('pressure_cm')

                temperature_c = data_match.group('temperature_c')
                d_row['temperature_c'] = temperature_c

                conductivity_mS_cm = data_match.group('conductivity_mS_cm')
                d_row['conductivity_mS_cm'] = conductivity_mS_cm

                #calculate salinity
                d_row['salinity_psu_calculated'] = (
                  self.project.SalinityPsuCalculator
                    .from_temperature_c_conductivity_mS_cm(
                       temperature_c, conductivity_mS_cm
                     )
                )

                if verbosity > 2:
                    for field_name in ['pressure_cm','temperature_c'
                      ,'conductivity_mS_cm', 'salinity_psu_calculated']:
                        print("Field_name='{}', value='{}'"
                          .format(field_name, d_row[field_name]))

                # Calculate salinity with the project's salinity_calculator

            # end line in input file
        # end with open.. input file_name

        # Insert rows to table water_observation from this input file
        n_exceptions = 0
        n_inserts = 0
        for row in l_rows:
            line_count += 1
            try:
                self.project.engine.execute(
                    self.project.observations_table.insert(), row)
                n_inserts += 1
            except Exception as ex:
                n_exceptions += 1
                if n_exceptions < self.project.max_exception_logs_per_file:
                    msg=("\n***************\n"
                        "WARNING: Input file '{}',\nline {} has error {}."
                        "\n***************\n"
                        .format(input_file_name, line_count,ex))
                    print(msg, file=log_file)
                elif n_exceptions == self.project.max_exception_logs_per_file:
                    msg = ('*** MADE MAXIMUM EXCEPTION REPORTS FOR THIS FILE.')
                    print(msg, file=log_file)

        if verbosity > 0:
            print("{}:Parsed file {} of {} rows, did {} inserts, had {} exceptions:"
                .format(me, input_file_name, line_count-1, n_inserts, n_exceptions)
                ,file=log_file)
        if verbosity > 1:
            print("Rows parsed were:")
            for count, d_row in enumerate(l_rows, start=1):
                print("{}\t{}".format(count,d_row),file=log_file)

        return len(l_rows), n_inserts, n_exceptions
    # end def import_file()
#end class Diver()

'''
However, this software is not dependent on that, though it
may facilitate locating test data to test modifications to this
program.
'''

'''
Using a given list of folders and a list of globs, create a
generator that yields:

The next path for a file under a given input folder that matches
a given glob.

TODO: revert to only one glob per generator! Two globs may be given if
a list is used that 'reiterates' the same file name, NOT a good idea.
The caller may handle this separately, or need a new non-generator
approach that keeps a dict of filenames and then tosses dups, and then
just iterates the keys.. but since the dict is already in memory, it would
NOT be a generator, just an interable.

'''

class Star():
    # This class represents water quality sensors of type "Star-ODDI".

    # class Star():
    def __init__(self,project=None, input_file_folders=None,
        input_file_globs=None, log_file=None, d_serial_location=None):
        me = "Star.__init__"
        if project is None:
            # eg an instance of the OysterProject() class
            raise ValueError("project not given")

        self.project = project
        self.max_exception_logs_per_file = project.max_exception_logs_per_file
        self.log_file = project.log_file if log_file is None else log_file

        print("{}:Using log file {}".format(me, self.log_file))
        print("{}:Using log file {}".format(me, self.log_file), file=self.log_file)

        # We require that all sensors, regardless of sensor type, maintain
        # unique sensor serial_number ids, so we can use project
        # level d_serial_sensor
        # Later we may possibly need unique serial_numbers per type,
        # so maintain this data member here.
        self.d_serial_sensor = project.d_serial_sensor

        self.input_file_folders = input_file_folders

        rx_serial = ''  #tbd

        if input_file_globs is None:
            self.input_file_globs = ['**/Star*WQ[0-9]']
        else:
            self.input_file_globs = input_file_globs

    #end def __init__

    # class Star():
    def parse_files(self, verbosity=1):
        me = 'parse_files'
        file_count = 0

        total_file_rows = 0
        log_file = self.log_file
        if verbosity > 0:
            print("{}:Starting with input_folders={},globs={}"
                .format(me, self.input_file_folders, self.input_file_globs),
                file=log_file)

        paths = sequence_paths(input_folders=self.input_file_folders,
            input_path_globs=self.input_file_globs)
        total_inserts = 0
        total_exceptions = 0
        for path in paths:
            file_count += 1

            input_file_name = path.resolve()
            n_rows, n_inserts, n_exceptions = self.import_file(
                input_file_name=input_file_name,
                verbosity=verbosity)

            total_file_rows += n_rows
            total_inserts += n_inserts
            total_exceptions += n_exceptions

        # end for path in paths
        if verbosity > 0:
            print("{}:STAR Files - Ending with {} files found and parsed."
                .format(me, file_count), file=log_file)
        return file_count, total_file_rows, total_inserts, total_exceptions
   # end def parse_files

    # class Star():
    '''
    Return None if re match failed, otherwise retur d_row of name-value pairs.
    '''
    def update_row_by_match(self, sensor_id=None,match=None, d_row=None, verbosity=1):
        me = 'update_row_by_match'

        log_file = self.log_file

        try:
            y4 = match.group("y4")
            mm = match.group("mm")
            dd = match.group("dd")
            hr = match.group("hr")
            minute = match.group("min")
            sec = match.group("sec")
            # NOTE: field_names match columns in observations_table_name
            for field_name in ['temperature_c','salinity_psu',
                'conductivity_mS_cm', 'sound_velocity_m_sec']:

                value = match.group(field_name)
                # Capitulation to inconsistent sea star sensor files.
                # Some use , some use . as decimal point
                value = value.replace(',','.')
                d_row[field_name] = value

                if verbosity > 2:
                    print("Field_name='{}', value='{}'"
                      .format(field_name, value), file=log_file)
            # end for field_name

            # Calculate salinity
            d_row['salinity_psu_calculated'] = (
              self.project.SalinityPsuCalculator
                .from_temperature_c_conductivity_mS_cm(
                   d_row['temperature_c'], d_row['conductivity_mS_cm']
                 )
            )

            date_str = "{}-{}-{} {}:{}:{}".format(y4,mm,dd,hr,minute,sec)
            d_row['observation_datetime'] = date_str
            obs_dt = datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")

            in_service, location_id = self.project.get_in_service_location(
                sensor_id=sensor_id, observation_datetime=obs_dt)

            d_row['in_service'] = in_service
            d_row['location_id'] = location_id

        except Exception as ex:
            # Signal a parsing exception
            msg = ("\n------------------\n{}:Got exception = {}"
               .format(me, repr(ex)))

            print(msg)
            sys.stdout.flush()
            print(msg, file=log_file)
            d_row = None

        return d_row
#end def update_row_by_match

    '''
    Line 19+: sample(Tab delimiters in raw file)
    1	26.10.2017 10:20:00	17.98	0.01	0.00	1475.31

        rx_line18_star_reading = (
        )
        rx_star = (
             r"\s*(?P<dd>.*)\.(?P<mm>.*)\.(?P<y4>.*)"
             r"\s\s*(?P<hr>\d):(?P<min>\d.*):(?P<sec>(\d+(\.\d*)))"
                     r"\s+(?P<temperature_c>(\d+(\.\d*)))"
                      r"\s+(?P<salinity_psu>(\d+(\.\d*)))"
                r"\s+(?P<conductivity_mS_cm>(\d+(\.\d*)))"
              r"\s+(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
             )

        rx_star_line19_reading = (
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
    # class Star():
    def import_file(self, input_file_name=None, verbosity=1):

        me='import_file'
        log_file = self.log_file
        l_rows = []
        # Date components
        # and Readings
        rx_star_serial_number_line16= (
           r".*\t(?P<serial_number>\d+)" )

        rx_star_line19_reading = (
           r"(?P<sn>\d+)\s*(?P<dd>\d+)\.(?P<mm>\d+)\.(?P<y4>\d+)"
           r"\s\s*(?P<hr>\d+):(?P<min>\d+):(?P<sec>(\d+))"
                    r"\s+(?P<temperature_c>(\d+([.,]\d*)))"
                     r"\s+(?P<salinity_psu>(\d+([.,]\d*)))"
               r"\s+(?P<conductivity_mS_cm>(\d+([.,]\d*)))"
             r"\s+(?P<sound_velocity_m_sec>(\d+([.,]\d*)))"
             )

        rx_star_line18_reading = (r"#D\s+Data:\s+"
              + rx_star_line19_reading )
              #but note sn is something else here...?

        if verbosity > 1:
            print("{}:rx_star_line19_reading='{}'"
                .format(me, rx_star_line19_reading)
                ,file=log_file)

        with open(input_file_name, 'r', encoding='latin1') as ifile:
            for line_count, line in enumerate(ifile, start=1):
                # Nip pesky ending newline
                line = line[:len(line)-1]
                if verbosity > 1:
                    print("Parsing line {} ='{}'".format(line_count,line)
                        ,file=log_file)

                if line_count == 16:
                    # Get serial number
                    rx_star_serial_number_line16= (
                       r".*\t(?P<serial_number>\d+)" )
                    try:
                        match = re.search(rx_star_serial_number_line16,line)
                        serial_number = match.group("serial_number")
                        # 20180424 - special need for Oyster Project, stick
                        # or impfer an S prefix in front of serial numbers now.
                        serial_number = 'S' + serial_number
                    except:
                        msg = ("{}: input_file has {} no serial number"
                            .format(me, input_file_name))
                        print(msg, file=log_file)
                        raise

                    d_serial_sensor = self.d_serial_sensor
                    if serial_number not in d_serial_sensor.keys():
                        msg=("ERROR: Input_file_name: {}\n"
                             "Found serial number '{}' not in '{}'"
                            .format(input_file_name, serial_number,
                            repr(d_serial_sensor.keys())) )
                        print(msg, file=log_file)
                        raise ValueError(msg)

                    sensor_id = self.d_serial_sensor[serial_number]

                    if verbosity > 0:
                        msg=("Star input file '{}',\n line13='{}',\n"
                            " serial_number='{}', sensor_id='{}'"
                            .format(input_file_name, line,
                              serial_number, sensor_id))
                        print(msg, file=log_file)

                # end if line_count == 16 (We set sensor_id and location_id)

                if line_count < 19:
                    # Skip constant sensor header information
                    continue

                d_row = {}
                l_rows.append(d_row)

                d_row['sensor_id'] = sensor_id
                if verbosity > 1:
                    print("{}: reading line {} = '{}'"
                        .format(me, line_count, line),file=log_file)

                # Here we have Line 19 and greater - regular-formatted data lines
                # read and parse this data line and create output d_row
                try:
                    data_match = re.search(rx_star_line19_reading, line)
                except Exception as ex:
                    msg=("ERROR: line number {}='{}', rx_star_line19_reading "
                         "fails,ex={}".format(line_count, line, repr(ex)))
                    raise ValueError(msg)

                # Note: since the location depends on observation date of
                # the row, the next method also updates location_id
                d_row = self.update_row_by_match(sensor_id=sensor_id,
                    match=data_match, d_row=d_row)
                if d_row is None:
                    msg = (
                            "\n*****************\n"
                            "Star.{}:PARSE ERROR:File name '{}', line count='{}':"
                            "\nLine='{}'\n"
                            "\n*****************\n"
                            .format(me, input_file_name, line_count, line))
                    print(msg, file=log_file)
                    raise ValueError(msg)

                if verbosity > 1:
                  print("{}: input line {}='{}'"
                        .format(me, line_count, line), file=log_file)

            # end line in input file
        # end with open.. input file_name

        # Insert rows to table water_observation from this input file
        line_count = 18
        n_exceptions = 0
        n_inserts = 0
        for row in l_rows:
            line_count += 1
            try:
                self.project.engine.execute(
                    self.project.observations_table.insert(), row)
                n_inserts += 1
            except Exception as ex:
                n_exceptions += 1
                if n_exceptions < self.project.max_exception_logs_per_file:
                    msg=("\n***************\n"
                        "WARNING: Input file {},\ninsert line_count {} has error {}."
                        "\n***************\n"
                        .format(input_file_name, line_count,ex))
                    print(msg, file=log_file)
                elif n_exceptions == self.project.max_exception_logs_per_file:
                    msg=("\n *** MADE MAXIMUM EXCEPTION REPORTS FOR THIS FILE")
                    print(msg, file=log_file)

        if verbosity > 0:
            print("{}:Parsed file {}\nSUMMARY: {} lines, {} inserts, "
                "and {} exceptions found.\n\n\n"
                .format(me, input_file_name, line_count-1, n_inserts,
                n_exceptions) ,file=log_file)
        if verbosity > 1:
            print("Parsed rows were:")
            for count,d_row in enumerate(l_rows, start=1):
                print("{}\t{}".format(count,d_row),file=log_file)

        return len(l_rows), n_inserts, n_exceptions
    #end def import_file

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
                # Stuck this in to test parsing 20180407
                'DST CTD 9238' : 9,
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
def get_lcroyster_settings(verbosity=1):

    # IMPORT SETTINGS FOR MARSHALING APPLICATION WEBSITE (MAW) settings
    import maw_settings
    settings_filename = '{}{}{}'.format(MY_SECRETS_FOLDER, os.sep, 'maw_settings.py')
    return maw_settings.my_project_params['lcroyster'], settings_filename

def run(input_folder=None,
    observations_table_name=None,
    log_file_name=None,
    max_exception_logs_per_file=5,
    skip_star=0, skip_diver=0, verbosity=1):
    me='run'

    d_lcroyster, settings_filename = get_lcroyster_settings()

    if input_folder is None:
        input_folder = d_lcroyster['sensor_observations_input_folder']

    if log_file_name is None:
        #datetime_string = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        day_string = datetime.datetime.utcnow().strftime("%Y%m%d")
        log_file_name = ("{}/import_buoy_sensor_data_{}.txt"
            .format(input_folder,day_string))

    log_file = open(log_file_name, mode="w", encoding='utf-8')

    print("STARTING: Using verbosity value={}".format(verbosity)
        ,file=log_file)

    print("{}:Using settings_filename={}".format(me, settings_filename)
        ,file=log_file)

    print("{}:Using data input_folder={}".format(me, input_folder)
        ,file=log_file)

    # engine_spec = get_engine_spec_by_name(name=engine_nick_name)
    d_engine_info = d_lcroyster['database_connections']['lcroyster']
    print("Got d_engine_info of length={}".format(len(d_engine_info))
        ,file=log_file)

    engine_spec = (d_engine_info['format'].format(**d_engine_info))
    engine = create_engine(engine_spec)

    # If indicated, delete the observations table rows first
    # Potential feature to add:
    '''
    if delete_observation_rows_first:
        if verbosity > 0:
            print("Deleting rows of table '{}' before importing input data."
                .format(observations_table_name),
                file=log_file)
        sa_metadata = MetaData()
        observations_table_object = Table(observations_table_name,
                sa_metadata, autoload=True, autoload_with=engine)
        observations_table_object.delete()
    '''

    oyster_project = OysterProject(engine=engine, log_file=log_file,
        observations_table_name=observations_table_name,verbosity=verbosity,
        max_exception_logs_per_file=max_exception_logs_per_file
        )

    # Create various sensor instances
    # for now, each class defines a glob to identify its files
    # and NO other sensor files.
    # This program ASSUMES/requires coordination/pre-enforcement
    # in file naming. All "Diver" raw sensor file names must
    # end in diver.MON and each Star raw sensor file name must end
    # in star.DAT
    # See the class code for exact 'glob' syntax used.

    input_file_folders = [input_folder]
    total_inserts = 0
    total_exceptions = 0

    if not skip_diver:
        diver = Diver(project=oyster_project,
            input_file_folders=input_file_folders,
            input_file_globs=['**/*diver.MON'])

        print("{}: calling diver parse_files".format(me),file=log_file)
        file_count, n_file_rows, n_inserts, n_exceptions = diver.parse_files(
           verbosity=verbosity)

        print("{}: Parsed {} Diver files with {} inserts, {} exceptions."
            .format(me, file_count, n_inserts, n_exceptions),file=log_file)

        total_inserts += n_inserts
        total_exceptions += n_exceptions

    if not skip_star:
        star = Star(project=oyster_project,
            input_file_folders=input_file_folders,
            input_file_globs=['**/*star.DAT',]
            )

        file_count, n_file_rows, n_inserts, n_exceptions = star.parse_files(
            verbosity=verbosity)
        print("{}: Parsed {} Star files with {} inserts, {} exceptions."
            .format(me, file_count, n_inserts,n_exceptions),file=log_file)

        total_inserts += n_inserts
        total_exceptions += n_exceptions

    msg = ("{}: ENDING: Did {} inserts, had {} exceptions.\n"
       "See log file name='{}'".format(me, total_inserts, total_exceptions,
       log_file_name))
    print(msg, file=log_file)
    print(msg)
    return

#end def run()

# end main code

# Launch the run() method with parsed command line parameters

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    #Hold of on making this a command line parameter for now.
    #It could allow for critical outages
    observations_table_name = 'lcroyster_buoyobservation'

    # Note: do default to get some settings from user
    # config file, like passwords
    # Add help to instruct about MY_SECRETS_FOLDER, etc.
    # Arguments

    '''
    parser.add_argument("-d", "--delete_observation_rows_first",
      # type=bool,  ## THere is no bool for add_argument, must use int
      #type=int,
      default=True, action='store_true',
      help="Defaults to True. This option deletes all table '{}' rows before "
           'importing data into the table.'.format(observations_table_name)
      )
    '''

    parser.add_argument("-v", "--verbosity",
      type=int, default=1,
      help="output verbosity integer (0 to 2)")

    parser.add_argument("-i", "--input_folder",
      #required=True,
      # default="U:\\data\\elsevier\\output_exoldmets\\test_inbound\\",
      help='All .DAT and .MON files anywhere under this folder will be read '
          'for imports. The import program will here create the file or '
          'overwrite a previous import log file.' )

    parser.add_argument("-x", "--max_exception_logs_per_file",
      type=int, default=5,
      help='Maxiumum number of insert exceptions to report per input file.' )


    parser.add_argument("-l", "--log_file_name",
      #required=True,
      # default="U:\\data\\elsevier\\output_exoldmets\\test_inbound\\",
      help='This is the name of the output log file to be placed under your '
      'input folder. If not given, the log_file_name defaults to'
      'import_buoy_sensor_data_log.txt.'
     )

    args = parser.parse_args()

    run(input_folder=args.input_folder,
        observations_table_name=observations_table_name,
        log_file_name=None,
        max_exception_logs_per_file=args.max_exception_logs_per_file,
        skip_star=0,
        skip_diver=0,
        verbosity=args.verbosity)

#end if __name__ == "__main__"

#END FILE
