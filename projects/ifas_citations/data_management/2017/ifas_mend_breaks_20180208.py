'''

This code removes line breaks in field-delimited files
This tries to replace all returns with a single space character when a
return is found within a field value.

Save results as a .txt file.

Assume: each logical data row is delimited by the delimiter character,
and contains the same number of fields, provided by a parameter.
If that parameter is None,
the first physical line in the file must have NO line breaks and thus
also contain the correct number of fields and represent a logical line.
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

print("INFO: Using paths in sys.path:")
for i,sp in enumerate(sys.path):
    print("INFO: sys.paths[{}]={}".format(i,repr(sp)))

import codecs
from collections import OrderedDict

units = [
    'ABE',
    'AgEd',
    'Agron',
    'AniSci',
    'Citrus_REC',

    'Custom 8',
    'EntNem',
    'EnvHort',
    'Everglades_REC',
    'FYCS',

    'FLMedEnt',
    'FRED',
    'FoodSci',
    'FtLauder_REC',
    'Gulf_REC',

    'HortSci',
    'IndianRiv_REC',
    'MicroCell',
    'MidFL_REC',
    'NoFL_REC',

    'PlantPath',
    'Range_REC',
    'SFRC',
    'SoilWater',
    'SW_REC',

    'Trop_REC',
    'West_REC',
    'WildEco',
    'IFAS_Global',
]
'''
summary: get first line of input file in arg ifile,
delimit it by tabs, and simply return the count of the Number
of fields.
This program assumes that all rows must/should have that number or less
as some 'txt' input file lines, in practice do have less, because this
program monitors each field value and considers the end of a logical line
to be where a units value resides. All fields after such a value on a
physical input line are ignored, and if a unit name appears in a column
that is not the column count column, a warning is issued.
'''
def process_first_line(ifile=None,ofile=None,delim='\t'):
    me = 'process_first_line'
    first_line = ifile.readline()
    first_line = first_line[:-1]

    print(first_line, file=ofile)
    #remove trailing newline

    field_names = first_line.split(delim)
    ifas_unit_field_count = 0;
    for i,name in enumerate(field_names, start=1):
        if name.lower() == 'ifas unit':
            ifas_unit_field_count = i;
            break;

    #end for field_names

    if ifas_unit_field_count == 0:
        msg = (
            "{}: FATAL ERROR: No 'IFAS Unit' field found in first line."
            .format(me))
        raise ValueError(msg)

    # Enforce that IFAS Unit name is the last field
    return field_names[:ifas_unit_field_count]
#end def process_first_line

'''
Given a line with fewer than field_count fields, keep reading lines
from input file, assuming that the first 'field' in newly read lines
is NOT a distinct new field, but the string value is to be appended to
the last field of the prior line. If the total field count exceeds
field_count it is a fatal exception. If it is less than the field_count,
then continue to read another line to use to patch onto the prior line(s).
Return the iline when the total field count equals the field count param.

Add check: only try to mend line if output field count is 4 title
or 5 journal
'''
def mend_line(ifile=None, nil=None,output_fields=None, field_count=None,
    delim='\t', lfile=None, units=None, verbosity=1):

    me = 'mend_line'
    nof = len(output_fields)
    if verbosity > 0:
        print("{}: INFO: nil={} nof={} output_fields={}"
            .format(me,nil,nof,output_fields),file=lfile)

    if nof < 1 :
        msg = "{}: rejecting line {} with no fields".format(me,nil)
        raise ValueError(msg)
    elif nof >= field_count:
        msg = ("{}: line {} should have {} fields, reject line with {} fields"
            .format(me,nil,field_count,nof))
        raise ValueError("With field_count {}, reject line with {} fields"
            .format(field_count,nof))

    # mend line at most twice, else  may go too far.
    # only mend output field count 4 or 5
    while (1):
        mending_line = ifile.readline()
        if mending_line == '':
            # either end of file or just a blank line.....
            # we'll assume EOF, because we don't have a choice with the
            # while loop
            break
        nil += 1

        mending_line = mending_line[:len(mending_line)-1] #kill newline
        input_fields = mending_line.split(delim)
        nif = len(input_fields)

        # Only remove trailing empty fields for nof 4 title or 5 journal
        # else may remove valid ending empty fields
        # Consider: if nof == 5 or nof==4 and nif[1](journal) is not empty
        #if ( nof == 4 or nof ==5 ):
        if ( nof <= field_count -2 ):
            n_trailing_empty_fields = 0
            reversed_fields = input_fields[::-1]

            for i in range(nif):
                rv = reversed_fields[i]
                #if len(rv) > 0 and not rv.startswith("Manually"):
                if len(rv) > 0 and rv in units:
                      #found the citatino's final logical fields
                      if nif -i < field_count -1:
                          msg = ('ERROR:Line {}: unit in column {}, not {}'
                              .format(nil,nif -i + 1, field_count))
                      break;
                n_trailing_empty_fields += 1

            #Next, ignore the trailing empty fields
            input_fields = input_fields[:-n_trailing_empty_fields]
        #end check for journal or title field

        nif = len(input_fields)
        print("{}: INFO: Got mending line {} = {}"
            .format(me,nil,mending_line),file=lfile)

        # Append the first field value to the previous lines's
        # last collected field value.
        broken_field = output_fields[nof - 1]
        mended_field = broken_field + ' ' + input_fields[0]
        print("{}: INFO: Broken field was '{}', and mended is {}"
            .format(nil,broken_field,mended_field),file=lfile)
        output_fields[nof - 1] = mended_field

        # Append any extra fields on this new line to output_fields
        # -1 because first field value was not a new field.
        output_fields.extend(input_fields[1:])
        nof = len(output_fields)
        print("{}: INFO: nof={} after extending output fields with '{}'"
            .format(nil,nof,input_fields[1:]),file=lfile)
        #Last coupld of field may be null sometimes in this data, so add this..
        if nof >= field_count -2: # we have tried mended title and journal fields
            break;
    #end while
    output_line = delim.join(output_fields)

    if nof > field_count:
        msg =("{}:FATAL ERROR: Mended line has {} output fields={}, not required field_count of {}"
             .format(nil,nof,output_fields, field_count))
        msg2 = ("{}: FATAL ERROR HINT: are you missing IFAS UNIT on previous line?"
            .format(nil))
        print(msg, file=lfile)
        print(msg2, file=lfile)
        raise ValueError(msg + '\n' + msg2)
    #allow field_count to be less than total here
    return output_line
'''
Only mend breaks if the current nof is 4 or 5, as those are the Only
fields that can have breaks now.
'''
def mend_breaks(input_file_name="c:/rvp/downloads/2018_test4.txt",
   output_file_name='c:/rvp/downloads/unbroken.txt',delim='\t',
   lfile=None,verbosity=1):

    me = 'mend_breaks'
    ifn = input_file_name
    ofn = output_file_name

    if verbosity > 0:
        print("{}: INFO: using input file={}, output file={}".format(me,ifn,ofn),
            file=lfile)

    ifile = open(ifn, mode="r", encoding='utf-8-sig',  errors='ignore')
    with open(ofn, mode="w" ) as ofile:
      first_fields = process_first_line(ifile=ifile,ofile=ofile,delim=delim)
      field_count = len(first_fields)
      ifas_unit_index = field_count -1
      print("INFO: First line has {} fields = {}"
          .format(field_count, first_fields), file=lfile)
      # Parse a set of rows, each row made of of 'count' fields
      # and output a line for each one
      # first check the newline
      # if a line has 'too few' tab-separated fields, keep reading until
      # the number of FIELDS is satisfied.
      # error abort if a line's cumulative field count exceeds the number of
      # expected fields.
      nil = 1 # start at 1 because process_first_line already read that.
      while (1):
          iline = ifile.readline()
          if iline ==  '':
              break;

          nil += 1
          iline = iline[:len(iline)-1]  #kill newline
          fields = iline.split(delim)
          nif = len(fields)
          n_trailing_empty_fields = 0;
          # Reverse fields to seek a unit_name from the back, the
          # somewhat more frequent case for input lines
          reversed_fields = fields[::-1]
          has_unit = 0
          for i in range(nif):
              value = reversed_fields[i]
              if value in units:
                  has_unit = 1
                  unit_field_count = nif - i
              if len(value) > 0:
                  #found the final field with a non-empty value
                  break;
              n_trailing_empty_fields += 1

          if  n_trailing_empty_fields > 0 and fields[ifas_unit_index] in units:
              # This is really a partial line that has been artificially
              # padded with columns on the end, an artifact found in the
              # input files.
              # Cut off the emptry trailing fields:
              print("{}: WARNING: Line {} has {} trailing empty fields, line='{}'"
                  .format(me,nil, n_trailing_empty_fields, iline), file=lfile)
              # new fields  - remove the trailing empty fields
              fields = fields[:-n_trailing_empty_fields]
              # Now fewer fields
              nif = len(fields)

          if nif != field_count:
              print("{}: INFO: input Line has {} fields: '{}'"
                 .format(nil,nif,fields), file=lfile)

          if has_unit == 0:
              print(
                "{}: INFO: Broken line has {} fields='{}'"
                .format(nil,nif,fields), file=lfile)

              iline = mend_line(
                  ifile=ifile, lfile=lfile, nil=nil, output_fields=fields,
                  units=units, field_count=field_count, delim=delim)

              print("{}: INFO: Mended input line ='{}' with nif={}"
                .format(nil,iline, nif), file=lfile)
              fields = iline.split('\t')

              print(delim.join(fields),file=ofile)
          else:
              #Got an ifas unit on this line, not broken.
              if unit_field_count != field_count :
                  print("{}: ERROR: line has unit in column {}, not {}"
                      .format(nil,unit_field_count, field_count), file=lfile)
              print(delim.join(fields),file=ofile)
        #endfor nil,iline
      print("INFO: Finished reading {} logical lines from {}".format(iline,ifn),
          file=lfile)
      #end while
    ifile.close()
# end def mend_breaks()

# MAIN PROGRAM
def test(study_year=2017, input_file_basename="2017_All_Units_4.txt"):

    input_files_glob = (
      'unbroken.txt'.format(study_year))

    input_folder = etl.data_folder(
        linux='/home/robert/',
        windows="C:\\rvp\\",
        data_relative_folder=(
          'git/citrus/projects/ifas_citations/data/{}/'
          .format(study_year)))

    input_file_name="{}{}".format(input_folder,input_file_basename)
    #input_file_name="/home/robert/Downloads/2017_All_Units_4.txt"

    output_file_name="{}unbroken.txt".format(input_folder)

    log_file_name="{}log_mender.txt".format(input_folder)

    lfile = open(log_file_name, mode="w")

    mend_breaks(input_file_name=input_file_name,output_file_name=output_file_name,
        lfile=lfile)

    print("INFO: Done!", file=lfile)

# MAIN Program
testme=1
if testme == 1:
    test()
    sys.stdout.flush()
