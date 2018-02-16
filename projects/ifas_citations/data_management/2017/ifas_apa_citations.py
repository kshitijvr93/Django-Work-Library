# 20170315 - Robert V. Phillips
# Python3 Code that runs in a Jupyter Cell
# to produce APA style citations from tab-delimited .txt files in a given input directory
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

from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder

'''

method make_annual_citations() pretties up most titles that added upper case
to each word, but REMOVES some uppercase words where they probably still
should remain.

Parameters:

input_folder must containe some files with names that end 'utf8.txt'

Each such file will be read and proceseed to produce an output file
with the same prefix in the filename, but ending with uf8.txt.html


MORAL: do not try to 'correct' some words that this program changed to
lower case because it will again put them to lowercase.
Rather, this is not designed to be iteratively applied - only to be
hand-modified for final use after it is run ONCE on input.
'''
def make_apa_citations(
    input_folder=None, output_folder=None,input_glob='**/*utf8.txt',
    log_file=None,verbosity=0):

    me = 'make_apa_citations'
    if verbosity > 1:
        msg=('{}: starting witn input folder={},ouput_folder={}',
            'glob={}'.format(input_folder,output_folder,input_glob))
        print(msg,file=log_file)

    if input_folder is None:
        raise ValueError("input_folder is not given as an argument")
    if output_folder is None:
        output_folder = input_folder
    print("{}: using input_folder={},\noutput_folder={},\ninput_glob={}"
          .format(me,input_folder,output_folder,input_glob),file=log_file)

    sys.stdout.flush
    input_folder_path = Path(input_folder)
    input_file_paths = list(input_folder_path.glob(input_glob))
    n_input_files = 0
    n_citations = 0

    print("Found {} input files".format(len(input_file_paths)),file=log_file)

    for path in input_file_paths:
        input_file_name = "{}\{}".format(path.parents[0], path.name)
        print("Processing file name={}".format(input_file_name),file=log_file)

        n_input_files += 1
        output_file_name = input_file_name + '.html'
        n_file_citations = 0
        with open(str(output_file_name),encoding="utf-8",mode="w") as output_file:
            print("\nReading input file {}".format(path.name),file=log_file)
            print("<!DOCTYPE html> <html>\n<head><meta charset='UTF-8'></head>\n"
                  "<body>\n<h3>APA Citations for Input File {}</h3>\n"
                  "<table border=2>\n"
                  .format(input_file_name), file=output_file)
            # NOTE: save EXCEL file as utf-8 encoded file
            with open (str(input_file_name),mode="r",encoding="utf-8",errors="ignore") as input_file:
                # NOTE: may use VIM or other tools to change input file encoding to required
                # utf-8 here if not already in utf-8 format
                # :set fileencoding=utf-8
                input_lines = input_file.readlines()
                for line in input_lines:
                    eline = etl.escape_xml_text(line)
                    #print("Got line='{}'.,eline='{}'".format(line,eline))
                    n_file_citations += 1
                    parts = line.split('\t')
                    authors, pubyear, title, journal, volume, issue, pages, doi = (
                        ("",) * 8 )
                    nparts = len(parts)
                    print("Line has {} tab-separated parts".format(nparts),file=log_file)
                    colskip = 0
                    colskip = 1 #per file from Suzanne 2017050x email with 'problem' in column 1,
                    colskip = 0

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

                        index +=1
                        if nparts > index:
                            doi = parts[index].replace(' ','').replace('\n','')
                            if doi.startswith('http://dx.doi.org/'):
                                doi = doi[18:]
                            if doi.upper().startswith('DOI:'):
                                doi = doi[4:]

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
                  .format(output_file_name, n_file_citations),file=log_file)
            print("</table></body></html>\n",file=output_file)
            # withoutput_file
    # with input_file
    return None
# end make_apa_citations

def run(study_year=2017):
    print("Starting")
    # input_folder = make_home_relative_folder("ifas_citations/inputs")
    linux = '/home/robert/'
    windows = 'C:/rvp/'
    data_relative_folder = ('git/citrus/projects/ifas_citations/data/{}/'
        .format(study_year))

    data_folder = etl.data_folder(linux=linux, windows=windows,
        data_relative_folder=data_relative_folder )

    print("Got data_folder={}".format(data_folder))
    # 2017 - I opened the xls file of the ifas inspector output and just saved
    # as tab-delimited text to produce the citations_input_file
    citations_input_file = 'IFAS_citations_2017_inspected.txt'
    #20180216 1pm test
    citations_input_file = 'Test_Agron_20180216.txt'
    log_basename = "log_apa_formatter.txt"
    log_filename = "{}{}".format(data_folder,log_basename)
    log_file = open(log_filename, encoding="utf-8",mode="w")
    print("Calling make_apa_citations...", file=log_file)

    input_folder = data_folder
    output_folder = data_folder

    # Just one file this year, so use its name as input_glob pattern
    make_apa_citations(input_folder=input_folder,output_folder=output_folder
        ,input_glob=citations_input_file, log_file=log_file,verbosity=1)

    print("Done! See log file='{}'".format(log_filename))

# RUN
run()
