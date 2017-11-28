#at_remove_txt_returns.py
#echo input file to output but remove return characters

import sys,os, os.path,platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))

print("Using paths in sys.path:")
for i,sp in enumerate(sys.path):
    print("sys.paths[{}]={}".format(i,repr(sp)))
import pymarc
from pymarc import MARCReader
#import etl
import codecs
from collections import OrderedDict

#Try some cleanup of  funky data from 'save results as' of SSMS on
#database archiviststoolkit, table accessions (and others) circa
# 20181129 - the first row seems like it is reliable to count tabs to determine
# the number of valid fields per row of data.
# thereafter, we find in the input file that newlines are inserted
# into the data that we want to replace with nothing.
# so we need to count tabs upon reading input and parse them indicator
# real lines/rows, removing newlines in every input value.
# on output end each line also with sentinel like "$%@"
# to possible disambiguate some cases ..
#
#Input file

def process_first_line(ifile=None):

    first_line = ifile.readline()
    #remove trailing newline
    first_line = first_line[:-1]

    field_names = first_line.split('\t')
    for count,fn in enumerate(field_names, start=1):
        print("{}: fn='{}'".format(count,fn))

    return count

# MAIN SETUP AND RUN
file_name="c:/rvp/documents/at_accessions_input.txt"

with open(file_name, mode="r", encoding='utf-8-sig',  errors='ignore') as ifile:

  print("starting using file_name={}".format(file_name))
  field_count = process_first_line(ifile=ifile)
  print("First line has {} fields".format(field_count))

  #Parse a set of rows, each row made of of 'count' fields
  #and output a line for each one
  #first check the newline
  #if a line has 'too few' tab-separated fields, keep reading until the number of FIELDS
  #is satisfied.
  #error abort if a line's cumulative field count exceeds the number of
  #expected fields.
  for line in ifile:
      print("Got line='{}'".format(line))

print("done!")
