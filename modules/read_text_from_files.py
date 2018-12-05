import os
import sys

import re
def get_file_path(bib, vid ):    
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (sep + vid) 
    flag = 0
    str1=""
    try:
        for filename in os.listdir(path):
            
            if re.search(".txt$",filename):            
                flag = 1
                f = open(path+sep+filename, "r")
                for line in f:
                    str1+=str(line)
            
        
        if flag != 1:
            print("There is no .txt file in the folder")
            
    except:
        print("enter a valid BIB:VID value")    

    print(str1)

    return "OK"
        
get_file_path("AA00000074","00001")