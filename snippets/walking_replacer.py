# walking replacer - walk from a directory to all mets files and use regex to change affected lines

import sys,re;
from pathlib import Path
# import sys,re;[sys.stdout.write(re.sub('PATTERN', 'SUBSTITUTION', line)) for line in sys.stdin]

def walking_replacer(headpath=None, outpath=None,ext=None, resubs=None):
    if not (headpath and outpath and resubs and ext):
        print("walking_replacer: headpath, outpath, and resubs must be given. Goodbye.")
        return 0

    p = Path(headpath)
    ps =  list(p.glob('**/*.{}'.format(ext)))
    print("Under path={} there are {} '{}' files".format(p.name, len(ps), ext))

    max_xml_files = 99999
    skipfrontfiles = 0
    mod_print = 100
    d_stats = {}

    i = 0
    for i, p in enumerate(ps):
        if i >= max_xml_files:
            print("\n******** BREAKING INPUT at {} FILES *****\n".format(i))
            break
        input_filename = "{}/{}".format(ps[i].parents[0], ps[i].name)
        if (i >= max_xml_files):
            break;
        out_filename = outpath + '\\' + ps[i].name
        if i % mod_print == 0 :
            print("\nReading: Path number {},\n\t input file name={},\n\t out_filename={}"
                   .format(i+1, input_filename, out_filename))

        # outfile = open(outfilename, 'wt', encoding='utf-8')
        with open(input_filename, 'rt', encoding='utf-8') as infile:
            with open(out_filename, 'wt', encoding='utf-8') as outfile:
                '''
                tickler = None
                lines = []
                for line in infile:
                    # if there is a tickler value save it to a resub pair
                    # so if there is NOT a ; in current extent, the tickler will be appended?
                    lines.append(line)
                '''

                for line in infile:
                    # make ordered line replacements
                    for resub in resubs:
                        line = re.sub(resub[0], resub[1], line)

                    outfile.write(line)
    return i

#
