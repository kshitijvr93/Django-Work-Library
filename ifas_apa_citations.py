# 20170315 - Robert V. Phillips
# Python3 Code that runs in a Jupyter Cell
# to produce APA style citations from tab-delimited .txt files in a given input directory
'''NOTE: This pretties up most titles that added upper case to each word, but REMOVES some uppercase words where they probably still should remain.
MORAL: do not try to 'correct' some words that this program changed to lower case because it will again put them to lowercase.
Rather, this is not designed to be iteratively applied - only to be hand-modified for final use after it is run ONCE on input.'''
from pathlib import Path
import re

def has_digit(inputString):
    return bool(re.search(r'\d', inputString))
def has_upper(inputString):
    return any(i.isupper() for i in inputString)

'''
Method escape_xml_text(str)

Replace text xml characters in given 'str' with their 'xml quotable' formats.
Also replace tabs with space for easier conversion of multiple fields later
to tab-separated values.

Return the altered str
'''
html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    "\t": " ", # extra:replace tabs to create tab-delimited outputs when needed
}

def html_escape(text):
    #text = str(text.encode('ascii', 'xmlcharrefreplace'))
    text_out = ""
    for c in text:
        text_out += str(html_escape_table.get(c,c) )
    #text_out = text_out.encode('utf-8', 'xmlcharrefreplace')
    return text_out

def make_apa_citations(input_folder='c:/rvp/tmpdir/citations/2017_ifas_test', output_folder=None):

    if output_folder is None:
        output_folder = input_folder
    input_folder_path = Path(input_folder)
    input_file_paths = list(input_folder_path.glob('**/*.txt'))
    n_input_files = 0
    n_citations = 0

    for path in input_file_paths:
        input_file_name = "{}\{}".format(path.parents[0], path.name)
        n_input_files += 1
        output_file_name = input_file_name + '.html'
        n_file_citations = 0

                    index = colskip
                    if nparts > index:
                        authors = (parts[index].replace('"','').replace(',;', ',')
                            .replace('; ', ', '))

                    index += 1
                    if nparts > index: pubyear = parts[index]

                    index += 1
                    if nparts > index: ### TITLE ###

                        # Replace nonbreaking spaces with 'normal' spaces first
                        title = parts[index].replace('\u00A0',' ')
                        # Remove multiple spaces everywhere. Split with no arguments adds this service
                        title = ' '.join(title.split())

                        # Remove troublesome quotation characters for APA citations
                        title = title.replace('"','')

                        words = title.split(' ')
                        # Enforce APA title style: First char of word must be capitalized, but lower
                        # first char for other words in title
                        title = ''
                        delim = ''
                        for word in words:
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
                #end processing all input file lines
            print("Produced APA citation output file {} with {} citations."
                  .format(output_file_name, n_file_citations))

            print("</table></body></html>\n",file=output_file)
        #end output
print("Starting")
make_apa_citations()
print("Done!")
