#
# eldpii - elsevier load date and pii relationship
# extract from an input directory, say '2016', which has month/day subdirectories,
# filenames like pii_*xml, all the * values, (assumed to be normalized pii values)
# and associated y4md dates.

#
from pathlib import Path
import os

def get_pii_ymd_by_years(input_base_folder=None, years=None):
    for year in years:
        if type(year) is not int:
            raise Exception("year = '{}', but must be integer".format(repr(year)))

        year_folders = []
        d_pii_ymd = {}

    for year in years:
        input_folder = '{}/{}'.format(input_base_folder, year)
        print("Examining input folder='{}'".format(repr(input_folder)))
        input_year_path = Path(input_folder)
        paths = list(input_year_path.glob('**/pii_*.xml'))
        print("Found {} pii xml files under {}.".format(len(paths),input_year_path))
        for i,path in enumerate(paths):
            #path_resolved = path.resolve()
            #print("resolved={}".format(path_resolved.name))
            #print("os abspath='{}'".format(os.path.abspath(path.name)))
            #print("str(p)={}".format(str(path)))
            parts = str(path).split(os.sep)
            basename = parts[-1]
            #print("parts={}".format(repr(parts)))
            dd = parts[-2]
            mm = parts[-3]
            #print("pm={},pd={}".format(pm,pd))
            ymd = "{}-{}-{}".format(year,mm,dd)
            parts1 = basename.split('_')
            #print(parts1)
            parts2 = parts1[1].split('.')
            #print(parts2)
            pii = parts2[0]
            if pii in d_pii_ymd:
                print("For pii={},overwriting former ymd={}".format(pii,ymd))
            d_pii_ymd[pii] = ymd
            #print(pii)
            #print("basename={},ymd={}, pii={}".format(basename,ymd,pii))

        #Get all paths
        return d_pii_ymd
#

input_base_folder = 'c:/rvp/elsevier/output_ealdxml'
years = [2016]

d_pii_ymd = get_pii_ymd_by_years(input_base_folder=input_base_folder,years=years)


print("Done")
