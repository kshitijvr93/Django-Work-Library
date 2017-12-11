import sys, os, os.path, platform

def register_modules():
    platform_name = platform.system().lower()
    if platform_name == 'linux':
        modules_root = 'tbd'
        raise ValueError("MISSING: Enter code here to define modules_root")
    else:
        # assume rvp office pc running windows
        modules_root="C:\\rvp\\"
    sys.path.append('{}git/citrus/modules'.format(modules_root))
    return
register_modules()

print("sys.path={}".format(repr(sys.path)))

sys.stdout.flush()
import etl

'''
20170530 - Robert V. Phillips
Python3 code
This file holds methods used to inspect and report problematic IFAS citations
that are received from the 28 IFAS units

TEST INPUT FILE NOTES:
Initial test FILENAME is 2015_master_base.txt, but original name left by
MSL staff is "2015 Master List_dedup.docx", which I opened wth word and
saved as a utf8 file and renamed to 2015_master_base.txt -

NOTE: the utf8 conversion seems to have errors, should revisit later.
There are no tabs in this file to delineate authors, etc, so must parse it
fully.

At first, just need to skim doi values that seem pretty uniformly to be
prefixed by "doi: ", so that's a start.
'''

'''
Method ifas_citations_base():

<summary> Read a 'base' file of previous IFAS citations that are not to be
allowed in this year's batch of input.
Create and return
(1) a dictionary keyed by line id (zfilled to 10 digits)
(2) and keyed by IFAS citation DOI values.
The value for key of each dictionary is a copy of the input citation line.

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
<summary>This object registers the annual IFAS citations input folders and
files, and has main method inspect() which inspects a year's worth of IFAS
'round1' citation data from the UF IFAS units.
It produces an output excel file for each unit that inputted data, with
various cell colorations and indications of warning and error conditions.

These files are for UF MSL staff and IFAS staff to review and consider in
making further manual refinements to each the unit-citations file to
register this year's scholarly publications in peer-reviwed journals,
authored by their employees.

Those files will comprise round2 orf input.
</summary>

<param> input_folder - main folder with a year of structured input
files, with filenames and subfolder structure as expcted i routing __init__
and object methods, </param>

<param name='base_pubs_file_name'> The name of the file (assumed to be in
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
    Glob pattern of input file filenames
    </param>

    <param name='base_pubs_file_name'>
    File name with DOIs of previous year's publications, used to reject as
    duplicates the lines in input files with the same DOI values.
    </param>

    Also read the base citations that have a doi mentioned and create a
    dictionary d_base_doi entry keyed by the doi with value being the entire
    line's text.

    Also keep every line in the d_base dictionary, keyed by index line number
    zfilled to 10 positions.
    '''
    def __init__(self, input_folder=None, input_files_glob=None
        , base_pubs_file_name=None, verbosity=1):
        required_args = [
          'input_folder','base_pubs_file_name', 'input_file_glob']
        if not all(required_args):
          msg = 'Missing a required arg from {}'.format(repr(required_args))
          raise ValueError(msg)
        self.verbosity = verbosity
        self.input_folder = input_folder
        self.units_folder = '{}units/'.format(self.input_folder)
        #self.input_files_glob = 'IFAS*txt'
        self.input_files_glob = input_files_glob
        if verbosity > 0:
            print("Inputs_folder='{}', glob='{}'".format(self.input_folder,
              self.input_files_glob))

        self.input_paths = list(
          Path(self.input_folder).glob(self.input_files_glob))
        if len(self.input_paths) < 1:
          raise ValueError(
            "Found ZERO input files in input folder {} with glob {}"
            .format(input_folder, input_files_glob))
        self.base_pubs_file_name = base_pubs_file_name
        if verbosity > 0:
            print("Using base pubs file name ='{}'"
              .format(self.base_pubs_file_name))
        # Number of lines in last year's citations file to skip from the start
        self.base_skip_lines = 4
        self.d_base_index = {}
        self.d_base_doi = {}
        self.d_current_doi = {}
        self.d_unit_doi = {}
        n_file_citations = 0
        self.output_columns = [
          'doi', 'authors',  'pub_year','title','journal','volume','issue',
          'page_range', 'original_line',
        ]

        # input and save last year's citation info to use to check for
        # duplicates in this year's units
        with open (str(self.base_pubs_file_name), encoding="utf-8-sig",
            errors='replace', mode="r") as input_file:
            input_lines = input_file.readlines()

            for (index_line, line) in enumerate(input_lines):
                # Skip the normal number of header lines of this file and any
                # topic section line
                if index_line < self.base_skip_lines or len(line) < 50:
                    # print("Skipping base citations file context line='{}'"
                    # .format(line))
                    continue
                zfilled_index = str(index_line).zfill(10)
                self.d_base_index[zfilled_index] = line
                #line = xml_escape(line)
                #print("Got line='{}'.,eline='{}'".format(line,eline))
                index_doi = -1
                try:
                    index_doi = line.find("doi:")
                except Excepton as e:
                    print("Skipping exception={}".format(repr(e.message)))
                    pass
                if index_doi < 0:
                    #print("Skip line index={}, {}. No doi found"
                    #      .format(index_line,line.encode('ascii','ignore')))
                    continue
                doi = line[index_doi:].replace('\n','').strip()
                if verbosity > 0:
                    msg = ("file={},line number={},Saving base_doi='{}'"
                          .format(self.base_pubs_file_name,index_line,doi))
                    #MUST encode as below to handle printing misc chars in input
                    omsg = msg
                    print(msg.encode('ascii',errors='replace'))
                    #print(omsg) -- would cause UnicodeEncodeError -
                    # charmap codec cant encodt '\ufffd\''
                # SAVE BASE DOI to check for duplicates later
                self.d_base_doi[doi] = line
                n_file_citations += 1
            # end with open input_file
        #self.d_base = d_base
        return None

    # end __init__

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
    def inspect(self, output_folder=None):

        if output_folder is None:
            msg="Required output_folder argument is missing."
            raise ValueError(msg)

        self.inspect_output_folder = output_folder
        me = 'inspect'

        # Keep track of current year's doi values
        n_input_files = 0
        n_citations = 0
        n_dup_old = 0
        n_dup_cur = 0
        n_dup_unit = 0
        print("{}: Found {} input files".format(me,len(self.input_paths)))
        for i,path in enumerate(self.input_paths):
            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("Processing input file {}, name={}"
                .format(i+1,input_file_name))
            n_input_files += 1

            dot_index = path.name.find('.')
            if dot_index > -1:
                output_book_name = path.name[:dot_index]
            else:
                output_book_name = '{}'.format(path.name).replace(' ','_')
            print("Creating ouput workbook={}".format(output_book_name))
            self.out_book_sheet = OutBookSheet(
              output_book_name=output_book_name, output_columns=self.output_columns)
            d_type_style = self.out_book_sheet.d_type_style #convenient abbreviation
            n_file_citations = 0
            print("\nReading input file {}".format(path.name))
            qmark_info = []
            # { NOTE: use encoding=utf-8-sig so on windows the BOM is properly ignored
            with open (str(input_file_name), encoding="utf-8-sig", errors='ignore', mode="r") as input_file:
                input_lines = input_file.readlines()
                n_unit_dois = 0
                d_unit_doi = {} # make a new dict per unit to detect local dups
                # {
                for index, line in enumerate(input_lines):
                    line = line.replace('\n','')
                    index_line = index + 1
                    print("\nReading input line count {}".format(index_line))
                    skip_remaining_parsing = 0

                    d_column_output = {}
                    d_column_style = {}

                    # default style to unparsed
                    for column_name in self.output_columns:
                        d_column_style[column_name] = d_type_style['unparsed']
                    d_output = {}
                    n_file_citations += 1

                    # DOI

                    # Default to column style for valid in this case 'doi'
                    d_column_style['doi'] = d_type_style['valid']

                    # Check for missing DOI
                    index_doi = line.find("doi:")
                    if index_doi < 0:
                        print(
                          "WARNING: NO DOI given in input file='{}',"
                          " index_line={}, {}." .format(path.name, index_line,
                          line.encode('ascii',errors='ignore')))

                        doi = "'{}:line={}".format(path.name, index_line)
                        d_column_style['doi'] = d_type_style['warning']
                    else:
                        # A DOI STRING WAS FOUND
                        doi = line[index_doi:]
                        line = line[:index_doi] #keep the non-doi part of the line
                        n_unit_dois += 1

                        # Three doi dup checks:
                        # DOI Dup Check (error2):
                        # check if doi already in the base, prev year's report
                        doi_base_dup = self.d_base_doi.get(doi, None)
                        if doi_base_dup is not None:
                            # ERROR: This doi duplicates one from base (previous) year
                            n_dup_old += 1
                            print("ERROR: Input file {}, index={},"
                              " has duplicate past doi '{}'".format(
                                input_file_name, index_line, doi_base_dup))
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
                              doi,
                              doi_current_dup))
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
                            d_unit_doi[doi] = index_line + 1

                    d_output['doi'] = doi
                    # end processing the doi, if any, in input line

                    # Parse the rest of the line that appears before the doi.
                    # Split the line based on the ')' that should first appear
                    # following the year that follows  the author list
                    index_base = 0
                    index_found = 0
                    print("\n---Input file={}, index_line={}"
                      .format(input_file_name,index_line))

                    # Get the authors
                    index_found = line[index_base:].find('(')
                    if index_found == -1:
                        authors = line[index_base:]
                        d_column_style['authors'] = d_type_style['error']
                        skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        authors = line[index_base : index_end].strip()
                        #Next +1 to skip the '(' sentinel character )
                        index_base = index_end + 1
                        d_column_style['authors'] = d_type_style['valid']
                    print("Got authors='{}'".format(authors).encode('utf-8'))
                    d_output['authors'] = authors

                    # Get the pub_year
                    index_found = line[index_base:].find(')')
                    if skip_remaining_parsing == 1:
                        pub_year = 'Not found'
                    elif index_found < 1:
                        pub_year = line[index_base:]
                        d_column_style['pub_year'] = d_type_style['error']
                        skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        pub_year = line[index_base:index_end].strip()
                        # +2 to skip sentinel character PLUS the following '.'.
                        index_base = index_end + 2
                        d_column_style['pub_year'] = d_type_style['valid']
                    # print("Got index_found={},index_end={},pub_year='{}'"
                    # .format(index_found,index_end,pub_year))
                    d_output['pub_year'] = pub_year

                    #TITLE
                    # Accept either the first period or the first question mark
                    # to end the title.
                    index_found = line[index_base :].find('.')
                    index_found2 = line[index_base :].find('?')
                    if (index_found2 < index_found and index_found2 != -1):
                        index_found = index_found2
                    if skip_remaining_parsing == 1:
                        title = 'Not found'
                    elif index_found < 1:
                        title = line[index_base :]
                        d_column_style['title'] = d_type_style['error']
                        skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        title = line[index_base:index_end].strip()
                        index_base = index_end + 1
                        d_column_style['title'] = d_type_style['valid']
                    #print("Got index_found={},end={},title='{}'"
                    # .format(index_found,index_end,title))
                    d_output['title'] = title

                    #JOURNAL
                    # Seek end of journal name by finding open paren of issue
                    # then backtracking to the 'last comma or period',
                    # the true end-sentinel, because title itself may have an
                    # arbitrary number of commas.
                    index_found = line[index_base:].find(',')
                    if skip_remaining_parsing == 1:
                        journal =  'Not found'
                    elif index_found < 1:
                        journal = line[index_base :]
                        d_column_style['journal'] = d_type_style['error']
                        skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        # Journal title is substring after last open paren(of
                        # year) and before last comma
                        # because a title may have commas within it...
                        journal = line[index_base:index_end].strip()
                        # In this case we add to the end of index_found_open
                        index_base = index_end + 1
                        d_column_style['journal'] = d_type_style['valid']
                    #print("Got journal = '{}'".format(journal))
                    d_output['journal'] = journal

                    #VOLUME
                    # Again find open paren that indicates end of volume
                    index_found = line[index_base:].find('(')
                    skip_issue = 0
                    if skip_remaining_parsing == 1:
                        volume = 'Not found'
                    elif index_found < 1:
                        # Issue, eg (11) in parens is optional so seek ending ,
                        index_comma = line[index_base:].find(',')
                        d_output['issue'] = '(Missing)'
                        d_column_style['issue'] = d_type_style['warning']
                        if index_comma > -1:
                            index_end = index_base + index_comma
                            volume = line[index_base:index_end].strip()
                            d_output['volume'] = volume
                            index_base = index_end + 1
                            d_column_style['volume'] = d_type_style['valid']
                            skip_issue = 1
                        else:
                            skip_issue = 0
                            volume = line[index_base :]
                            d_column_style['volume'] = d_type_style['error']
                            skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        volume = line[index_base:index_end].strip()
                        index_base = index_end + 1
                        d_column_style['volume'] = d_type_style['valid']
                    d_output['volume'] = volume

                    #ISSUE
                    if skip_issue == 0:
                        index_found = line[index_base:].find(')')
                        if skip_remaining_parsing == 1:
                            issue = 'Not Found'
                        elif index_found < 1:
                            issue = line[index_base :]
                            d_column_style['issue'] = d_type_style['error']
                            skip_remaining_parsing = 1
                        else:
                            index_end = index_base + index_found
                            issue = line[index_base:index_end].strip()
                            # Do '+ 2' next: also skip the , after the ending )
                            index_base = index_end + 2
                            d_column_style['issue'] = d_type_style['valid']
                        #print("Got issue = '{}'".format(issue))
                        d_output['issue'] = issue
                    if d_output.get('issue', None) == None:
                        print("FieldISSUE:Issue not a key. Skip_issue={}"
                          .format(skip_issue))

                    #Page Range:
                    index_found = line[index_base:].find('.')
                    if skip_remaining_parsing == 1:
                        page_range = 'Not found'
                    elif index_found < 1:
                        page_range = line[index_base :]
                        d_column_style['page_range'] = d_type_style['error']
                        skip_remaining_parsing = 1
                    else:
                        index_end = index_base + index_found
                        page_range = line[index_base:index_end]
                        index_base = index_end + 1
                        d_column_style['page_range'] = d_type_style['valid']
                    d_output['page_range'] = page_range
                    print("input file {}, index {}, Calling writerow "
                      .format(input_file_name,index))

                    d_output['original_line'] = line
                    d_column_style['original_line'] = d_type_style['original']
                    # Write spreadsheet row
                    self.out_book_sheet.writerow(d_output=d_output,
                        d_column_style=d_column_style)
                # } end for line in input_lines
            # } end with open input_file
            print("0")
            print("\n\n Inspected input file={} with {} lines and {} dois."
              .format(input_file_name, len(input_lines), n_unit_dois ),
              file=sys.stdout)

            # Output excel workbook for this unit input file
            output_file_name = "{}/{}tmp.xls".format(path.parents[0],
                output_book_name)
            sys.stdout.flush()
            print("Using output_file_name={}.".format(output_file_name))
            self.out_book_sheet.work_book.save(output_file_name)
            print("SAVED EXCEL WORKBOOK in EXCEL OUTPUT FILE NAMED '{}'"
              .format(output_file_name))
            sys.stdout.flush()

        # end for path in self.unit paths
        self.n_dup_old = n_dup_old
        self.n_dup_cur = n_dup_cur
        self.n_dup_unit = n_dup_unit
        return
    # end inspect()
# end class CitationsInspector

'''
method run() - run the ifas citations inspectior
<param name='this_year'>
The integer 4 digit A.D. year, aka C.E. year
</param>
<param name='study'>
Value 'year_end' means it is the year_end study
</param>
'''
def run(this_year=2016, study='year_end'):
    me = 'run[ifas_citations_inspect]'
    print("{}: Starting".format(me))
    last_year = this_year - 1
    if study not in ['year_end','normal']:
        msg="Invalid study type={}. Error.".format(study)
        raise ValueError(msg)

    base_pubs_folder = etl.data_folder(linux='/home/robert', windows='U:',
    data_relative_folder='/data/ifas_citations/{}/base_info/'.format(this_year))

    base_file_name = 'IFAS-{}-pubs_by_topic-1.txt'.format(last_year)

    # base_pubs_file_name: is the absolute path of the input file with LAST
    # YEAR's DOIs to flag as a duplicate error if any is found in
    # THIS YEAR's input data

    base_pubs_file_name = '{}{}'.format(base_pubs_folder, base_file_name)

    if study == 'normal':
        #Here we read input files under inputs_round1/units
        input_files_glob = 'IFAS*txt'
        input_folder = etl.data_folder(linux='/home/robert', windows='U:',
            data_relative_folder='/data/ifas_citations/{}/inputs_round1/units/'
            .format(this_year))
    else:
        # study is 'year_end'
        # here we use as input the yearly base_info .txt file
        input_files_glob = '{}_Master_List_Final.txt'.format(this_year)
        input_folder = etl.data_folder(linux='/home/robert', windows='U:',
          data_relative_folder='/data/ifas_citations/{}/base_info/'
          .format(this_year))

    # example for params for a normal run comparing this years final list of
    # pubs to previous year and checking for dups, etc...

    inspector = CitationsInspector(base_pubs_file_name=base_pubs_file_name
        ,input_folder=input_folder, input_files_glob=input_files_glob)

    # Optional param output_folder defaults to input_folder if not given
    inspector.inspect(output_folder=input_folder)

    print("Got d_base_doi length='{}'".format(len(inspector.d_base_doi)))

    n_dup_old = inspector.n_dup_old
    n_dup_cur = inspector.n_dup_cur
    n_dup_unit = inspector.n_dup_cur

    print("Skipped {} dois of older ones, {} of current. Done!"
      .format(n_dup_old,n_dup_cur))

# RUN
run()
