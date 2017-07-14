import sys,os, os.path,platform
sys.path.append('{}\\git\\citrus\\modules'.format(os.path.expanduser('~')))

print("Using paths in sys.path:")
for i,sp in enumerate(sys.path):
    print("sys.paths[{}]={}".format(i,repr(sp)))
import pymarc
from pymarc import MARCReader
import etl
import codecs
from collections import OrderedDict
'''
I ran a slightly modified version of this same code to generate the list of all fields for this input file
and copy-pasted them here to l_subfields
'''
l_subfields_5000 = [
    'c001_data', 'c003_data', 'c005_data', 'c008_data', 'c040_a', 'c040_c', 'c040_d', 'c100_a', 'c245_a'
    , 'c260_a' , 'c260_b', 'c260_c', 'c300_a', 'c300_c', 'c500_8', 'c500_a', 'c510_a', 'c510_c', 'c590_a'
    , 'c590_x', 'c591_a', 'c591_x', 'c595_a', 'c595_c', 'c595_d', 'c595_f', 'c595_k', 'c595_n'
    , 'c595_r', 'c599_a', 'c599_x', 'c852_a', 'c852_b', 'c852_e', 'c852_n', 'c852_r', 'c852_s'
    , 'c852_v'
]
l_subfields_100 = [
    'c001_data', 'c003_data', 'c005_data', 'c008_data', 'c010_a', 'c035_a', 'c040_a', 'c040_b', 'c040_c', 'c040_d'
, 'c041_a', 'c043_a', 'c050_a', 'c050_b', 'c100_a', 'c100_c', 'c100_d', 'c100_q', 'c110_a', 'c110_b'
, 'c240_a', 'c245_a', 'c245_b', 'c245_c', 'c246_a', 'c250_a', 'c260_a', 'c260_b', 'c260_c', 'c300_a'
, 'c300_b', 'c300_c', 'c490_a', 'c500_5', 'c500_8', 'c500_a', 'c500_t', 'c504_a', 'c505_a', 'c510_a'
, 'c510_c', 'c533_7', 'c533_a', 'c533_b', 'c533_c', 'c533_d', 'c533_e', 'c533_f', 'c533_n', 'c588_a'
, 'c590_a', 'c590_x', 'c591_a', 'c591_x', 'c595_a', 'c595_c', 'c595_d', 'c595_f', 'c595_k', 'c595_n'
, 'c595_r', 'c599_2', 'c599_a', 'c599_b', 'c599_c', 'c599_e', 'c599_h', 'c599_i', 'c599_j', 'c599_m'
, 'c599_q', 'c599_x', 'c599_z', 'c600_a', 'c600_d', 'c610_a', 'c650_2', 'c650_a', 'c650_v', 'c650_x'
, 'c650_z', 'c651_a', 'c651_v', 'c651_x', 'c651_y', 'c700_a', 'c700_d', 'c700_e', 'c710_a', 'c710_b'
, 'c752_a', 'c752_d', 'c776_a', 'c776_c', 'c776_d', 'c776_i', 'c776_t', 'c776_w', 'c852_a', 'c852_b'
, 'c852_e', 'c852_h', 'c852_n', 'c852_p', 'c852_q', 'c852_r', 'c852_s', 'c852_v', 'c856_3', 'c856_u'
, 'c856_z'
]
l_subfields = [
 'c001_data', 'c003_data', 'c005_data', 'c008_data', 'c010_a', 'c010_z', 'c012_a', 'c012_i', 'c015_2', 'c015_a'
, 'c016_2', 'c016_a', 'c022_2', 'c022_a', 'c022_l', 'c024_a', 'c024_z', 'c035_9', 'c035_a', 'c035_z'
, 'c040_a', 'c040_b', 'c040_c', 'c040_d', 'c040_e', 'c040_q', 'c041_a', 'c041_h', 'c043_a', 'c045_a'
, 'c045_b', 'c048_a', 'c050_a', 'c050_b', 'c060_a', 'c060_b', 'c070_a', 'c070_b', 'c072_a', 'c082_2'
, 'c082_a', 'c082_b', 'c084_2', 'c084_a', 'c086_a', 'c100_a', 'c100_b', 'c100_c', 'c100_d', 'c100_e'
, 'c100_j', 'c100_q', 'c100_v', 'c110_S', 'c110_a', 'c110_b', 'c110_c', 'c110_d', 'c110_f', 'c110_k'
, 'c111_a', 'c111_d', 'c111_q', 'c130_a', 'c130_d', 'c130_l', 'c130_n', 'c240_a', 'c240_d', 'c240_f'
, 'c240_g', 'c240_k', 'c240_l', 'c240_s', 'c245_a', 'c245_b', 'c245_c', 'c246_a', 'c246_i', 'c247_a'
, 'c247_b', 'c247_f', 'c250_a', 'c250_b', 'c260_a', 'c260_b', 'c260_c', 'c300_a', 'c300_b', 'c300_c'
, 'c310_a', 'c310_b', 'c321_a', 'c321_b', 'c362_a', 'c362_z', 'c490_a', 'c490_v', 'c500_5', 'c500_8'
, 'c500_a', 'c500_b', 'c500_c', 'c500_t', 'c500_x', 'c501_5', 'c501_a', 'c502_a', 'c504_a', 'c505_a'
, 'c505_c', 'c509_a', 'c510_a', 'c510_b', 'c510_c', 'c510_x', 'c515_a', 'c515_z', 'c520_a', 'c525_a'
, 'c530_a', 'c533_7', 'c533_a', 'c533_b', 'c533_c', 'c533_d', 'c533_e', 'c533_f', 'c533_m', 'c533_n'
, 'c546_a', 'c550_a', 'c555_a', 'c580_a', 'c588_a', 'c590_a', 'c590_c', 'c590_x', 'c591_a', 'c591_x'
, 'c591_z', 'c595_a', 'c595_c', 'c595_d', 'c595_f', 'c595_k', 'c595_n', 'c595_r', 'c599_2', 'c599_3'
, 'c599_a', 'c599_b', 'c599_c', 'c599_e', 'c599_h', 'c599_i', 'c599_j', 'c599_m', 'c599_p', 'c599_q'
, 'c599_r', 'c599_t', 'c599_u', 'c599_v', 'c599_w', 'c599_x', 'c599_z', 'c600_2', 'c600_a', 'c600_b'
, 'c600_c', 'c600_d', 'c600_e', 'c600_j', 'c600_q', 'c600_t', 'c600_v', 'c600_x', 'c600_z', 'c610_2'
, 'c610_a', 'c610_b', 'c610_j', 'c610_k', 'c610_t', 'c610_v', 'c610_x', 'c610_y', 'c610_z', 'c611_a'
, 'c611_c', 'c611_d', 'c611_n', 'c630_a', 'c630_x', 'c650_2', 'c650_a', 'c650_c', 'c650_d', 'c650_j'
, 'c650_t', 'c650_v', 'c650_x', 'c650_y', 'c650_z', 'c651_2', 'c651_a', 'c651_j', 'c651_v', 'c651_x'
, 'c651_y', 'c651_z', 'c653_a', 'c655_2', 'c655_5', 'c655_a', 'c655_x', 'c655_y', 'c655_z', 'c700_5'
, 'c700_a', 'c700_b', 'c700_c', 'c700_d', 'c700_e', 'c700_f', 'c700_j', 'c700_k', 'c700_q', 'c700_t'
, 'c700_v', 'c710_a', 'c710_b', 'c710_d', 'c710_e', 'c710_g', 'c710_k', 'c710_s', 'c710_t', 'c711_a'
, 'c711_c', 'c711_d', 'c730_a', 'c730_d', 'c730_f', 'c730_l', 'c730_p', 'c740_a', 'c752_a', 'c752_b'
, 'c752_d', 'c773_7', 'c773_a', 'c773_b', 'c773_d', 'c773_g', 'c773_t', 'c773_w', 'c774_i', 'c774_t'
, 'c774_w', 'c775_d', 'c775_t', 'c775_w', 'c776_a', 'c776_b', 'c776_c', 'c776_d', 'c776_h', 'c776_i'
, 'c776_s', 'c776_t', 'c776_w', 'c780_t', 'c780_w', 'c785_a', 'c785_s', 'c785_t', 'c785_w', 'c785_x'
, 'c787_d', 'c787_t', 'c787_w', 'c800_a', 'c800_c', 'c800_d', 'c800_f', 'c800_t', 'c800_v', 'c810_a'
, 'c810_n', 'c810_p', 'c810_t', 'c810_v', 'c830_a', 'c830_n', 'c830_p', 'c830_v', 'c852_1', 'c852_a'
, 'c852_b', 'c852_e', 'c852_h', 'c852_n', 'c852_p', 'c852_q', 'c852_r', 'c852_s', 'c852_v', 'c852_z'
, 'c856_3', 'c856_u', 'c856_x', 'c856_y', 'c856_z'
]
'''
Per 20170703 uf email from jesse english, read a certain mrc file and convert to a csv file
for her.
See what I can do... I copied the input to data/UCRiverside folder,
file UCRdatabase_2015-12-04.mrc
'''

def ucr_mrc_to_csv(input_file_name=None,output_file=None,output_fields2=None,output_file2=None):
    # get input data folder
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
            od_recordField = OrderedDict() # Save all field(tag).subfield counts for this record
            for sf in l_subfields:
                od_recordField[sf] = None
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
                            outline += ('{}{}\n'.format(vsep,str(value[i2])))
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
                        f_sf = 'c{}_data'.format(tag)
                        base_value = od_recordField.get(f_sf,None)
                        if base_value is None:
                            od_recordField[f_sf] = str(field.data)
                        else:
                            od_recordField = "{}|{}".format(base_value, str(field.data))
                    else:
                        outline += ('\nindicators={}:'
                            .format(tag,repr(field.indicators)))
                        sfs = field.subfields
                        lsfs = len(sfs)

                        # outline += ("\nSUBFIELDS: count={},subfields={}"
                        #    .format(len(sfs),sfs))
                        if (lsfs > 0):
                            # This tag has subfield values to reckon, whers sfs[]
                            # even indexes are keys, odd are values, then zip to make an odict
                            od_sf = OrderedDict(zip(sfs[0:][::2],sfs[1:][::2]))
                            for key,value in od_sf.items():
                                value = str(value)
                                f_sf = 'c{}_{}'.format(tag,key)
                                outline += ("\nsubfield '{}' value='{}'".format(f_sf,value))
                                # adjust this record's value for this field/subfield
                                base_value = od_recordField.get(f_sf,None)
                                if base_value is None:
                                    # Values cannot have pipe nor tab. Reserved for field separators.
                                    # Replace with spaces.
                                    od_recordField[f_sf] = value.replace("|"," ").replace("\t"," ")
                                else:
                                    od_recordField[f_sf] = "{}|{}".format(base_value, value)
                        else: #field has no subfields, so keep no value in od_recordField
                            pass
                # end for nf,field in enumerate(record.fields)
            # end else (handle formal MARC fields in this record (not csv_fields))
            if i < max_items_detail:
                #just some debug output for first few input marc records
                print(i, ':',outline) # print subfield values
                #next output subfield counts

            for i1,(key,value) in enumerate(od_recordField.items()):
                if i < max_items_detail: #more detailed debug output
                    print('{}:key={},count={}:'.format(i1,key,value)) # print subfield values
                if value is not None: # Keep track of encounterd field value occurrences
                    count = d_fileField.get(key,0)
                    d_fileField[key] = count + 1
            # OUTPUT filterings of this record in multiple outut files
            # First, all fields, in the tab-separated output txt file
            sep = ''
            for value in od_recordField.values():
                print("{}{}".format(sep,value), file=output_file,end="")
                sep = '\t'
            print(file=output_file)

            #Second - output just the fields mentioned in output_fields2
            sep = ''
            for key,value in od_recordField.items():
                if key in output_fields2:
                    print("{}{}".format(sep,value), file=output_file2,end="")
                    sep = '\t'
            print(file=output_file2)

        #for i,record in enumerate(reader)
    # end with open
    #output fileField final found field-subfields and counts among the input
    print("\nTOTAL KEYS WITH RECORD COUNTS AMONG ALL INPUT ITEMS:")
    od = OrderedDict(sorted(d_fileField.items()))
    print (" *********** START ALL FIELDS *************")
    for i,(key,value) in enumerate(od.items()):
        #print('{}:key={},count={}:'.format(i,key,value)) # print subfield values
        if (i % 10 == 0):
            print()
        print(", '{}'".format(key), end="")
    print ("\n *********** END ALL FIELDS *************")

    threshholds=[16000,13000, 10000,5000,3000,2000,1000,500,100]
    for thidx, threshhold in enumerate(threshholds):
        print("\nCOLUMNS FOR THRESHHOLD VALUE={}".format(threshhold))
        tcount = 0
        keysep=""
        for i,(key,value) in enumerate(od.items()):
            if value >= threshhold:
                tcount += 1
                print("{} '{}'".format(keysep,key),end="")
                keysep= ','
                #print('{}:key={},count={}:'.format(tcount,key,value)) # print subfield values
        print("\nEND COLUMNS THRESHOLD VALUE={}".format(threshhold))
    return

in_folder_name = etl.data_folder(linux='/home/robert/git/citrus/data/',
    windows='c:/users/podengo/git/citrus/data/', data_relative_folder='UCRiverside')

out_folder_name = etl.data_folder(linux='/home/robert/git/outputs/jessica_english/',
    windows='c:/users/podengo/git/outputs/jessica_english/', data_relative_folder='UCRiverside')

#os.makedirs(out_folder_name, exist_ok=True)

input_file_name = '{}/UCRdatabase_2015-12-04.mrc'.format(in_folder_name)
output_file_name = '{}/UCRdatabase_all_2015-12-04.txt'.format(out_folder_name)
output_file_name2 = '{}/UCRdatabase_selected_2015-12-04.txt'.format(out_folder_name)

with open(output_file_name, mode='w', encoding='utf-8') as output_file, \
     open(output_file_name2, mode='w', encoding='utf-8') as output_file2:

        # Insert first row of key (marc subfield names to output file first)
        l_subfields2 = l_subfields_5000
        for ofile,lfields in [(output_file, l_subfields), (output_file2,l_subfields2)]:
            sep = ""
            for key in lfields:
                print("{}{}".format(sep,key), end="",file=ofile)
                sep = '\t'
            print(file=ofile)

        # Read input marc file and produce output tab-separated file
        ucr_mrc_to_csv(input_file_name=input_file_name,output_file=output_file
            ,output_fields2=l_subfields2, output_file2=output_file2)

print("Done.")
