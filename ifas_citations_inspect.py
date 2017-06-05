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

from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlrd import open_workbook

'''
class OutBookSheet is a simple excel workbook of type xls with one sheet.

'''
class OutBookSheet(Object):

    def __init__(self, name=None, output_columns=None):
        # To save data, caller must use the self.book.save(filename) method
        # Note: and user MUST use the .xls suffix in that filename. Though
        # suffix xslx will work OK with LibreOffice, it causes Excel 2013 to choke.
        self.book = xlwt.Workbook()
        self.sheet = self.book.add_sheet(name)
        self.output_columns = output_columns
        # Caller may use this to set a style per column before calling writerow
        self.d_column_style = {}
        # Header row
        for col_index,col_name in enumerate(self.output_columns):
            # Write first output row 0 with column names
            self.sheet.write(0, col_index, col_name)
            self.d_column_style[col_name] = None

        # Set 'cursor' of current outbook row to assist repreated writerow calls
        self.outbook_row_index = 1

    def writerow(self, d_output=None, d_column_style=None, verbosity=0):
        column_values = [ d_output[column] for column in self.output_columns]
        for column_index, (column_key, column_value) in enumerate(d_output.items()):
            #print ("outbooks_writerow: index={}, key='{}', value='{}'".format(column_index, column_key, column_value) )
            style = d_column_style.get(column_key, None)
            if style is None:
                self.sheet.write(self.outbook_row_index, column_index, column_value.strip())
            else:
                if (verbosity > 0):
                    print("Writing a style for column '{}'".format(column_key))
                self.deeply_sheet.write(self.outbook_row_index, column_index, column_value.strip(), style)
        self.outbook_row_index += 1

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
    def __init__(self, year_input_folder_name=None, unit_has_tab_sep=False):
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
        self.outbook = OutBook()
        self.d_base_index = {}
        self.d_base_doi = {}
        self.d_current_doi = {}
        n_file_citations = 0
        self.output_columns = [
        'doi', 'authors', 'title', 'journal','volume','issue','page_range'
        ]
        self.book_sheet = OutBookSheet(self.output_columns)
        # input and save last year's citation info to use to check for duplicates in this year's units
        with open (str(self.base_pubs_file_name),
                encoding="utf-8", errors='replace', mode="r") as input_file:
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
                doi = line[index_doi:]
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
        d_column_output = {}
        d_column_style = {}
        print("{}: Found {} input files".format(me,len(self.unit_paths)))
        for path in self.unit_paths:
            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("Processing file name={}".format(input_file_name))
            n_input_files += 1
            #
            output_file_name = input_file_name + '.html'
            outbook_name = '{}'.format(path.name.replace(' ','_'))
            self.outbooksheet = OutBookSheet(name=outbook_name, self.output_columns)
            n_file_citations = 0
            dot_index = path.name.find('.')
            input_unit_base_name = path.name[:dot_index]
            # We produce one output file, an excel workbook, for every unit intput file
            with open(str(output_file_name), encoding="utf-8", errors='replace',mode="w") as output_file:
                outbook = OutBookSheet(name=input_unit_base_name,output_columns=self.output_columns)
                print("\nReading input file {}".format(path.name))
                print("<!DOCTYPE html> <html>\n<head><meta charset='UTF-8'></head>\n"
                      "<body>\n<h3>APA Citations for Input File {}</h3>\n"
                      "<table border=2>\n"
                      .format(input_file_name), file=output_file)
                # NOTE: save EXCEL file as "UNICODE text" file
                with open (str(input_file_name), encoding="utf-8-sig", errors='ignore', mode="r") as input_file:
                    input_lines = input_file.readlines()
                    n_unit_dois = 0
                    for index, line in enumerate(input_lines):
                        d_output = {}
                        index_line = index + 1
                        n_file_citations += 1
                        line = line.replace('\n','')
                        index_doi = -1
                        try:
                            index_doi = line.find("doi:")
                        except Exception as e:
                            print("Ignoring exception={}".format(repr(e.message)))
                            pass
                        if index_doi < 0:
                            print("WARNING: NO DOI given in input file={}, index_line={}, {}."
                              .format(input_file_name, index_line, line.encode('ascii','ignore')))
                            doi = ''
                            doi = "{}:linecount={}".format(input_file_name, index_line)
                        else:
                            doi = line[index_doi:]
                            line = line[:index_doi] #keep the non-doi part of the line
                            n_unit_dois += 1
                            # Complain if the doi is already in the base or this
                            # 'current' list of ifas citation files
                            doi_base_dup = self.d_base_doi.get(doi, None)
                            if doi_base_dup is not None:
                                n_dup_old += 1
                                print("ERROR: Input file {}, index={}, has duplicate past doi '{}'"
                                  .format(input_file_name, index_line, doi_base_dup))

                        d_output['doi'] = doi
                        doi_cur_dup = self.d_current_doi.get(doi, None)
                        if doi_cur_dup is not None:
                            n_dup_cur += 1
                            print("ERROR: Input file {} index={} has duplicate current year doi '{}'"
                                  " to one in this year's input file name = '{}'"
                              .format(input_file_name,index_line,doi,doi_cur_dup))

                            outbook.d_column_style['doi'] = easyxf_style = ('pattern: pattern solid, fore_colour light_blue;'
                                  'font: colour white, bold True;')
                        else:
                            outbook.d_column_style['doi'] = None
                            self.d_current_doi[doi] = input_file_name
                        # end else clause - doi given in input line

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
                            index_base = len(line)
                            continue
                        else:
                            index_end = index_base + index_found
                            authors = line[index_base : index_end].strip()
                            index_base = index_end + 1 # plus one to skip the '(' sentinel character )
                        print("Got authors='{}'".format(authors).encode('utf-8'))
                        d_output['authors'] = authors
                        d_column_style['authors'] = None

                        # Get the pub_year
                        if index_found < 1:
                            continue
                        index_found = line[index_base:].find(')')
                        if index_found < 1:
                            pub_year = line[index_base]
                        else:
                            index_end = index_base + index_found
                            pub_year = line[index_base:index_end].strip()
                            index_base = index_end + 2 # Add 1 to also skip sentinel character PLUS the following '.'.
                        print("Got index_found={},index_end={},pub_year='{}'".format(index_found,index_end,pub_year))

                        #TITLE
                        if index_found < 1:
                            continue
                        index_found = line[index_base :].find('.')
                        if index_found < 1:
                            title = line[index_base :]
                        else:
                            index_end = index_base + index_found
                            title = line[index_base:index_end].strip()
                            index_base = index_end + 1
                        print("Got index_found={},end={},title='{}'".format(index_found,index_end,title))

                        #JOURNAL
                        # Seek end of journal name by finding open paren of issue then backtracking to the
                        # 'last comma or period', the true end-sentinal, because title itself may have an arbitrary number of commas.
                        if index_found < 1:
                            continue
                        index_found = line[index_base:].find(',')
                        if index_found < 1:
                            journal = ''
                            journal = line[index_base :]
                        else:
                            index_end = index_base + index_found
                            # Journal title is substring after last open paren(of year) and before last comma
                            # because a title may have commas within it...
                            journal = line[index_base:index_end].strip()
                            # In this case we add to the end of index_found_open
                            index_base = index_end + 1
                        print("Got journal = '{}'".format(journal))

                        #VOLUME
                        # Again find open paren that indicates end of volume
                        if index_found < 1:
                            continue
                        index_found = line[index_base:].find('(')
                        if index_found < 1:
                            volume=''
                            volume = line[index_base :]
                        else:
                            index_end = index_base + index_found
                            volume = line[index_base:index_end].strip()
                            index_base = index_end + 1
                        print("Got volume = '{}'".format(volume))

                        #ISSUE
                        if index_found < 1:
                            continue
                        index_found = line[index_base:].find(')')
                        if index_found < 1:
                            issue = line[index_base :]
                        else:
                            index_end = index_base + index_found
                            issue = line[index_base:index_end].strip()
                            index_base = index_end + 1
                        print("Got issue = '{}'".format(issue))

                        #Page Range:
                        if index_found < 1:
                            continue
                        index_found = line[index_base:].find('.')
                        if index_found < 1:
                            page_range = line[index_base :]
                        else:
                            index_end = index_base + index_found
                            page_range = line[index_base:index_end]
                            index_base = index_end + 1
                    # for line in input_lines

                print("Inspected input file={} with {} lines and {} dois."
                  .format(input_file_name, len(input_lines), n_unit_dois))


                # end with open input_file
            # end with open output_file
        # end for path in self.unit paths
        self.n_dup_old = n_dup_old
        self.n_dup_cur = n_dup_cur
        return n_dup_old, n_dup_cur
    # end make_apa_citations
# end class CitationsInspector

print("Starting")
year_input_folder_name = make_home_relative_folder(
    "data/ifas_citations/2016/inputs_round1")

inspector = CitationsInspector(year_input_folder_name=year_input_folder_name)

inspector.inspect()

print("Got d_base_doi length='{}'".format(len(inspector.d_base_doi)))

n_dup_old = inspector.n_dup_old
n_dup_cur = inspector.n_dup_cur

print("Skipped {} dois of olders ones, {} of current.Done!"
  .format(n_dup_old,n_dup_cur))
