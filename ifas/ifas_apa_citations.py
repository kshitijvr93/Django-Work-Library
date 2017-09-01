# 20170315 - Robert V. Phillips
# Python3 Code that runs in a Jupyter Cell
# to produce APA style citations from tab-delimited .txt files in a given input directory
import sys, os, os.path, platform
def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())
print("Sys.path={}".format(sys.path))
sys.stdout.flush()
import etl

from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder

'''

method make_annual_citations() pretties up most titles that added upper case to each word,
but REMOVES some uppercase words where they probably still should remain.

Parameters:

input_folder must containe some files with names that end 'utf8.txt'

Each such file will be read and proceseed to produce an output file
with the same prefix in the filename, but ending with uf8.txt.html


MORAL: do not try to 'correct' some words that this program changed to
lower case because it will again put them to lowercase.
Rather, this is not designed to be iteratively applied - only to be
hand-modified for final use after it is run ONCE on input.
'''
def make_apa_citations(input_folder=None, output_folder=None,input_glob='**/*utf8.txt'):
    me = 'make_apa_citations'
    if input_folder is None:
        raise ValueError("input_folder is not given as an argument")
    if output_folder is None:
        output_folder = input_folder
    print("{}: using input_folder={},output_folder={},input_glob={}"
          .format(me,input_folder,output_folder,input_glob))
    input_folder_path = Path(input_folder)
    input_file_paths = list(input_folder_path.glob(input_glob))
    n_input_files = 0
    n_citations = 0
    print("Found {} input files".format(len(input_file_paths)))
    for path in input_file_paths:
        input_file_name = "{}\{}".format(path.parents[0], path.name)
        print("Processing file name={}".format(input_file_name))
        n_input_files += 1
        output_file_name = input_file_name + '.html'
        n_file_citations = 0
        with open(str(output_file_name),encoding="utf-8",mode="w") as output_file:
            print("\nReading input file {}".format(path.name))
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
                    print("Got line='{}'.,eline='{}'".format(line,eline))
                    n_file_citations += 1
                    parts = line.split('\t')
                    print("Line has {} tab-separated parts")
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
                  .format(output_file_name, n_file_citations))
            print("</table></body></html>\n",file=output_file)
            # withoutput_file
    # with input_file
    return None
# end make_apa_citations

def run():
    print("Starting")
    # input_folder = make_home_relative_folder("ifas_citations/inputs")
    input_folder = etl.data_folder(linux='/home/robert', windows='U:',
          data_relative_folder='/data/ifas_citations/2016/')

    output_folder = etl.data_folder(linux='/home/robert/', windows='U:/',
          data_relative_folder='data/ifas_citations/2016/')

    make_apa_citations(input_folder=input_folder,output_folder=output_folder
          ,input_glob='*utf8.txt')
    print("Done!")

# RUN
run()
