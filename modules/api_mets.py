import uuid
import os, sys
from django.db import models
from django.utils import timezone
import datetime
#from django_enumfield import enum

#other useful model imports at times (see django docs, tutorials):
import datetime
from django.utils import timezone
from maw_utils import SpaceTextField, SpaceCharField, PositiveIntegerField

import html
import sys, os, os.path, platform
import re
import sys
import requests
import urllib, urllib.parse
import json
import pprint
from collections import OrderedDict
from io import StringIO, BytesIO
from datetime import datetime
import etl
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import datetime
import pytz
import os
import urllib.request
import requests, lxml




import threading
from time import sleep

def get_title_from_xml_path(bib, vid ):    
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (sep + vid) 
    flag = 0
    str1=""
    str_out = ""
    
    
    try:
        list1 = os.listdir(path)
        list1.sort()
        for filename in list1:
            
            char_count = 0
            if re.search(".mets.xml$",filename):    
                flag = 1
                f = open(path+sep+filename, "r",encoding='utf8')            
                
                for line in f:                
                    if line.strip():                                    
                        str1+= line + " "                    
                f.close()  
        if flag != 1:
            print("There is no .mets file in the folder")


        root = etree.fromstring(str1)
        for child in root.findall('.//{*}title'):
            str_out += child.text
        
        # for child in root.findall('.//{*}abstract'):
        #     print(child.text)

    except:
        print("enter a valid BIB:VID value")    

    print(str_out)
    return str_out


get_text_from_xml_path("AA00000074","00001")