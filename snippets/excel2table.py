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
from dataset import Dataset

workbook_file = "C:/users/podengo/citrus/data/workbook.xslx"
filename_input_csv = "C:/users/podengo/git/citrus/data/am4ir/FloridaQatar_AM4IR_pilot_filtered.txt"

dsr = Dataset(dbms='csv',name=filename_input_csv, open_mode="r", encoding='utf-8')

rows = dsr.dict_reader()
for i0,row in enumerate(rows):
    print(i0)
