'''
20170530 - Robert V. Phillips
Python3 code
This file holds methods used to inspect and report problematics IFAS citations
that are received from the 28 IFAS units

TEST INPUT FILE NOTES:
 FILENAME is 2015_master_base.txt, but original name left by MSL staff is
"2015 Master List_dedup.docx", which I opened wth word and saved as a utf8 file
and renamed to 2015_master_base.txt -

NOTE: the utf8 conversion seems to have errors, should revisit later.
There are no tabs in this file to delineate authors, etc, so must parse it fully.

At first, just need to skim doi values that seem pretty uniformly to be prefixed
by "doi: ", so that's a start.
'''

'''
Method ifas_citations_base():
<summary> Read a 'base' file of previous IFAS citations that are not to be allowed
in this year's batch of input.
Create and return (1)a dictionary keyed by line id (zfilled to 10 digits)
(2) and keyd by IFAS citation DOI values.
The value used to pair to each key of each dictionary is a copy of the
input citation line.
Note that not all citation lines have DOI values, and so the length of
dictionary 1.

Will always be greater or equal to the length of dictionary 2.
The dictionaries are used to detect duplicate citations attempted to be filed as new
articles for this year's batch of citations</summary>

NOTE: some issues with both word and writer fail to export the master docx file
to a completely valid utf-8 file format. For example, of the first citations has
a greek character that fails to be exported as utf-8, it seems.
That detail needs to be resolved.
'''
import sys, os, os.path, platform
sys.path.append('{}/github/citrus/modules'.format(os.path.expanduser('~')))
from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlwt import easyxf
from xlrd import open_workbook

'''
class OutBookSheet is a simple excel workbook of type xls with one sheet.

'''
class OutBookSheet():

    def __init__(self, name=None, output_columns=None):
        # To save data, caller must use the self.book.save(filename) method
        # Note: and user MUST use the .xls suffix in that filename. Though
        # suffix xslx will work OK with LibreOffice, it causes Excel 2013 to choke.
        self.work_book = xlwt.Workbook()
        self.sheet = self.work_book.add_sheet(name)
        self.output_columns = output_columns
        self.d_type_style = {
        'unparsed' : easyxf( 'pattern: pattern solid, fore_colour '
            'grey25; font: colour black, bold True;'),
        'warning' :  easyxf( 'pattern: pattern solid, fore_colour '
            'pale_blue; font: colour black, bold True;'),
        'error' :  easyxf( 'pattern: pattern solid, fore_colour '
            'pink; font: colour black, bold True;'),
        'error2' :  easyxf( 'pattern: pattern solid, fore_colour '
            'rose; font: colour black, bold True;'),
        'error3' :  easyxf( 'pattern: pattern solid, fore_colour '
            'light_orange; font: colour black, bold True;'),
        'valid' :  easyxf( 'pattern: pattern solid, fore_colour '
            'white; font: colour black, bold False;'),
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

    def writerow(self, d_output=None, d_column_style=None, verbosity=0):

        for column_index, column_key in enumerate(self.output_columns):
            column_value = d_output[column_key]
            #print ("outbooks_writerow: index={}, key='{}', value='{}'".format(column_index, column_key, column_value) )
            style = d_column_style.get(column_key, None)
            if style is None:
                self.sheet.write(self.outbook_row_index, column_index, column_value.strip())
            else:
                if (verbosity > 0):
                    print("Writing a style for column '{}'".format(column_key))
                self.sheet.write(self.outbook_row_index, column_index, column_value.strip(), style)
        self.outbook_row_index += 1
        return
# end class OutBookSheet

'''
<summary>This object registers the annual IFAS citations input folders and files,
and has main method inspect() which inspects a year's worth of IFAS
'round1' citation data from the UF IFAS units.
It produces an output excel file for each unit that inputted data, with
various cell colorations and indications of warning and error conditions .

These files are for UF MSL staff and IFAS staff to review and consider in
making further manual refinements to each the unit-citations file to
register this year's scholarly publications in peer-reviwed journals,
authored by their employees.

Those files will comprise round2 orf input.
</summary>

<param> year_input_folder_name - main folder with a year of structured input files, with filenames and subfolder
structure as expcted i routing __init__ and object methods, </param>
'''
class CitationsInspector():
    '''
    Set up input parameters and file references for use by the inspect method.
    Also read the base citations that have a doi mentioned and create a dictionary
    d_base_doi entry keyed by the doi with value being the entire line's text.
    Also keep every line i the d_base dictionary, keyed by index line number zfilled to 10 positions.
    '''
    def __init__(self, year_input_folder_name=None, unit_has_tab_sep=False,verbosity=0):
        self.year_input_folder_name = year_input_folder_name
        self.units_folder = '{}/units'.format(self.year_input_folder_name)
        self.units_file_glob = 'IFAS*txt'
        print("Units_folder-'{}', glob='{}'".format(self.units_folder, self.units_file_glob))

        self.unit_paths = list(Path(self.units_folder).glob(self.units_file_glob))
        self.base_folder = '{}/base_info'.format(self.year_input_folder_name)
        print("Base folder-'{}'".format(self.base_folder))
        self.base_pubs_file_name = '{}/IFAS-2015-pubs_by_topic-1.txt'.format(self.base_folder)
        self.base_skip_lines = 4 # Number of lines in last years citations file to skip from the start
        self.unit_has_tab_sep = unit_has_tab_sep; #If true, unit citations files are tab-separated
        self.d_base_index = {}
        self.d_base_doi = {}
        self.d_current_doi = {}
        self.d_unit_doi = {}
        n_file_citations = 0
        self.output_columns = [
          'doi', 'authors', 'title', 'pub_year','journal','volume','issue',
          'page_range', 'original_line',
        ]

        # input and save last year's citation info to use to check for duplicates in this year's units
        with open (str(self.base_pubs_file_name), encoding="utf-8-sig", errors='replace', mode="r") as input_file:
            input_lines = input_file.readlines()
            for (index_line, line) in enumerate(input_lines):
                # Skip the normal number of header lines of this file and any topic section line
                if index_line < self.base_skip_lines or len(line) < 50:
                    #print("Skipping base citations file context line='{}'".format(line))
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
                    #print(omsg) -- would cause UnicodeEncodeError - charmap codec cant encodt '\ufffd\''
                # SAVE BASE DOI to check for duplicates later
                self.d_base_doi[doi] = line
                n_file_citations += 1
            # end with open input_file
        #self.d_base = d_base
        return None

    # end __init__
        '''
    Method inspect()

    <summary> Read the unit paths input files of ifas citations and inspect them for problems</summary>
    <param> input_file: input file with multiple citations </param>
    <outputs>excel files in an output folder with apt violation warnings per
    citation</output>
    '''
    def inspect(self, output_folder=None):
        if output_folder is None:
            output_folder = self.year_input_folder_name
        self.inspect_output_folder = output_folder
        me = 'inspect'

        # Keep track of current year's doi values
        n_input_files = 0
        n_citations = 0
        n_dup_old = 0
        n_dup_cur = 0
        n_dup_unit = 0
        print("{}: Found {} input files".format(me,len(self.unit_paths)))
        for path in self.unit_paths:
            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("Processing file name={}".format(input_file_name))
            n_input_files += 1

            dot_index = path.name.find('.')
            if dot_index > -1:
                out_book_name = path.name[:dot_index]
            else:
                out_book_name = '{}'.format(path.name).replace(' ','_')

            self.out_book_sheet = OutBookSheet(name=out_book_name, output_columns=self.output_columns)
            d_type_style = self.out_book_sheet.d_type_style #convenient abbreviation
            n_file_citations = 0
            print("\nReading input file {}".format(path.name))

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
                        print("WARNING: NO DOI given in input file='{}', index_line={}, {}."
                          .format(path.name, index_line, line.encode('ascii',errors='ignore')))
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
                            print("ERROR: Input file {}, index={}, has duplicate past doi '{}'"
                              .format(input_file_name, index_line, doi_base_dup))
                            d_column_style['doi'] = d_type_style['error2']

                        # DOI Dup Check  (error):
                        # check if doi already in current year
                        # for a unit report that has just been processed earlier in this
                        # loop over units

                        doi_current_dup = self.d_current_doi.get(doi, None)
                        if doi_current_dup is not None:
                            n_dup_cur += 1
                            print("ERROR: Input file {} index={} has duplicate current year doi '{}'"
                                  " to one in this year's input file name = '{}'"
                              .format(input_file_name,index_line,doi,doi_current_dup))
                            d_column_style['doi'] = d_type_style['error']
                        else:
                            # Do not reset style here for doi - keep it from prior doi check
                            self.d_current_doi[doi] = input_file_name


                        # DOI Dup Check 3 (error3):
                        # check if doi already in previous line of
                        # this unit report that has just been processed earlier in this
                        # loop over units

                        doi_unit_dup = d_unit_doi.get(doi, None)
                        if doi_unit_dup is not None:
                            n_dup_unit += 1
                            print("ERROR: Input file {} line index={} has duplicate doi '{}'"
                                  " to previous line {} in this unit's sheet."
                              .format(input_file_name,index_line,doi,doi_unit_dup))
                            d_column_style['doi'] = d_type_style['error3']
                        else:
                            # Do not reset style here for doi - keep it from prior doi check
                            d_unit_doi[doi] = index_line + 1

                    d_output['doi'] = doi
                    # end processing the doi, if any, in input line

                    # Parse the rest of the line that appears before the doi.
                    #  Split the line based on the ')' that should first appear following the year that follows
                    #  the author list
                    index_base = 0
                    index_found = 0
                    print("\n---Input file={}, index_line={}".format(input_file_name,index_line))

                    # Get the authors
                    index_found = line[index_base:].find('(')
                    if index_found == -1:
                        authors = line[index_base:]
                        d_column_style['authors'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        authors = line[index_base : index_end].strip()
                        index_base = index_end + 1 # plus one to skip the '(' sentinel character )
                        d_column_style['authors'] = d_type_style['valid']
                    print("Got authors='{}'".format(authors).encode('utf-8'))
                    d_output['authors'] = authors

                    # Get the pub_year
                    index_found = line[index_base:].find(')')
                    if index_found < 1:
                        pub_year = line[index_base:]
                        d_column_style['pub_year'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        pub_year = line[index_base:index_end].strip()
                        index_base = index_end + 2 # Add 1 to also skip sentinel character PLUS the following '.'.
                        d_column_style['pub_year'] = d_type_style['valid']
                    #print("Got index_found={},index_end={},pub_year='{}'".format(index_found,index_end,pub_year))
                    d_output['pub_year'] = pub_year

                    #TITLE
                    index_found = line[index_base :].find('.')
                    if index_found < 1:
                        title = line[index_base :]
                        d_column_style['title'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        title = line[index_base:index_end].strip()
                        index_base = index_end + 1
                        d_column_style['title'] = d_type_style['valid']
                    #print("Got index_found={},end={},title='{}'".format(index_found,index_end,title))
                    d_output['title'] = title

                    #JOURNAL
                    # Seek end of journal name by finding open paren of issue then backtracking to the
                    # 'last comma or period', the true end-sentinal, because title itself may have an arbitrary number of commas.
                    index_found = line[index_base:].find(',')
                    if index_found < 1:
                        journal = line[index_base :]
                        d_column_style['journal'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        # Journal title is substring after last open paren(of year) and before last comma
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
                    if index_found < 1:
                        volume = line[index_base :]
                        d_column_style['volume'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        volume = line[index_base:index_end].strip()
                        index_base = index_end + 1
                        d_column_style['volume'] = d_type_style['valid']
                    #print("Got volume = '{}'".format(volume))
                    d_output['volume'] = volume

                    #ISSUE
                    index_found = line[index_base:].find(')')
                    if index_found < 1:
                        issue = line[index_base :]
                        d_column_style['issue'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        issue = line[index_base:index_end].strip()
                        index_base = index_end + 2 # increment 2 also skips the , after the ending )
                        d_column_style['issue'] = d_type_style['valid']
                    #print("Got issue = '{}'".format(issue))
                    d_output['issue'] = issue

                    #Page Range:
                    index_found = line[index_base:].find('.')
                    if index_found < 1:
                        page_range = line[index_base :]
                        d_column_style['page_range'] = d_type_style['error']
                    else:
                        index_end = index_base + index_found
                        page_range = line[index_base:index_end]
                        index_base = index_end + 1
                        d_column_style['page_range'] = d_type_style['valid']
                    d_output['page_range'] = page_range
                    print("input file {}, index {}, Calling writerow ".format(input_file_name,index))

                    d_output['original_line'] = line
                    # Write spreadsheet row
                    self.out_book_sheet.writerow(d_output=d_output, d_column_style=d_column_style)
                # } end for line in input_lines

                # Output this line's Excel row
            # } end with open input_file
            print("Inspected input file={} with {} lines and {} dois."
              .format(input_file_name, len(input_lines), n_unit_dois))

            # Output excel workbook for this unit input file
            excel_file_name = "{}/{}.xls".format(path.parents[0], out_book_name)
            self.out_book_sheet.work_book.save(excel_file_name)
            print("SAVED EXCEL WORKBOOK in EXCEL FILE NAMED '{}'".format(excel_file_name))

        # end for path in self.unit paths
        self.n_dup_old = n_dup_old
        self.n_dup_cur = n_dup_cur
        self.n_dup_unit = n_dup_unit
        return
    # end inspect()
# end class CitationsInspector

print("Starting")
year_input_folder_name = make_home_relative_folder(
    "data/ifas_citations/2016/inputs_round1")

inspector = CitationsInspector(year_input_folder_name=year_input_folder_name)

inspector.inspect()

print("Got d_base_doi length='{}'".format(len(inspector.d_base_doi)))

n_dup_old = inspector.n_dup_old
n_dup_cur = inspector.n_dup_cur
n_dup_unit = inspector.n_dup_cur

print("Skipped {} dois of olders ones, {} of current.Done!"
  .format(n_dup_old,n_dup_cur))
