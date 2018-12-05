import os
import sys

import re
def get_file_path(bib, vid ):    
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (vid)
    for filename in os.listdir(path):
        if re.match(".txt$", filename):
            with open(filename, "r") as f:
            # Read each line of the file
                for line in file:
                    print line.split()

    

    return "OK"
        
get_file_path("AA000074","00001")