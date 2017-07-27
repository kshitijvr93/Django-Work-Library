import sys, os, os.path, platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
for i,path in enumerate(sys.path):
    print("sys.path[{}]={}".format(i,repr(path)))

import datetime
import pytz
import os
import sys
from collections import OrderedDict
from etl import add_subelements_from_dict
from dataset import Dataset, data

'''

Load a couple of csv text files saved from some excel workbooks that Elsevier's Letitia
Mukherjee emailed me in 2017, into an sql server database.

'''

filename_input_csv = "C:/users/podengo/git/citrus/data/am4ir/FloridaQatar_AM4IR_pilot_filtered.txt"

dsr = Dataset(dbms='csv',delimiter='\t',name=filename_input_csv, open_mode="r", encoding='utf-8')

row_set = dsr.dict_reader()

#Print field/column/header values
print("Input field names={}".format(row_set.fieldnames))

#for i0,row in enumerate(row_set):

# create pyodbc connection for the table to which we will write
# create dataset writer for input dataset 'a' for am4ir in year 2017

dsw = Dataset(dbms="pyodbc",open_mode="w", encoding='utf=8'
    , server=".\SQLEXPRESS", db="silodb", table='am4ir_2017a')

data(dsr=dsr, dsw=dsw, verbosity=1)
#dw.writeheader()
