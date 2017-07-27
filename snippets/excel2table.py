import sys, os, os.path, platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
print("sys.path={}".format(repr(sys.path)))
import datetime
import pytz
import os
import sys
from collections import OrderedDict
from dataset import *

workbook_file="C:/users/podengo/citrus/data/workbook.xslx"

sh_dict_reader = SheetDictReader(dbms='excel_srcn',workbook_file=workbook_file)
