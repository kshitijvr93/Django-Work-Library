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

        self.d_base_index = {}
        self.d_base_doi = {}
        self.d_current_doi = {}
        n_file_citations = 0

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

        print("{}: Found {} input files".format(me,len(self.unit_paths)))
        for path in self.unit_paths:
            input_file_name = "{}/{}".format(path.parents[0], path.name)
            print("Processing file name={}".format(input_file_name))
            n_input_files += 1
            #
            output_file_name = input_file_name + '.html'

            n_file_citations = 0
            with open(str(output_file_name), encoding="utf-8", errors='replace',mode="w") as output_file:
                print("\nReading input file {}".format(path.name))
                print("<!DOCTYPE html> <html>\n<head><meta charset='UTF-8'></head>\n"
                      "<body>\n<h3>APA Citations for Input File {}</h3>\n"
                      "<table border=2>\n"
                      .format(input_file_name), file=output_file)
                # NOTE: save EXCEL file as "UNICODE text" file
                with open (str(input_file_name), encoding="utf-8", errors='replace',mode="r") as input_file:
                    input_lines = input_file.readlines()
                    n_unit_dois = 0

                    for index_line, line in enumerate(input_lines):
                        n_file_citations += 1
                        line = line.replace('\n','')
                        index_doi = -1
                        try:
                            index_doi = line.find("doi:")
                        except Exception as e:
                            print("Skipping exception={}".format(repr(e.message)))
                            pass
                        if index_doi < 0:
                            print("WARNING: Input file={}, index_line={}, {}."
                              .format(input_file_name, index_line, line.encode('ascii','ignore')))
                            doi = ''
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

                            doi_cur_dup = self.d_current_doi.get(doi, None)
                            if doi_cur_dup is not None:
                                n_dup_cur += 1
                                print("ERROR: Input file {} index={} has duplicate current year doi '{}'"
                                      " to one in this year's input file name = '{}'"
                                  .format(input_file_name,index_line,doi,doi_cur_dup))
                            else:
                                self.d_current_doi[doi] = input_file_name
                        # end else clause - doi given in input line

                        # Parse the rest of the line that appears before the doi.
                        #  Split the line based on the ')' that should first appear following the year that follows
                        #  the author list
                        index_next = 0
                        print("\nInput file={}, index_line={}".format(input_file_name,index_line))

                        # Get the authors
                        index_open_paren = line.find('(')
                        if index_open_paren == -1:
                            authors = line.strip()
                            index_open_paren = index_next
                        else:
                            authors = line[:index_open_paren].strip()
                            index_next = index_open_paren
                        print("Got authors='{}'".format(authors).encode('utf-8'))

                        # Get the year
                        index_found = line[index_open_paren+1:].find(')')
                        if index_found == -1:
                            index_closed_paren = index_next
                            pub_year = line.strip()
                        else:
                            index_closed_paren = index_found + index_open_paren + 1
                            pub_year = line[index_open_paren + 1:index_closed_paren].strip()
                            index_next = index_closed_paren
                        print("Got pub_year='{}'".format(pub_year))

                        #JOURNAL
                        # Seek end of journal name by finding open paren of issue then backtracking to a comma
                        index_found = line[index_closed_paren + 1:].find('(')
                        if index_found == -1:
                            journal = line.strip()
                            index_period = index_next
                        else:
                            line2 = line[index_closed_paren + 1:index_found]
                            # find all commas between the last closed parena and this found open paren
                            print("seeking last comma in '{}'".format(line2))
                            l_pos_comma = [pos for pos, char in enumerate(line2) if char == ',']
                            index_comma = l_pos_comma[-1]
                            # Journal title is substring after last open paren(of year) and before last comma
                            # because a title may have commas within it...
                            journal = line[index_closed_paren: index_closed_paren + index_found].strip()
                            index_next = index_comma
                        print("Got journal = '{}'".format(journal))

                        #VOLUME
                        index_found = line[index_period +1 :].find('(')
                        if index_open_paren == -1:
                            volume=''
                            index_open_paren = index_next
                        else:
                            index_open_paren = index_found + index_period + 1
                            volume = line[index_period:index_open_paren].strip()
                            index_found = volume.find(',')
                            if index_found >= 0:
                                volume = volume[index_found + 1:]
                            volume = volume.strip()
                            index_next = index_open_paren
                        print("Got volume = '{}'".format(volume))

                        #ISSUE
                        index_found = line[index_open_paren + 1:].find(')')
                        if index_found == -1:
                            issue = ''
                            index_closed_paren = index_next
                        else:
                            index_closed_paren = index_open_paren + 1 + index_found
                            issue = line[index_open_paren+1:index_closed_paren].strip()
                            index_next = index_closed_paren
                        print("Got issue = '{}'".format(issue))
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
