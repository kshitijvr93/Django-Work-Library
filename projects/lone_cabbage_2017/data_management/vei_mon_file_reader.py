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
# d_data is data parameter nams and values

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

'''
<summary name='mon_file_parse'>

Assumption: the output table is just inserted into, and has already
been created:

</summary>

'''
import re
def mon_file_parse(engine_write=None, input_file_name=None,verbosity=1):
    me='mon_file_parse'
    rx_floats = r"(?<![a-zA-Z:])[-+]?\d*\.?\d+"
    rp_floats = re.compile(rx_floats)
    float_names = ['pressure_cm', 'temperature_c', 'conductivity_mS_cm']
    l_rows = []
    with open(input_file_name,'r', encoding='utf-8') as ifile:
        for line_index, line in enumerate(ifile, start = 1):
            if verbosity > 0:
              print("{}: input line {}='{}'"
                    .format(me,line_index,line),flush=True)

            l_matches = rp.findall(source_str)
            n_measures = len(l_matches)
            if len(l_matches != 3):
                msg=("{}: file={}, line {} has {} measurements, Not 3."
                    .format(me,input_file_name,line_index,n_measrues))
                raise ValueError(msg)
            d_row = {}
            l_rows.append(d_row)
            for float_index,m in enumerate(l_matches, start=0):
                #ms = m.group() #method group() returns the match string
                if verbosity > 0:
                    print("Got match ='{}'".format(m),flush=True)
                d_row[float_names[float_index]] = float(m)
        # end line in input file
    # end with open.. input file_name
    return l_rows

def run(verbosity=1):
    me='run'
    glob = '*'
    input_folder=(
      '/c/rvp/git/citrus/projects/lone_cabbage_2017/data_management')
    print("Using input folder='{}',glob='{}'"
       .format(input_folder,glob), flush=True)
    input_path_list = list(Path(input_folder).glob(glob))
    count = 0
    for count,path in enumerate(input_path_list, start=1):
        mon_file_parse(engine_write=None,input_file_name=path.name
            ,verbosity=verbosity)
    if verbosity > 0:
        print("{}:Processed count={} input files."
           .format(me, count), flush=True)
    return count

testme = 1
if testme == 1:
    run()
