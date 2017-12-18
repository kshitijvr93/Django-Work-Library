#at_remove_txt_returns.py
# exploratory  code that is not promising, so abandoned. See notes.
#echo input file to output but remove return characters
# This was/is exploratory code to try to undo the odd outputs of ssms when doubling
# save results as a .txt file... when it insists on writing newlines for certain
#subfields of database fields.
# CONCLUSION: this is too idiosyncratic behavior of SSMS/ SQL Server stuff, so
# going ahead with more generally useful code development that will do this
# by connecting to the database with python code to dump TABLES
# to files, bypassing use of SSMS.
# rvp - 20171129

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
'''
summary: get firt line of input file in arg ifile,
delimit it by tabs, and simply return the count of the Number
of fields.
This program assumes that all rows must/should have that number.
'''
def process_first_line(ifile=None):

    first_line = ifile.readline()
    #remove trailing newline
    first_line = first_line[:-1]

    field_names = first_line.split('\t')
    for count,fn in enumerate(field_names, start=1):
        print("{}: fn='{}'".format(count,fn))

    return count

# MAIN SETUP AND RUN
ifn ="c:/rvp/documents/at_accessions_input.txt"
print("Starting using input file name={}".format(ifn))

ifile = open(ifn, mode="r", encoding='utf-8-sig',  errors='ignore')
field_count = process_first_line(ifile=ifile)
print("First line has {} fields".format(field_count))

ofn ="c:/rvp/documents/at_accessions_output.txt"
with open(ofn, mode="w" ) as ofile:
  #Parse a set of rows, each row made of of 'count' fields
  #and output a line for each one
  #first check the newline
  #if a line has 'too few' tab-separated fields, keep reading until the number of FIELDS
  #is satisfied.
  #error abort if a line's cumulative field count exceeds the number of
  #expected fields.
  output_fields = []
  nof = 0
  nol = 0
  for nil, iline in enumerate(ifile, start=2):
      fields = iline.split('\t')
      nif = len(fields)
      print("Got input line {}='{}'\n --- iline {} with nif={},nof={}"
        .format(nil,iline,nil,nif,nof))

      if nif == 1 :
          # Here, this is an 'artifact' line of silly ssms output
          # of some fields with newlines, so we append to last
          #output field. We do not increment nof.
          f = fields[0]
          print("Appending subfield='{}'".format(f))
          f=f.replace('\n','|')
          output_fields[nof-1] = output_fields[nof-1] + f
          nif = 0
          #will next syntax work?
          #output_fields[nof-1] += fields[0]
      elif nof + nif == field_count +1:
          #This is the first line after the artifact-lines, so a secondary
          #artificat. We ignore the first field
          fields = fields[1:]
          nof += nif - 1
      else:
          #here we have multiple fields, in a line from ssms results,
          #so experience shows we extend the fields
          output_fields.extend(fields)
          nof += nif

      print("Input line {}. nif={},nof={}, fields={}".format(nil,nif,nof,fields))
      if nof  > field_count:
          msg = ("Abort. Line {} accrues {} fields, too many. {}"
          .format(nil, nof,iline))
          sys.stdout.flush()
          raise ValueError(msg)
      elif nof == field_count:
          nol += 1
          print("{}:{}".format(nol,output_fields),file=ofile)
          output_fields=[]
          nof = 0
      #
    #endfor nil,iline
  print("Finished reading {} lines from {}".format(iline,ifn))
  #end while
close(ifile)

print("done!")
sys.stdout.flush()
