import sys,os, os.path,platform
sys.path.append('{}/github/citrus/modules'.format(os.path.expanduser('~')))
import pymarc
from pymarc import MARCReader
import etl
import codecs

'''
Per 20170703 uf email from jesse english, read a certain mrc file and convert to a csv file
for her.
See what I can do... I copied the input to data/UCRiverside folder,
file UCRdatabase_2015-12-04.mrc
'''

def ucr_mrc_to_csv():
    # get input data folder
    in_folder_name = etl.data_folder(linux='/home/robert/github/citrus/data/',
        windows='u:/data/', data_relative_folder='UCRiverside')
    input_file_name='{}/UCRdatabase_2015-12-04.mrc'.format(in_folder_name)
    csv_fields=[
        'title', 'author','isbn','subjects','location','notes','physicaldescription'
        ,'publisher', 'pubyear'
    ]
    print("Using {} csv fields".format(len(csv_fields)))
    use_csv_fields = 1
    with open(input_file_name, mode='rb') as infile:
        reader = MARCReader(infile)
        for i,record in enumerate(reader):
            fsep = ''
            outline = ''
            print("RECORD {} FOLLOWS:".format(i))
            if (use_csv_fields):
                for nf,field in enumerate(csv_fields):
                    outline += '\nFIELD {}={}: '.format(nf,field)
                    value = getattr(record, field)()
                    outline += fsep
                    if type(value) is list:
                        vsep = ''
                        for i2 in range(len(value)):
                            outline += ('{}{}\n'.format(vsep,value[i2]))
                            vsep = '|'
                    elif type(value) is str:
                        outline += (str(value))

                    fsep = '-----'
                if i > 15:
                    break
                print(i, ':',outline)
        pass
    return
ucr_mrc_to_csv()
print("Done.")
