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

def ifas_citations_base(input_file_name=None):
    d_base = {}
    d_doi = {}
    n_file_citations = 0
    with open (str(input_file_name),
            encoding="utf-8", errors='replace', mode="r") as input_file:
        input_lines = input_file.readlines()
        for (index_line, line) in enumerate(input_lines):
            key = str(index_line).zfill(10)
            d_base[key] = line
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
            d_doi[doi] = line
            n_file_citations += 1
        # end with open input_file
    return d_base, d_doi
# end def ifas_citations_base(input_file_name=None)
'''
Method ifas_citations_inspect()

<summary> Read an input file of ifas_citations and inspect them for problems
<param> input_file: input file with multiple citations </param>
<outputs>excel files in an output folder with apt violation warnings per
citation</output>
'''
def ifas_citations_inspect(input_folder='c:/rvp/tmpdir/citations/2017_ifas_test'
    , output_folder=None, d_doi_old=None):
    if input_folder is None or d_doi is None:
        raise Exception(ValueError, 'input_folder and d_doi are required')
    if output_folder is None:
        output_folder = input_folder
    d_doi_current = {}
    input_folder_path = Path(input_folder)
    input_file_paths = list(input_folder_path.glob('**/*utf8.txt'))
    n_input_files = 0
    n_citations = 0
    n_dup_old = 0
    n_dup_cur = 0
    print("Found {} input files".format(len(input_file_paths)))
    for path in input_file_paths:
        input_file_name = "{}/{}".format(path.parents[0], path.name)
        print("Processing file name={}".format(input_file_name))
        n_input_files += 1
        output_file_name = input_file_name + '.html'
        n_file_citations = 0
        with open(str(output_file_name),encoding="utf-8", mode="w") as output_file:
            print("\nReading input file {}".format(path.name))
            print("<!DOCTYPE html> <html>\n<head><meta charset='UTF-8'></head>\n"
                  "<body>\n<h3>APA Citations for Input File {}</h3>\n"
                  "<table border=2>\n"
                  .format(input_file_name), file=output_file)
            # NOTE: save EXCEL file as "UNICODE text" file
            with open (str(input_file_name),encoding="utf-8",mode="r") as input_file:
                # NOTE: may use VIM or other tools to change input file encoding to required
                # utf-8 here if not already in utf-8 format
                # :set fileencoding=utf-8
                input_lines = input_file.readlines()
                for line in input_lines:
                    #line = xml_escape(line)
                    #print("Got line='{}'.,eline='{}'".format(line,eline))
                    n_file_citations += 1
                    parts = line.split('\t')
                    nparts = len(parts)
                    authors, pubyear, title, journal, volume, issue, pages, doi = ("",) * 8
                    colskip = 0
                    colskip = 1 #per file from Suzanne 2017050x email with 'problem' in column 1,

                    index = colskip
                    if nparts > index:
                        authors = (parts[index].replace('"','').replace(',;', ',')
                            .replace('; ', ', '))

                    index += 1
                    if nparts > index:
                        pubyear = parts[index]

                    index += 1
                    if nparts > index: ### TITLE ###

                        # Replace nonbreaking spaces with 'normal' spaces first
                        title = parts[index].replace('\u00A0',' ')
                        # Remove multiple spaces everywhere. Split with no arguments adds this service
                        title = ' '.join(title.split())
                        # Remove troublesome quotation characters for APA citations
                        title = title.replace('"','')
                        title_words = title.split(' ')
                        # Enforce APA title style: First char of word must be capitalized, but lower
                        # first char for other words in title
                        title = ''
                        delim = ''

                        for word in title_words:
                            nchars = len(word)
                            if nchars < 1:
                                continue
                            title += delim
                            if delim == '':
                                title +=  word[0].upper()
                                if nchars > 1:
                                    title += word[1:]
                            elif nchars == 1:
                                title += word[0].lower()
                            elif (nchars > 2
                                  and not has_digit(word[1:])
                                  and not has_upper(word[1:])):
                                # This is a second or following title word.
                                # APA style says it should not be upper-case, but probably
                                # only unless it has other uppercase characters
                                # or digits (for example "RNA" "O2").
                                # So here we make first letter lowercase only if
                                # second (and greater) letter of word has no uppercase
                                # nor digit characters
                                title += word[0].lower()
                                title += word[1:]
                            else:
                                title += word
                            delim = ' '
                        # end for word in title_words

                        # Get rid of trailing . in title
                        while title.endswith('.'):
                            title = title[:-1]
                        # end title
                        index += 1
                        if nparts > index: journal = parts[index]

                        index += 1
                        if nparts > index: volume = parts[index]

                        index +=1
                        if nparts > index: issue = parts[index]

                        index += 1
                        if nparts > index:
                            pages = parts[index]
                            while pages.endswith('.'):
                                pages = pages[:-1]

                        # FIELD DOI
                        index +=1
                        if nparts > index:
                            doi = parts[index].replace(' ','').replace('\n','')
                            if doi.startswith('http://dx.doi.org/'):
                                doi = doi[18:]
                            if doi.upper().startswith('DOI:'):
                                doi = doi[4:]
                            if len(doi.strip()) > 0:
                                # Complain if the doi is already in the base or this
                                # 'current' list of ifas citation files
                                doi_old = d_doi_old.get(doi, None)
                                if doi_old is not None:
                                    n_dup_old += 1
                                    print("ERROR: Input file {} has duplicate past doi '{}'"
                                      .format(input_file_name,doi_old))

                                doi_cur_val = d_doi_current.get(doi, None)
                                if doi_cur_val is not None:
                                    n_dup_cur += 1
                                    print("ERROR: Input file {} index={} has duplicate doi '{}'"
                                          " to one in this year's input file name = '{}'"
                                      .format(input_file_name,index,doi,doi_cur_val))
                                else:
                                    d_doi_current[doi] = input_file_name
                            # end if len(doi) > 0
                        #end field DOI

                        p_volume = '' if volume == '' else ', {}'.format(volume)
                        p_issue = '' if issue == '' else '({})'.format(issue)
                        p_pages = '' if pages == '' else ', {}'.format(pages)
                        p_doi = '' if doi == '' else (
                            ' <a href="http:/dx.doi.org/{}"> {}</a>'.format(doi,doi))

                        print("<tr><td>{} ({}). {}. "
                              "<span style='font-style: italic;'>{}{}</span>{}{}.{}\n</td></tr>\n"
                            .format(html_escape(authors),
                                    html_escape(pubyear),
                                    html_escape(title),
                                    html_escape(journal),
                                    html_escape(p_volume),
                                    html_escape(p_issue),
                                    html_escape(p_pages),
                                    p_doi)
                            ,file=output_file)
                    # end nparts > title index value
                # for line in input_lines

            print("Produced APA citation output file {} with {} citations."
                  .format(output_file_name, n_file_citations))
            print("</table></body></html>\n",file=output_file)
            # withoutput_file
    # with input_file
    return n_dup_old, n_dup_cur
# end make_apa_citations

print("Starting")
input_folder = make_home_relative_folder(
    "ifas_citations/inputs/20170419_test_citations_txt_files")
master_base_file = input_folder + "/2015_master_base.txt"

d_base, d_doi = ifas_citations_base(input_file_name=master_base_file)

print("Got d_doi length='{}'".format(len(d_doi)))

n_dup_old, n_dup_cur = ifas_citations_inspect(input_folder=input_folder,d_doi_old=d_doi)

print("Skipped {} dois of olders ones, {} of current.Done!"
  .format(n_dup_old,n_dup_cur))