'''
Python3 program mets_copy

Summary:

Python3 code mets_copy.py is used to facilitate manual editing of UF DPS citrus label collection for
the 'deeply rooted' project started in April 2017. Its general purpose is to copy a set of UFDC bibs mets files from
the resources diretory to an external location for editing and re-insertion into the UFDC resources.

Ideally, the set of bibs mets files would be 'locked out of other editing attempts' while edits on the file copies proceed,
but for first cut, this code puts no mechanism or indicators into UFDC SobekCM to lock out other edits while this set
of bibs is 'out for external editing'.

Program mets_copy creates the contents of the output_folder by copying a limited set of bibid.xml files from a
UFDC (production or test) resources folder that uses 'key-pair' folder hierarchy to house mets.xml and accompanying
bib_vid item files.

Note: A special xml2rdb code study 'citrus' is the first consumer of mets_copy.py output.
That citrus study is implemented to read this program's output and convert the citrus mets records' <mods:mods> data
to relational tables in the silodb.  That data might be edited with the database applications or further exported,
say to excel or othe programs. Other 'studies' may easily be created to convert all or other portions of the mets file data
to relational tables.

Another consumer of the mets_copy.py output might be existDB, of another xml editor, to allow in-place edits to the
copied METS files.

Note: Another python3 program: 'implant.py' will implant some or all the edited mods data, or portions of it,
say from excel spreadsheets or other edited formats,  back into the copies of the mets files overwriting unwanted
prior data. The final 'implanted' (or entirely supplanted) mets files would be suitable for copying to the
UFDC inbound folder for the builder to use to update UFDC.

Input params:

filename_bib_vid: string of a .txt file with one field per line, eg, a bib_vid, eg AA00033113_00001
   Input the file of bib_vids, and to start we need only one_column (now column 1 in initial input)
   holding the bib_vid of interest, eg,  a citrus label.

resources_folder:
    For each bib_vid, copy its data from the resources_folder (eg UFDC production's (or test's)  resource folder

output_folder:

    Location under which to paste mets output files, with locations in the format:
     output_folder/<bib_vid>/<bib_vid>.mets.xml

     Note: this way,
     (a) xml2rdb can use this output_folder as input and convert all the xml to relational tables for batch edits, reports, etc.

     (b)also, one can
        (a) optionaly perfrom edits on the mets.xml files
        (b) and copy-paste a set (or all) the top_level bib_vid folders in this output folder and paste them into the
            ufdc inbound folder again for ufdc ingestion.
#
'''
from shutil import copyfile

def get_bibvids(input_file='c:/rvp/tmpdir/deeply_rooted/citrus_bibs.txt',
                output_folder='c:/rvp/elsevier/output_citrus_mets/',
                resources_folder=None):

    if not input_file and output_folder and resources_folder:
        raise Exception("Bad args")

    # Read input dictionary that maps bibid_vid to pii value:
    in_fn_pii_bibvid = 'c:/rvp/tmpdir/deeply_rooted/citrus_bibs.txt'

    d_bibvid = {}
    skip = 3
    i = 0;
    with open(in_fn_pii_bibvid, "r") as d_file:
        for line in d_file:
            line = line.replace('\n','')
            i += 1;
            if (i <= skip):
                continue
            parts = line.split('\t')
            b = parts[0]
            d_bibvid[b] = 1

            # open the input file and copy it to the output folder
            kp_name = "{}/{}/{}/{}/{}/00001/".format(b[0:2],b[2:4],b[4:6],b[6:8],b[8:10])
            source_filename = resources_folder + kp_name + b + "_00001.mets.xml"
            output_filename = output_folder + b + "_00001.mets.xml"
            if (i < 10 or i %100 == 0):
                print("Line {} has bibvid='{}',source_filename={}".format(
                i,b,source_filename))
                print("Copying from source='{}' to dest='{}'".format(source_filename, output_filename))
            #copy the input file to output_folder
            copyfile(source_filename, output_filename)
            #break

    return d_bibvid

def runme():
    d_bibvid = get_bibvids()
    return d_bibvid


print("Starting2")

input_file='c:/rvp/tmpdir/deeply_rooted/citrus_bibs.txt'
output_folder='c:/rvp/elsevier/output_citrus_mets/'
resources_folder='//flvc.fs.osg.ufl.edu/flvc-ufdc/resources/'

d_bibvid = get_bibvids(input_file=input_file,output_folder=output_folder,
            resources_folder=resources_folder)
print("Got {} bibvids. Done!".format(len(d_bibvid)))
