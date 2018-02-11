'''
ifas_20180208_citations_inspect.py

This is a changed/different program as of 20171219 (compared to earlier versions)
altered now to handle a new type of ifas citations input file that
MSL is providing as input, which now has tab-separated input fields.

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

print("sys.path={}".format(repr(sys.path)))

sys.stdout.flush()
import etl
from pathlib import Path
from collections import OrderedDict
'''
Python3 code
20180208 - Robert V. Phillips
Testing with real MSL data, altered a bit to remove double-quotes
somehow inserted around the author value in MSL 20180208 input databases
- but no other field values.

20171219 - major modification to handle tab-separated fields on input file,
that MSL is now able to provide as input.
This is a nicer input, simpler to parse, but much code since prior version
20170530 must change...


TEST INPUT FILE NOTES:

Initial test FILENAME has last year's citations...
'''

'''
deprecated or renamed? Method ifas_citations_past():

<summary> Read a 'base' file of previous IFAS citations that are not to be
allowed in this year's batch of input.
Create and return

(1) dictionary 1 - dictionary keyed by line id (zfilled to 10 digits)
(2) dictionary 2 - keyed by IFAS citation DOI values.

For each dictarion rhe value for any key is a copy of the assocated
input citation line.

Note that not all citation lines have DOI values, and so the length of
dictionary 1 will always be greater or equal to the length of dictionary 2.

The dictionaries are used to detect duplicate citations attempted to be
filed as new articles for this year's batch of citations</summary>

NOTE: some issues with both word and writer fail to export the master docx
file to a completely valid utf-8 file format.

For example, if the first citation has a greek character that fails to be
exported as utf-8, it seems.
That detail needs to be resolved.
'''

from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlwt import easyxf
from xlrd import open_workbook

'''
class OutBookSheet is a simple excel workbook of type xls with one sheet.

'''
class OutBookSheet():

    '''
    Method __init__ creates a workbook with the given names in the list
    argument output_columns. It writes the first spreadsheet output row
    with the given output_column names, sets some error color styles.

    <param name='output_columns'>
         List of column names to associate with this new OutBookSheet().
    </param>
    <param name='output_workbook_name'>Name of output workbook.</param>
    '''
    def __init__(self, output_book_name=None, output_columns=None):
        # To save data, caller must use the self.book.save(filename) method
        # Note: and user MUST use the .xls suffix in that filename.
        # Though suffix xslx will work OK with LibreOffice, it causes Excel
        # 2013 to choke.
        required_args = ['output_book_name','output_columns']
        if not all(required_args):
            msg = "Missing a required arg from {}".format(required_args)
            raise ValueError(msg)
        self.work_book = xlwt.Workbook()
        self.sheet = self.work_book.add_sheet(output_book_name)
        self.output_book_name = output_book_name
        self.output_columns = output_columns
        self.d_type_style = {
        'warning' :  easyxf( 'pattern: pattern solid, fore_colour '
            'pale_blue; font: colour black, bold True;'),
        'error' :  easyxf( 'pattern: pattern solid, fore_colour '
            'yellow; font: colour black, bold True;'),
        'error2' :  easyxf( 'pattern: pattern solid, fore_colour '
            'rose; font: colour black, bold True;'),
        'error3' :  easyxf( 'pattern: pattern solid, fore_colour '
            'light_orange; font: colour black, bold True;'),
        'unparsed' : easyxf( 'pattern: pattern solid, fore_colour '
            'grey25; font: colour black, bold True;'),
        'valid' :  easyxf( 'pattern: pattern solid, fore_colour '
            'white; font: colour black, bold False;'),
        'original' :  easyxf( 'pattern: pattern solid, fore_colour '
            'light_green; font: colour black, bold False;'),
        }
        # Caller may use this to set a style per column before calling writerow
        self.d_column_style = {}
        # Header row
        for col_index,col_name in enumerate(self.output_columns):
            # Write first output row 0 with column names
            self.sheet.write(0, col_index, col_name)
            self.d_column_style[col_name] = None

        # Set 'cursor' of current outbook row to assist repeated writerow calls
        self.outbook_row_index = 1
        return

    '''
    Method OutBookSheet.writerow():
    <summary> Write a row with given column values in the given column styles.
    </summary>
    <param name='d_output'>
    Dictionary where key must be an output column name for this OutBookSheet,
    and value is an output value for that column.
    </param>
    <param name='d_column_style'>
    Dictionar. where key must be in self.output_columns, and value is an excel
    cell 'style value', typically used to provide a background color for a cell.
    </param>
    '''
    def writerow(self, d_output=None, d_column_style=None, verbosity=0):

        for column_index, column_key in enumerate(self.output_columns):
            column_value = d_output[column_key]
            if verbosity > 1:
                print ("outbook_writerow: row={},index={},key='{}',value='{}'"
                  .format(self.outbook_row_index,column_index, column_key,
                  column_value) )
            style = d_column_style.get(column_key, None)
            if style is None:
                self.sheet.write(self.outbook_row_index, column_index,
                  column_value.strip())
            else:
                if (verbosity > 0):
                    print("Writing a style for column '{}'".format(column_key))
                self.sheet.write(self.outbook_row_index, column_index,
                  column_value.strip(), style)
        self.outbook_row_index += 1
        return
    # end def writerow()
# end class OutBookSheet

'''
<summary name="CitationsInspector">

This object registers the annual IFAS citations input folders and
files, and has main method inspect() which inspects a year's worth of IFAS
'round1' citation data from the UF IFAS units.

It produces an output excel file for each unit that inputted data, with
various cell colorations and indications of warning and error conditions.

These output files files are for UF MSL staff and IFAS staff to review and
consider in making further manual refinements to each the unit-citations
file to register this year's scholarly publications in peer-reviwed
journals, authored by their employees.

Those files will comprise round2 orf input to this program

</summary>

<param> input_folder - main folder with a year of structured input
files, with filenames and subfolder structure as expcted in routing __init__
and object methods, </param>

<param name='past_pubs_file_name'> The name of the file (assumed to be in
the input_folder folder) containing the 'base' publications for
the previous year's period, used to check for duplicates across new inputs
this year and the previous year<./param>


'''
class CitationsInspector():

    '''
    Set up input parameters and file references for use by the inspect method.

    <param name='input_folder'>
    Root folder with a subfolder for each IFAS unit containing input files.
    </param>

    <param name='input_files_glob'>
    Glob pattern of input file filenames to use in the input folder(s)
    </param>

    <param name='past_pubs_file_name'>
    File name with DOIs of previous year's publications, used to reject as
    duplicates the lines in input files with the same DOI values.
    </param>

    Also read the base citations that have a doi mentioned and create a
    dictionary d_past_doi entry keyed by the doi with value being the entire
    line's text.

    Also keep every line in the d_base dictionary, keyed by index line number
    zfilled to 10 positions.
    '''
    def __init__(self, input_folder=None, input_files_glob=None,
        past_pubs_file_name=None, log_file=None, verbosity=0):

        required_args = [
          'input_folder','past_pubs_file_name', 'input_files_glob','log_file']
        if not all(required_args):
          msg = 'Missing a required arg from {}'.format(repr(required_args))
          raise ValueError(msg)
        self.log_file = log_file
        self.verbosity = verbosity
        self.input_folder = input_folder
        self.units_folder = '{}units/'.format(self.input_folder)
        #self.input_files_glob = 'IFAS*txt'
        self.input_files_glob = input_files_glob
        if verbosity > 0:
            print("{}:input_folder='{}', glob='{}'".format(me,self.input_folder,
              self.input_files_glob), file=self.log_file)

        self.input_paths = list(
          Path(self.input_folder).glob(self.input_files_glob))
        if len(self.input_paths) < 1:
          raise ValueError(
            "Found ZERO input files in input folder {} with glob {}"
            .format(input_folder, repr(input_files_glob)))
        self.past_pubs_file_name = past_pubs_file_name
        if verbosity > 0:
            print("Using past pubs file name ='{}'"
              .format(self.past_pubs_file_name), file=self.log_file)
        # Number of lines in last year's citations file to skip from the start
        self.base_skip_lines = 4
        self.d_base_index = {}
        self.d_past_doi = {}
        self.d_current_doi = {}
        self.d_unit_doi = {}
        n_file_citations = 0
        self.output_columns = [
          'unit','doi', 'authors',  'pub_year','title','journal','volume',
          'issue', 'pages', 'original_line',
        ]

        # input and save last year's citation info to use to check for
        # duplicates in this year's units
        read_file_name = str(self.past_pubs_file_name)
        with open(read_file_name, encoding="utf-8-sig",
            errors='replace', mode="r") as input_file:
            input_lines = input_file.readlines()

            for (index_line, line) in enumerate(input_lines):
                # Skip the normal number of header lines of this file and any
                # topic section line
                if index_line < self.base_skip_lines or len(line) < 50:
                    continue
                zfilled_index = str(index_line).zfill(10)
                self.d_base_index[zfilled_index] = line
                #line = xml_escape(line)
                index_doi = -1
                try:
                    index_doi = line.find("doi:")
                except Excepton as e:
                    print("{}: Reading file {}, Line {}: Skipping exception={}"
                        .format(me,read_file_name,index_line,repr(e.message)),
                        file=log_file)
                if index_doi < 0:
                    #print("Skip line index={}, {}. No doi found"
                    #      .format(index_line,line.encode('ascii','ignore')))
                    continue
                # Prior to 20171210 or so, the unit 'name' was not at the
                # tail end, which was ony the doi;
                # but now we scrape the unit name off the end, assuming
                # the doi starts at the tail and has NO spaces, so we
                # Parse by space, leaving the first such field as the
                # doi value and the following as the unit name.
                doi = line[index_doi:].replace('\n','').strip()
                unit = ''

                if verbosity > 0:
                    msg = (
                      "file={},line number={},with past_doi='{}',unit={}"
                      .format(self.past_pubs_file_name,index_line,doi,unit))
                    #MUST encode as below to handle printing misc chars in input
                    omsg = msg
                    print(msg.encode('ascii',errors='replace'),file=log_file)
                    #print(omsg) -- would cause UnicodeEncodeError -
                    # charmap codec cant encodt '\ufffd\''
                # SAVE past DOI to check for duplicates later
                self.d_past_doi[doi] = line
                n_file_citations += 1
            # end with open input_file
        #self.d_base = d_base
        return None

    # end __init__

    '''
    Works like inspect(), but re-done for new input file formats in 2017
    '''
    def inspect2017(self, study_year=None, output_folder=None
      ,output_book_name=None):

        me = 'inspect2017'
        log_file = self.log_file

        if output_folder is None:
            msg="{}:Required output_folder argument is missing.".format(me)
            raise ValueError(msg)

        self.inspect_output_folder = output_folder
        self.study_year = study_year

        # in year 2017, we get 11 fields per line
        fields_per_line = 11
        # Keep track of current year's doi values
        n_input_files = 0
        n_citations = 0
        n_dup_old = 0
        n_dup_cur = 0
        n_dup_unit = 0
        self.output_book_name = output_book_name

        # Read the input files
        print("{}: Found {} input files"
            .format(me,len(self.input_paths)),file=log_file)

        for i, path in enumerate(self.input_paths):

            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("{}: Processing input file {}, name={}"
                .format(me,i+1,input_file_name),file=log_file)
            n_input_files += 1

            #dot_index = path.name.find('.')
            #if dot_index > -1:
            #    output_book_name = path.name[:dot_index]
            #else:
            #    output_book_name = '{}'.format(path.name).replace(' ','_')

            print("Creating output workbook={}".format(output_book_name)
                ,file=log_file)

            self.out_book_sheet = OutBookSheet(
              output_book_name=output_book_name,
              output_columns=self.output_columns)

            d_type_style = self.out_book_sheet.d_type_style #convenient abbreviation
            n_file_citations = 0

            print("\n{}:Reading input file {} named {}".format(me,i,path.name),
                file=log_file)
            qmark_info = []

            # { NOTE: use encoding=utf-8-sig so on windows the BOM is properly ignored
            with open (str(input_file_name), encoding="utf-8-sig", errors='ignore', mode="r") as input_file:
                input_lines = input_file.readlines()
                n_unit_dois = 0
                # make a new dict per input_file/unit to detect local dups
                d_unit_doi = {}

                od_field_name__index = {
                    'authors': 0,
                    'pub_year': 1,
                    'title': 2,
                    'journal': 3,
                    'volume': 4,
                    'issue': 5,
                    'pages': 6,
                    'reference_type': 7,
                    'research_notes': 8,
                    'doi': 9,
                    'unit': 10,
                    }

                # Some vars to manage partial physical lines,
                # cf at_remove_txt_returns.py
                nof = 0
                nol = 0
                logical_fields = []
                # {
                for index_line, line in enumerate(input_lines):
                    # NOTE: Not realy "ORIGNAL_LINE", but replace the tabs with
                    # pipes so the line can display in an excel output cell
                    original_line=line.replace('\t','|')
                    line = line.replace('\n','')
                    fields = line.split('\t')
                    nif = len(fields)
                    if index_line == 0:
                        # This is the first line with header names
                        # and it always has all the fields, so
                        # first collect the N of fields
                        # and then skip it.
                        field_count = nif
                        continue

                    if nif != fields_per_line:
                        msg = (
                          "ERROR: skiping line {} with {} fields, not {}."
                          .format(index_line,nif,fields_per_line))
                        raise ValueError(msg)

                    print("\n{}:Processing at physical input line count {}"
                        .format(me,index_line),file=log_file)
                    d_column_output = {}
                    d_column_style = {}

                    # default style to unparsed
                    for column_name in self.output_columns:
                        d_column_style[column_name] = d_type_style['unparsed']

                    d_output = {}
                    n_file_citations += 1

                    # DOI
                    d_column_style['doi'] = d_type_style['valid']

                    # Check for missing DOI
                    # Use field name doi
                    fname = 'doi'
                    value = fields[od_field_name__index[fname]]
                    doi = value
                    print("----------------- GOT DOI={}".format(doi),
                        file=log_file)

                    if value is None or value == '':
                        print(
                          "WARNING: NO DOI given in input file='{}',"
                          " index_line={}, {}." .format(path.name, index_line,
                          line.encode('ascii',errors='ignore')),file=log_file)
                        d_column_style[fname] = d_type_style['warning']
                    else:
                        doi = value
                        n_unit_dois += 1
                        # A DOI STRING WAS FOUND
                        # Now do three doi duplication checks:
                        # DOI Dup Check (error2):
                        # check if doi already in the past, prev year's report
                        doi_past_dup = self.d_past_doi.get(doi, None)

                        if doi_past_dup is not None:
                            # ERROR: This doi duplicates one from base (previous) year
                            n_dup_old += 1
                            print("ERROR: Input file {}, index={},"
                              " has duplicate past doi '{}'".format(
                                input_file_name, index_line, doi_past_dup)
                                ,file=log_file)
                            d_column_style['doi'] = d_type_style['error2']

                        # DOI Dup Check  (error):
                        # check if doi already in current year
                        # for a unit report that has just been processed earlier
                        # in this loop over units

                        doi_current_dup = self.d_current_doi.get(doi, None)
                        if doi_current_dup is not None:
                            n_dup_cur += 1
                            print(
                              "ERROR: Input file {} index={} has duplicate"
                              " current year doi '{}'"
                              " to one in this year's input file name = '{}'"
                              .format(input_file_name,index_line,
                              doi, doi_current_dup),file=log_file)
                            d_column_style['doi'] = d_type_style['error']
                        else:
                            # Do not reset style here for doi - keep it from
                            # prior doi check
                            self.d_current_doi[doi] = input_file_name

                        # DOI Dup Check 3 (error3):
                        # check if doi already in previous line of this unit
                        # report that has just been processed earlier this read
                        # loop of the input file

                        doi_unit_dup = d_unit_doi.get(doi, None)
                        if doi_unit_dup is not None:
                            n_dup_unit += 1
                            print(
                              "ERROR: Input file {} line index={} has duplicate doi '{}'"
                              " to previous line {} in this unit's sheet."
                              .format(input_file_name,index_line,doi,doi_unit_dup)
                              ,file=log_file)
                            d_column_style['doi'] = d_type_style['error3']
                        else:
                            # Do not reset style here for doi - keep it from
                            # prior doi check
                            pass
                    d_output['doi'] = doi
                    # end processing the doi, if any, in input line

                    # Parse the rest of the fields
                    print("\n---Input file={}, index_line={}"
                      .format(input_file_name,index_line),file=log_file)

                    for fname in [
                      'authors','pub_year', 'title','journal',
                      'volume','issue','pages','unit'
                      ]:
                        try:
                          # Get some fields
                          findex = od_field_name__index[fname]
                          value = fields[od_field_name__index[fname]]
                        except Exception as e:
                            msg = ("input_file={},index_line={},field name='{}', findex={}, e='{}'"
                              .format(input_file_name,index_line,fname,findex,e))
                            raise ValueError(msg)

                        if value is None or value == '':
                            d_column_style[fname] = d_type_style['error']
                        else:
                            d_column_style[fname] = d_type_style['valid']
                        d_output[fname] = value.strip()

                    # Save the original line
                    d_output['original_line'] = original_line
                    d_column_style['original_line'] = d_type_style['original']

                    # Write spreadsheet row
                    self.out_book_sheet.writerow(d_output=d_output,
                        d_column_style=d_column_style)
                # } end for line in input_lines
            # } end with open input_file

            print("\n\n{}:Inspected input file={} with {} lines and {} dois."
              .format(me,input_file_name, len(input_lines), n_unit_dois )
              ,file=log_file)

            sys.stdout.flush()

            # Output excel workbook for this unit input file
            output_file_name = (
              "{}/{}_inspected.xls"
              .format(path.parents[0], output_book_name))
            sys.stdout.flush()
            print("Using output_file_name={}.".format(output_file_name),
                file=log_file)
            self.out_book_sheet.work_book.save(output_file_name)
            print("{}:SAVED EXCEL WORKBOOK {} in EXCEL OUTPUT FILE NAMED '{}'"
              .format(me,i,output_file_name),file=log_file)
            sys.stdout.flush()
        # end for i, path in enumerate self.input paths

        self.n_dup_old = n_dup_old
        self.n_dup_cur = n_dup_cur
        self.n_dup_unit = n_dup_unit
        print("{}: processed {} input files. Returning."
          .format(me,len(self.input_paths)),file=log_file)
        return
    '''
    Method inspect()

    <summary> Read the unit paths input files (as tab-delimited rows)
    of ifas citations, one per line, inspect them for problems.
    Then write out the output worksheet to file named
    "{}.xls".format(out_book_name) to the output folder.
    It may be the same directory that holds the input file(s).
    </summary>

    <param name="input_file"> input file with multiple citations </param>
    <param name=output_folder>ouput folder to contain output excel files
    with same lines as in excel input files, with added indicators
    for violations/warnings per line/citation
    </param>
    '''
    def inspect(self, study_year=None, output_folder=None
      ,output_book_name=None):

        me = 'inspect'
        if output_folder is None:
            msg="{}:Required output_folder argument is missing.".format(me)
            raise ValueError(msg)

        self.inspect_output_folder = output_folder
        self.study_year = study_year

        # Keep track of current year's doi values
        n_input_files = 0
        n_citations = 0
        n_dup_old = 0
        n_dup_cur = 0
        n_dup_unit = 0
        self.output_book_name = output_book_name
        print("{}: Found {} input files".format(me,len(self.input_paths)))
        for i, path in enumerate(self.input_paths):

            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("{}: Processing input file {}, name={}"
                .format(me,i+1,input_file_name))
            n_input_files += 1

            #dot_index = path.name.find('.')
            #if dot_index > -1:
            #    output_book_name = path.name[:dot_index]
            #else:
            #    output_book_name = '{}'.format(path.name).replace(' ','_')

            print("Creating output workbook={}".format(output_book_name))
            self.out_book_sheet = OutBookSheet(
              output_book_name=output_book_name, output_columns=self.output_columns)
            d_type_style = self.out_book_sheet.d_type_style #convenient abbreviation
            n_file_citations = 0

            print("\n{}:Reading input file {} named {}".format(me,i,path.name))
            qmark_info = []

            # { NOTE: use encoding=utf-8-sig so on windows the BOM is properly ignored
            with open (str(input_file_name), encoding="utf-8-sig", errors='ignore', mode="r") as input_file:
                input_lines = input_file.readlines()
                n_unit_dois = 0
                # make a new dict per input_file/unit to detect local dups
                d_unit_doi = {}

                if study_year == 2016:
                    od_field_name__index = {
                        'unit': 0,
                        'authors': 1,
                        'pub_year': 2,
                        'title': 3,
                        'journal': 4,
                        'volume': 5,
                        'issue': 6,
                        'pages': 7,
                        'doi': 8,
                    }
                else: # assume study year 2017 for Now
                    od_field_name__index = {
                        'authors': 1,
                        'pub_year': 2,
                        'title': 3,
                        'journal': 4,
                        'volume': 5,
                        'issue': 6,
                        'pages': 7,
                        'reference_type': 7,
                        'research_notes': 7,
                        'doi': 10,
                        'unit': 11,
                    }

                # Some vars to manage partial physical lines,
                # cf at_remove_txt_returns.py
                nof = 0
                nol = 0
                logical_fields = []
                # {
                for index_line, line in enumerate(input_lines):
                    original_line=line.replace('\t','|')
                    line = line.replace('\n','')
                    fields = line.split('\t')
                    nif = len(fields)
                    if index_line == 0:
                        # First line has header names, so skip it.
                        # Here however, it alwasy has all the fields, so
                        # first collect the N of fields
                        field_count = nif
                        continue

                    if nif == 1:
                        # Handle artifact of user-inputted newlines
                        f = fields[0]
                        logical_fields [nof-1] = logical_fields[nof-1] + f
                    elif nof + nif == field_count + 1:
                        fields = fields[1:]
                        nof += nif - 1
                    else:
                        logical_fields.extend(fields)
                        nof += nif
                        continue;
                    # if nof equals field_count, logical_fields are full/ready
                    if nof > field_count:
                        msg = "Line {} adds up to too many fields."
                        raise ValueError(msg)
                    elif nof == field_count:
                        nof = 0
                        fields = logical_fields;
                        original_line = '|'.join(fields)

                    print("\nProcessing at physical input line count {}"
                        .format(index_line))
                    d_column_output = {}
                    d_column_style = {}

                    # default style to unparsed
                    for column_name in self.output_columns:
                        d_column_style[column_name] = d_type_style['unparsed']

                    d_output = {}
                    n_file_citations += 1

                    # DOI
                    d_column_style['doi'] = d_type_style['valid']

                    # Check for missing DOI
                    fname = 'doi'
                    value = fields[od_field_name__index[fname]]
                    doi = value
                    print("----------------- GOT DOI={}".format(doi))

                    if value is None or value == '':
                        print(
                          "WARNING: NO DOI given in input file='{}',"
                          " index_line={}, {}." .format(path.name, index_line,
                          line.encode('ascii',errors='ignore')))
                        d_column_style[fname] = d_type_style['warning']
                    else:
                        doi = value
                        n_unit_dois += 1
                        # A DOI STRING WAS FOUND
                        # Now do three doi duplication checks:
                        # DOI Dup Check (error2):
                        # check if doi already in the past, prev year's report
                        doi_past_dup = self.d_past_doi.get(doi, None)

                        if doi_past_dup is not None:
                            # ERROR: This doi duplicates one from base (previous) year
                            n_dup_old += 1
                            print("ERROR: Input file {}, index={},"
                              " has duplicate past doi '{}'".format(
                                input_file_name, index_line, doi_past_dup))
                            d_column_style['doi'] = d_type_style['error2']

                        # DOI Dup Check  (error):
                        # check if doi already in current year
                        # for a unit report that has just been processed earlier
                        # in this loop over units

                        doi_current_dup = self.d_current_doi.get(doi, None)
                        if doi_current_dup is not None:
                            n_dup_cur += 1
                            print(
                              "ERROR: Input file {} index={} has duplicate"
                              " current year doi '{}'"
                              " to one in this year's input file name = '{}'"
                              .format(input_file_name,index_line,
                              doi, doi_current_dup))
                            d_column_style['doi'] = d_type_style['error']
                        else:
                            # Do not reset style here for doi - keep it from
                            # prior doi check
                            self.d_current_doi[doi] = input_file_name

                        # DOI Dup Check 3 (error3):
                        # check if doi already in previous line of this unit
                        # report that has just been processed earlier this read
                        # loop of the input file

                        doi_unit_dup = d_unit_doi.get(doi, None)
                        if doi_unit_dup is not None:
                            n_dup_unit += 1
                            print(
                              "ERROR: Input file {} line index={} has duplicate doi '{}'"
                              " to previous line {} in this unit's sheet."
                              .format(input_file_name,index_line,doi,doi_unit_dup))
                            d_column_style['doi'] = d_type_style['error3']
                        else:
                            # Do not reset style here for doi - keep it from
                            # prior doi check
                            pass
                    d_output['doi'] = doi
                    # end processing the doi, if any, in input line

                    # Parse the rest of the fields
                    print("\n---Input file={}, index_line={}"
                      .format(input_file_name,index_line))

                    for fname in [
                      'authors','pub_year', 'title','journal',
                      'volume','issue','pages','unit'
                      ]:
                        # Get the authors
                        value = fields[od_field_name__index[fname]]

                        if value is None or value == '':
                            d_column_style[fname] = d_type_style['error']
                        else:
                            d_column_style[fname] = d_type_style['valid']
                        d_output[fname] = value.strip()

                    # Save the original line
                    d_output['original_line'] = original_line
                    d_column_style['original_line'] = d_type_style['original']

                    # Write spreadsheet row
                    self.out_book_sheet.writerow(d_output=d_output,
                        d_column_style=d_column_style)
                # } end for line in input_lines
            # } end with open input_file

            print("\n\n{}:Inspected input file={} with {} lines and {} dois."
              .format(me,input_file_name, len(input_lines), n_unit_dois ))

            sys.stdout.flush()

            # Output excel workbook for this unit input file
            output_file_name = (
              "{}/{}_inspected.xls"
              .format(path.parents[0], output_book_name))
            sys.stdout.flush()
            print("Using output_file_name={}.".format(output_file_name))
            self.out_book_sheet.work_book.save(output_file_name)
            print("{}:SAVED EXCEL WORKBOOK {} in EXCEL OUTPUT FILE NAMED '{}'"
              .format(me,i,output_file_name))
            sys.stdout.flush()
        # end for i, path in enumerate self.input paths

        self.n_dup_old = n_dup_old
        self.n_dup_cur = n_dup_cur
        self.n_dup_unit = n_dup_unit
        print("{}: processed {} input files. Returning."
          .format(me,len(self.input_paths)))
        return
    # end inspect()
# end class CitationsInspector

'''
method run() - run the ifas citations inspectior
<param name='study_year'>
The integer 4 digit A.D. year, aka C.E. year in which the input items
are supposed to have been published.
</param>
<param name='study'>
Value 'year_end' means it is the year_end study
</param>
'''

def run(study_year=2016,  past_pubs_file_name=None,
    study_type='year_end'):

    me = 'run'
    required_args = [ study_year, past_pubs_file_name, study_type]
    if not all(required_args):
        msg="Not all required args given: {}".format(required_args)
        raise ValueError(msg)

    print("{}: Starting with study_year={}, past_pubs_file_name={}"
        .format(me, study_year, past_pubs_file_name))

    if study_type not in ['year_end','normal']:
        msg="Invalid study type={}. Error.".format(study)
        raise ValueError(msg)

    if study_year == 2016:

        if study_type == 'normal':
            # In 2016, we read input files under inputs_round1/units
            input_files_glob = 'IFAS*txt'
            input_folder = etl.data_folder(linux='/home/robert', windows='U:',
                data_relative_folder='/data/ifas_citations/{}/inputs_round1/units/'
                .format(study_year))
        else:
            # study_type is 'year_end'
            # here we use as input the yearly base_info .txt file
            input_files_glob = '{}_Master_List_Final.txt'.format(study_year)

            # Manual insertion 20171212 - got new file from Suzanne to use for 2016,
            # via email,and I copied it to windows folder assumed here
            input_files_glob = (
              '{}_IFAS_All_Unit_List_original_3.txt'.format(study_year))

            input_folder = etl.data_folder(linux='/home/robert', windows='U:',
              data_relative_folder='/data/ifas_citations/{}/base_info/'
              .format(study_year))

    elif study_year == 2017:
        if study_type == 'normal':

            msg = (
              "{}: Got study_type='{}', but in year 2017 only "
              "study_type 'year_end' is used"
                .format(me))
            raise ValueError(msg)

        else:
            # study_type is 'year_end'
            # In 20171212 - got new file type via email from Suzanne to
            # use as input with 'broken fields' where users inserted return
            # characters in titles, journals, dois.
            # So new program ifas_mend_lines.py was created to fix
            # any such 'broken' lines and to produce one big file,
            # unbroken.txt, inputted here.

            input_files_glob = (
              'unbroken.txt'.format(study_year))

            input_folder = etl.data_folder(
                linux='/home/robert/',
                windows='/c/Users/robert/',
                data_relative_folder=(
                  'git/citrus/projects/ifas_citations/data/{}'
                  .format(study_year)))
        # end year_end study_type
    # end study_year clauses

    log_file_name = "{}/log_inspector.txt".format(input_folder)
    log_file = open(log_file_name, mode='w')

    # Example for params for a normal run comparing this years final list of
    # pubs to previous year and checking for dups, etc...

    inspector = CitationsInspector(past_pubs_file_name=past_pubs_file_name
        ,input_folder=input_folder, input_files_glob=input_files_glob,
        log_file=log_file)

    # Optional param output_folder defaults to input_folder if not given
    if study_year > 2016:
        inspector.inspect2017(study_year=study_year,output_folder=input_folder,
          output_book_name="IFAS_citations_2017")
    else:
        inspector.inspect(study_year=study_year,output_folder=input_folder,
          output_book_name="IFAS_citations_2017")

    print("Got d_past_doi length='{}'".format(len(inspector.d_past_doi))
        ,file=log_file)

    n_dup_old = inspector.n_dup_old
    n_dup_cur = inspector.n_dup_cur
    n_dup_unit = inspector.n_dup_cur

    print("Skipped {} dois of older ones, {} of current. Done!"
      .format(n_dup_old,n_dup_cur),file=log_file)

# RUN
# For testing study_year 2017, use past_year 2015 until we get year 2016 test data
past_year = 2015
study_year = 2017

# Set some vars to specify year 2015 past pubs, and change Later
# for 2016 past pubs file

past_pubs_folder = etl.data_folder(linux='/home/robert/', windows='U:',
    data_relative_folder = ('git/citrus/projects/ifas_citations/data/'
    '{}/base_info/'.format(past_year)))

# past_file_name = 'ifas-{}-pubs_by_topic-1.txt'.format(past_year)
past_file_name = '2015_master_base.txt'.format(past_year)

# past_pubs_file_name: is the absolute path of the input file with last
# year's dois to flag as a duplicate error if any is found in
# this year's input data
past_pubs_file_name = '{}{}'.format(past_pubs_folder, past_file_name)

print("MAIN: using past_year = {}, study_year = {}, past_pubs_file_name={}"
    .format(past_year,study_year,past_pubs_file_name))

run(study_year=2017,
    past_pubs_file_name=past_pubs_file_name)
