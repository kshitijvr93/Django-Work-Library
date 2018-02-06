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

import sys,os, os.path,platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))

print("Using paths in sys.path:")
for i,sp in enumerate(sys.path):
    print("sys.paths[{}]={}".format(i,repr(sp)))
#import pymarc
#from pymarc import MARCReader
#import etl
import codecs
from collections import OrderedDict

l_unit = [
    'AgEd',
    'Agron',
    'Citrus_REC',
    'Custom 8',
    'FRED',
]
'''
summary: get first line of input file in arg ifile,
delimit it by tabs, and simply return the count of the Number
of fields.
This program assumes that all rows must/should have that number.
'''
def process_first_line(ifile=None,ofile=None,delim='\t'):

    first_line = ifile.readline()
    first_line = first_line[:len(first_line)-1]  #kill newline
    print(first_line, file=ofile)
    #remove trailing newline
    first_line = first_line[:-1]

    field_names = first_line.split(delim)
    for count,fn in enumerate(field_names, start=1):
        print("{}: fn='{}'".format(count,fn))
    return count

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
def  mend_line(ifile=None, output_fields=None, field_count=None, delim='\t'):
    me = 'mend_line'
    nof = len(output_fields)
    print("{} Got arg {} output_fields={}".format(me,nof,output_fields))

    if nof < 1 :
        raise ValueError("mend_line rejects lines with no fields")
    elif nof >= field_count:
        raise ValueError("With field_count {}, reject line with {} fields"
            .format(field_count,nof))

    # mend line at most twice, else  may go too far.
    # only mend output field count 4 or 5
    while (1):
        next_line = ifile.readline()
        if next_line is None:
            break
        next_line = next_line[:len(next_line)-1] #kill newline
        input_fields = next_line.split(delim)
        nif = len(input_fields)

        # Only remove trailing empty fields for nof 4 title or 5 journal
        # else may remove valid ending empty fields
        # Consider: if nof == 5 or nof==4 and nif[1](journal) is not empty
        if ( nof == 4 or nof ==5 ):
            n_trailing_empty_fields = 0
            reverse_fields = input_fields[::-1]

            for i in range(nif):
                rv = reverse_fields[i]
                #if len(rv) > 0 and not rv.startswith("Manually"):
                if len(rv) > 0 and not rv.startswith('Manually'):
                      #found the final field with a non-empty value
                      break;
                n_trailing_empty_fields += 1

            #Next, ignore the trailing empty fields
            input_fields = input_fields[:-n_trailing_empty_fields]
        #end check for journal or title field

        nif = len(input_fields)
        print("Got mending line with {} input fields={}".format(nif,input_fields))

        # Append the first field value to the previous lines's
        # last collected field value.
        broken_field = output_fields[nof - 1]
        mended_field = broken_field + ' ' + input_fields[0]
        print("Broken field was '{}', and mended is {}"
            .format(broken_field,mended_field))
        output_fields[nof - 1] = mended_field

        # Append any extra fields on this new line to output_fields
        # -1 because first field value was not a new field.
        output_fields.extend(input_fields[1:])
        nof = len(output_fields)
        print("nof={} after extending output fields with '{}'"
            .format(nof,input_fields[1:]))
        #Last coupld of field may be null sometimes in this data, so add this..
        if nof > 5: # we have tried mended title and journal fields
            break;
    #end while
    output_line = delim.join(output_fields)

    if nof > field_count:
        msg =("We have {} output fields={}, not required field_count of {}"
             .format(nof,output_fields, field_count))
        raise ValueError(msg)
    #allow field_count to be less than total here
    return output_line
'''
Only mend breaks if the current nof is 4 or 5, as those are the Only
fields that can have breaks now.
'''
def mend_breaks(input_file_name="c:/rvp/downloads/broken_lines.txt",
   output_file_name='c:/rvp/downloads/unbroken.txt',delim='\t'):

    me = 'mend_breaks'
    ifn = input_file_name
    ofn = output_file_name

    print("{}: using input file={}, output file={}".format(me,ifn,ofn))

    ifile = open(ifn, mode="r", encoding='utf-8-sig',  errors='ignore')
    with open(ofn, mode="w" ) as ofile:
      field_count = process_first_line(ifile=ifile,ofile=ofile,delim=delim)
      print("First line has {} fields".format(field_count))
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
          if iline is None:
              break
          nil += 1
          iline = iline[:len(iline)-1]  #kill newline
          fields = iline.split('\t')
          nif = len(fields)
          n_trailing_empty_fields = 0;
          reverse_fields = fields[::-1]

          for i in range(nif):
              if len(reverse_fields[i]) > 0:
                  #found the final field with a non-empty value
                  break;
              n_trailing_empty_fields += 1

          if n_trailing_empty_fields  > 4:

              # empirically good for ifas ciations data
              # this is really a partial line that has been artificially
              # padded. Cut off the emptry trailing fields:
              print("Line {} has {} trailing empty fields of {} fields,line line='{}'"
                  .format(nil, n_trailing_empty_fields, nif,iline))
              # new fields  - remove the trailing empty fields
              fields = fields[:-n_trailing_empty_fields]
              # Now fewer fields
              nif = len(fields)

          print("Input Line {} has {} fields: '{}'".format(nil,nif,fields))

          if nif < field_count:
              if nif == 1 and len(field[0]) == 0:
                  break; # last line
              print(
                "Got broken input line number {} of {} fields='{}'"
                .format(nil,nif,fields))

              iline = mend_line(ifile=ifile, output_fields=fields,
                field_count=field_count, delim=delim)

              print("Mended input line {}='{}'\n --- iline {} with nif={}"
                .format(nil,iline,nil,nif))
              fields = iline.split('\t')

              print(delim.join(fields),file=ofile)
        #endfor nil,iline
      print("Finished reading {} logical lines from {}".format(iline,ifn))
      #end while
    ifile.close()
# end def mend_breaks()

mend_breaks()

print("done!")
sys.stdout.flush()
