import sys,os, os.path,platform
sys.path.append('{}/github/citrus/modules'.format(os.path.expanduser('~')))
import pymarc
from pymarc import MARCReader
import etl
import codecs
from collections import OrderedDict

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
    use_csv_fields = 0
    d_fileField = {} # save counts of records that use each field.subfield
    max_items_detail = 2;
    with open(input_file_name, mode='rb') as infile:
        reader = MARCReader(infile)
        max_records = 0
        for i,record in enumerate(reader):
            if max_records > 0 and i > max_records:
                break
            fsep = ''
            outline = ''
            d_recordField = {} # Save all field(tag).subfield counts for this record
            print(" [{}] ".format(i), end="")
            if i % 20 == 0:
                print()
            if i < max_items_detail:
                print("RECORD {} of type {}, leader='{}' with {} MARC fields FOLLOWS:\n"
                .format(i, type(record),record.leader,len(record.fields)))
            if (use_csv_fields): #show 'pymarc' field values for this record
                for nf,field_name in enumerate(csv_fields):
                    outline += '\nFIELD {}={}: '.format(nf,field_name)
                    value = getattr(record, field_name)()
                    outline += fsep
                    if type(value) is list:
                        vsep = ''
                        for i2 in range(len(value)):
                            outline += ('{}{}\n'.format(vsep,value[i2]))
                            vsep = '|'
                    elif type(value) is str:
                        outline += (str(value))
                    fsep = '-----'
            else: # show formal MARC fields in this record
                for nf,field in enumerate(record.fields):
                    tag = field.tag
                    outline += '\nFIELD {}, tag={}:'.format(nf+1, tag)
                    if tag < '010' and tag.isdigit():
                        outline += ("\ndata='{}'".format(field.data))
                        f_sf = '{}.data'.format(tag)
                        count = d_recordField.get(f_sf,0)
                        d_recordField[f_sf] = count + 1
                    else:
                        outline += ('\nindicators={}:'
                            .format(tag,repr(field.indicators)))
                        sfs = field.subfields
                        lsfs = len(sfs)

                        # outline += ("\nSUBFIELDS: count={},subfields={}"
                        #    .format(len(sfs),sfs))
                        if (lsfs > 0):
                            # even indexes are keys, odd are values, then zip to make odict
                            od_sf = OrderedDict(zip(sfs[0:][::2],sfs[1:][::2]))
                            for key,value in od_sf.items():
                                outline += ("\nsubfield '{}' value='{}'"
                                #.format(key,repr(value)))
                                .format(key,value))
                                # adjust this record's count for this field/subfield
                                f_sf = '{}.{}'.format(tag,key)
                                count = d_recordField.get(f_sf,0)
                                d_recordField[f_sf] = count + 1
                        else:
                            f_sf = '{}'.format(tag)
                            count = d_recordField.get(f_sf,0)
                            d_recordField[f_sf] = count + 1
                            pass
                # end for nf,field in enumerate(record.fields)
            # end else (formal MARC fields)
            if i < max_items_detail:
                print(i, ':',outline) # print subfield values
                #next output subfield counts

            for i1,(key,value) in enumerate(d_recordField.items()):
                if i < max_items_detail:
                    print('{}:key={},count={}:'.format(i1,key,value)) # print subfield values
                count = d_fileField.get(key,0)
                d_fileField[key] = count + 1
        #for i,record in enumerate(reader)
    # end with open
    #output fileField final found field-subfields and counts among the input
    print("\nTOTAL KEYS WITH RECORD COUNTS AMONG ALL INPUT ITEMS:")
    od = OrderedDict(sorted(d_fileField.items()))
    for i,(key,value) in enumerate(od.items()):
        print('{}:key={},count={}:'.format(i,key,value)) # print subfield values

    threshholds=[16000,13000, 10000,5000,3000,2000,1000,500,100]
    for threshhold in threshholds:
        print("\nTHRESHHOLD VALUE={}".format(threshhold))
        tcount = 0
        for i,(key,value) in enumerate(od.items()):
            if value >= threshhold:
                tcount += 1
                print('{}:key={},count={}:'.format(tcount,key,value)) # print subfield values
    return
ucr_mrc_to_csv()
print("Done.")
