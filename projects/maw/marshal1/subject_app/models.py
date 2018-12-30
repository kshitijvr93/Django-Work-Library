from django.db import models

# Create your models here.
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
import time
from dps.models import BatchSet, BatchItem
#from django.apps import apps
#BatchSet = apps.get_model('dps','BatchSet')
#BatchItem = apps.get_model('dps','BatchSet')
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
import maw_settings
from time import sleep
from django.contrib.auth import get_user_model
User = get_user_model()

get_suggested_xml_fmt = '''
<TMMAI project="{project}" location = ".">
<Method name="getSuggestedTerms" returnType="{return_type}"/>
<VectorParam>
<VectorElement>{doc}</VectorElement>
</VectorParam>
</TMMAI>
'''



'''
NOTE: rather than have a separate file router.py to host HathiRouter, I just
put it here. Also see settings.py should include this dot-path
as one of the listed strings in the list
setting for DATABASE_ROUTERS.

'''
# Maybe move the HathiRouter later, but for now keep here
#
class SubjectAppRouter:
    '''
    A router to control all db ops on models in the Subject_App Application.
    '''

    # app_label is really an app name. Here it is hathitrust.
    app_label = 'subject_app'

    # app_db is really a main settings.py DATABASES name, which is
    # more properly a 'connection' name
    app_db = 'subject_app_connection'

    '''
    See: https://docs.djangoproject.com/en/2.0/topics/db/multi-db/
    For given 'auth' model (caller insures that the model is always an auth
    model ?),  return the db alias name (see main DATABASES setting in
    settings.py) to use.
    '''
    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return self.app_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (   obj1._meta.app_label == self.app_label
           or  obj2._meta.app_label == self.app_label):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == self.app_db
        return None

#end class

# Create your models here.
#
# NB: we accept the django default of prefixing each real
# db table name with the app_name, hence the model names
# below do not start with hathi or hathitrust.
# class HathiItemState(enum.Enum):
#       HAS_FOLDER = 0
#       FOLDER_LOADED = 1
#       FILES_EXAMINED = 2
#       FILES_NEED_CHANGES = 3
#       YAML_CREATED = 4


from pathlib import Path
from natsort import natsorted
from shutil import copy2, make_archive, move

def line(s=''):
    return '\n>' + s
def resource_path_by_bib_vid(bib_vid=None):
    if not bib_vid:
        raise ValueError(f'Bad bib_vid={bib_vid}')
    parts = bib_vid.split('_')
    count = len(parts)
    if count != 2:
        raise ValueError(f'Bad count of parts for bib_vid={bib_vid}')
    if len(parts[0]) != 10:
        raise ValueError(f'Bib is not 8 characters in bib_vid={bib_vid}')
    if len(parts[1]) != 5:
        raise ValueError(f'Vid is not 5 characters in bib_vid={bib_vid}')
    path = ''
    sep = ''
    for i in range(0,10,2):
        path = path + sep + parts[0][i:i+2]
        sep = os.sep
    path += sep
    path += parts[1]
    return path

import hashlib
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

import os
import datetime
def modification_utc_str_by_filename(filename):
    t = os.path.getmtime(filename)
    d = datetime.datetime.fromtimestamp(t)
    du = datetime.datetime.utcfromtimestamp(t)
    tz = du - d
    utc_str = du.strftime("%Y-%m-%dT%H:%M:%SZ")
    d_str = d.strftime("%Y-%m-%dT%H:%M:%S")
    return d_str, tz, utc_str


# This function gets subject terms based on the input for thesis( for eg. floridathes) from all the text inside every .txt files , titles 
# from .mets files and abstract from .mets files for every BIB , VID combinations in a batch Job.


def get_subject_from_thesis(obj):
    me = 'get_subject_from_thesis'
    print(f"{me}: Getting subjects for batch_set {obj.batch_set}")
    sys.stdout.flush()
    
# string sent to the api for titles
    titles_string_for_api = ""

# string sent to the api for abstract
    abstract_string_for_api = ""

# string sent to the api for text
    text_string_for_api = ""

# string to write to .txt file that has word count and subject outputs for every input i.e. title, text and abstract
    consolidated_string_to_be_written = "\n-----------------------------------------------FULL TEXT FROM FILES----------------------------------------------------- \n\n"

# string containing all the subjects( text, title and abstract)
    subject_string=""
    

# generate strings by concatenating strings from every file inside BIB VID and from every BIB VID inside a Batch Job for API calls to 
# access innovation

    batch_items = BatchItem.objects.filter(batch_set=obj.batch_set_id)

    for batch_item in batch_items:
        bib = batch_item.bibid
        vid = batch_item.vid

        text_from_each_file = get_text_from_file_path(bib, vid )[0]
        text_to_write_from_each_file = get_text_from_file_path(bib, vid )[1]
       
        text_string_for_api += " " + text_from_each_file
        consolidated_string_to_be_written += " " + text_to_write_from_each_file

        title_from_each_file = get_title_from_xml_path(bib, vid)        
        titles_string_for_api += " " + title_from_each_file 

        abstract_from_each_file = get_abstract_from_xml_path(bib , vid)
        abstract_string_for_api += " " + abstract_from_each_file

# taken from input such as floridathes     
    project = obj.thesaurus

# truncate if the total number of characters exceeds 500000 characters for the string
    if len(text_string_for_api)>50000:
        doc = text_string_for_api[0:50000]   
    else:
        doc = text_string_for_api

    doc = re.sub(r'\s+', ' ',doc)    

# make the API call with string = FULL TEXT    
    result1 = get_suggested_terms_data_harmony_api_result(project=project, doc=doc)
    print(result1.text)
# parsing for lxml
    root = etree.fromstring(result1.content)
    consolidated_string_to_be_written += "\n \n \n"+"------------------------------------SUBJECT TERMS : FULL TEXT--------------------------------\n \n \n"

# store the each of the subject terms for FULL TEXT in Parsed_Subjects Table and also add it to consolidated string which will be
# written to a file

    for child in root.findall('.//{*}VectorElement'):
        if re.search(r"<TERM>.*",child.text):            
            
            subject_string+=" "+child.text[6:-7]
            consolidated_string_to_be_written += " "+str(child.text[6:-7])+"\n"
            sub1 = Parsed_Subject() 
            sub1.subject_batchset_id = obj           
            sub1.subject_term_scraped = child.text[6:-7].split('|')[0]
            sub1.subject_term_count = int(str(child.text[6:-7]).split('|')[1].split(" ",1)[0][1:-1])
            sub1.subject_term_hinted = str(child.text[6:-7]).split('|')[1].split(" ",1)[1]
            sub1.subject_type = "Full Text"
            sub1.save()


# add all the Titles for every BIB VID inside a Batch Job to the string that will be written to a file
    consolidated_string_to_be_written += "\n-------------------------------------------------------- TEXT FROM TITLES ---------------------------------------------------------------- \n\n"
    consolidated_string_to_be_written += titles_string_for_api+"\n"


# truncate if the total number of characters exceeds 500000 characters for the string
    if len(titles_string_for_api)>50000:
        doc = titles_string_for_api[0:50000]   
    else:
        doc = titles_string_for_api

# substitute any excess spaces and remove any non aplha numeric characters from the string that is to be passed to the API
    doc = re.sub(r'\s+', ' ',doc)
    doc = ''.join(e for e in doc if e.isalnum() or e==" ")

# make the API call with string = TITLE

    result2 = get_suggested_terms_data_harmony_api_result(project=project, doc=doc)
    print("Result Title")
    print(result2.text)

# parsing for lxml

    root = etree.fromstring(result2.content)
    consolidated_string_to_be_written += "\n \n \n"+"------------------------------------SUBJECT TERMS : TITLE--------------------------------\n \n \n"

# store the each of the subject terms for TITLE in Parsed_Subjects Table and also add it to consolidated string which will be
# written to a file 

    for child in root.findall('.//{*}VectorElement'):
        if re.search(r"<TERM>.*",child.text):           
            
            subject_string+=" "+child.text[6:-7]
            consolidated_string_to_be_written += " "+str(child.text[6:-7])+"\n"
            sub1 = Parsed_Subject() 
            sub1.subject_batchset_id = obj           
            sub1.subject_term_scraped = child.text[6:-7].split('|')[0]
            sub1.subject_term_count = int(str(child.text[6:-7]).split('|')[1].split(" ",1)[0][1:-1])
            sub1.subject_term_hinted = str(child.text[6:-7]).split('|')[1].split(" ",1)[1]
            sub1.subject_type = "Title"
            sub1.save()

    

# add all the Abstracts for every BIB VID inside a Batch Job to the string that will be written to a file
    consolidated_string_to_be_written += "\n--------------------------------------------------------------- TEXT FROM ABSTRACTS------------------------------------------------- \n\n"
    consolidated_string_to_be_written += abstract_string_for_api+"\n"

# truncate if the total number of characters exceeds 500000 characters for the string  
    if len(abstract_string_for_api)>50000:
        doc = abstract_string_for_api[0:50000]   
    else:
        doc = abstract_string_for_api

# substitute any excess spaces and remove any non aplha numeric characters from the string that is to be passed to the API
    doc = re.sub(r'\s+', ' ',doc)
    doc = ''.join(e for e in doc if e.isalnum() or e==" ")

# make the API call with string = ABSTRACT
    result3 = get_suggested_terms_data_harmony_api_result(project=project, doc=doc)
    print(result3.text)

# parsing for lxml
    root = etree.fromstring(result3.content)
    consolidated_string_to_be_written += "\n \n \n"+"------------------------------------SUBJECT TERMS : ABSTRACT--------------------------------\n \n \n"
    
# store the each of the subject terms for ABSTRACT in Parsed_Subjects Table and also add it to consolidated string which will be
# written to a file 
    for child in root.findall('.//{*}VectorElement'):
        if re.search(r"<TERM>.*",child.text):           
            
            subject_string+=" "+child.text[6:-7]
            consolidated_string_to_be_written += " "+str(child.text[6:-7])+"\n"
            sub1 = Parsed_Subject() 
            sub1.subject_batchset_id = obj           
            sub1.subject_term_scraped = child.text[6:-7].split('|')[0]
            sub1.subject_term_count = int(str(child.text[6:-7]).split('|')[1].split(" ",1)[0][1:-1])
            sub1.subject_term_hinted = str(child.text[6:-7]).split('|')[1].split(" ",1)[1]
            sub1.subject_type = "Abstract"
            sub1.save()

# Print Subject String i.e. the string that contains all the subject terms
    print(subject_string)





################################################################################
# CHANGE PATH ACCORDING TO MAW_SETTINGS
################################################################################
################################################################################
    path = 'D:\\resource_items_mets'
    sep = os.sep
    path += sep

# check if maw_work exists inside directory else create a new directory
    if not(os.path.isdir(path+"maw_work")):
        os.mkdir(path)
    
    path += "maw_work"+sep

# check if Subject_Jobs exists inside directory else create a new directory
    if not(os.path.isdir(path+"Subject_Jobs")):
        os.mkdir(path)

    path += "Subject_Jobs"+sep
    path += "id_"+ str(obj.id)
    os.mkdir(path)

# write all the text and their outputs to consolidated text file inside maw_work/Subject_Jobs/job_id/
    f= open(path+sep+"consolidated.txt","w+")
    f.write(consolidated_string_to_be_written)

# Update the Subject_Jobs Table once all the API calls are done
    utc_now = timezone.now()
    obj.end_datetime = utc_now
    obj.status = "Completed"
    obj.subject_terms = subject_string
    

    obj.save()


# functions that takes a String of Text without any special characters and a Thesis as an Input and returns Subject Terms as Output
    
def get_suggested_terms_data_harmony_api_result(
    doc='farming and ranching in Peru', #example from DH Guide v3.13
    #url from email of xxx
    url='http://dh.accessinn.com:9084/servlet/dh',
    project='floridathes', # in 2018 or geothesFlorida'

    #return_type='java.util.String', # error
    return_type='java.util.Vector',

    log_file=sys.stdout,
    verbosity=1):

    me='get_suggested_terms_data_harmony_api_result'
    if doc is None:
        raise Exception("doc document string is required")

    d = ({'doc': doc, 'project':project, 'return_type':return_type, })
    query_xml = get_suggested_xml_fmt.format(**d)

    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        # msg="*** BULDING GET REQUEST FOR SCIDIR RESULTS FOR URL='{url}' ***"
        # print(f'msg(url)')
        response = requests.post(url, data=query_xml.encode('utf-8'))
    except:
        raise Exception("Cannot post a request to url={}".format(url))

    #result = json.loads(response.read().decode('utf-8'))

    print( f"{me} got response encoding={response.encoding}".encode('latin-1',errors='replace'),file=log_file)

    print(log_file, f'{me} got response text="{response.text}"'.encode('latin-1',errors='replace'))

    return response
# end def get_suggested_terms_data_harmony_api_result



# reads all text from .txt files inside a particular BIB VID pair and returns all the text content inside them as a String
# Also calculates the character count inside each file and uses it for the consolidated text file
def get_text_from_file_path(bib, vid ): 


################################################################################
# CHANGE PATH ACCORDING TO MAW_SETTINGS
################################################################################
################################################################################
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (sep + vid) 
    flag = 0
    str1=""
    str2=""
    
    char_count_total = 0
    try:

# Every filename inside a directory defined by path is stored in a list and sorted
        list1 = os.listdir(path)
        list1.sort()

# Iterate over every file in a directory
        for filename in list1:
            char_count = 0

# Search for only .txt files and only work on them

            if re.search(".txt$",filename):  
                str2=str2+"\n"+"----------------------------------file:  "+str(filename)+"--------------------------------------------------------------------------------------------------------------------------------------------\n"
                         
                flag = 1

# Open the .txt file
                f = open(path+sep+filename, "r")
                
# Iterate over every line of the file
                for line in f:
                    
# Only operate on non empty lines of a file
                    if line.strip():                   
                        alpha_num_string = ''.join(e for e in line if e.isalnum() or e==" ")
                        alpha_num_string = re.sub(r'\s+',' ',alpha_num_string)                        
                        char_count += len(alpha_num_string.strip()) + 1                        
                        str1+=" "+alpha_num_string.strip()
                        str2+=" "+alpha_num_string.strip()
                f.close()
                char_count_total+= char_count
                str2=str2+"\n-----------------character count:  "+str(char_count)+"  running count:  "+str(char_count_total)+"-------------------------------------------------------------------------------------------------------- \n"
               

            
            
        if flag != 1:
            print("There is no .txt file in the folder")
            
    except:
        print("enter a valid BIB:VID value")    

    
    return [str1,str2]


# reads all text inside title tag from .mets files inside a particular BIB VID pair and returns them as a String
def get_title_from_xml_path(bib, vid ):   


################################################################################
# CHANGE PATH ACCORDING TO MAW_SETTINGS
################################################################################
################################################################################ 
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (sep + vid) 
    flag = 0
    str1=""
    str_out = ""
    
    
    try:

# Every filename inside a directory defined by path is stored in a list and sorted
        list1 = os.listdir(path)
        list1.sort()

# Iterate over every file in a directory
        for filename in list1:
            
            char_count = 0

# Search for only .mets.xml files and only work on them
            if re.search(".mets.xml$",filename):    
                flag = 1

# Open the .mets.xml file
                f = open(path+sep+filename, "r",encoding='utf8')            

# Iterate over every line of the file                
                for line in f:

# Only operate on non empty lines of a file                                   
                    if line.strip():                                                            
                        str1+= line + " "                    
                f.close()  
        if flag != 1:
            print("There is no .mets file in the folder")


        root = etree.fromstring(str1)
        for child in root.findall('.//{*}title'):
            str_out += child.text+" "    
        

    except:
        print("enter a valid BIB:VID value")    

    print(str_out)
    return str_out


# reads all text inside abstract tag from .mets files inside a particular BIB VID pair and returns them as a String
def get_abstract_from_xml_path(bib, vid ):    


################################################################################
# CHANGE PATH ACCORDING TO MAW_SETTINGS
################################################################################
################################################################################
    path = 'D:\\resource_items_mets'
    
    sep = os.sep
    for i in range(0,10,2):
        path += (sep + bib[i:i+2])
    path += (sep + vid) 
    flag = 0
    str1=""
    str_out = ""
    
    
    try:

# Every filename inside a directory defined by path is stored in a list and sorted
        list1 = os.listdir(path)
        list1.sort()

# Iterate over every file in a directory
        for filename in list1:
            
            char_count = 0

# Search for only .mets.xml files and only work on them

            if re.search(".mets.xml$",filename):    
                flag = 1
                f = open(path+sep+filename, "r",encoding='utf8')            

# Iterate over every line of the file                  
                for line in f:   

# Only operate on non empty lines of a file              
                    if line.strip():                                                           
                        str1+= line + " "                    
                f.close()  
        if flag != 1:
            print("There is no .mets file in the folder")


        root = etree.fromstring(str1)
        for child in root.findall('.//{*}abstract'):
            str_out += child.text+" "  
       

    except:
        print("enter a valid BIB:VID value")    

    print(str_out)
    return str_out




class SubjectJob(models.Model):
    '''
    

    '''

    id = models.AutoField(primary_key=True)

    batch_set = models.ForeignKey(BatchSet,related_name="subject_app_batch_set", blank=False, null=False,
      db_index=True,
      help_text="BatchSet for which we generate Subject Terms",
      on_delete=models.CASCADE,)

    thesaurus = SpaceTextField('Thesaurus',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Enter Value for Thesaurus"),
      editable=True,
      )

    subject_terms = SpaceTextField('subject_terms',max_length=2550, null=True, default='',
      blank=True, editable=False,
      )
    create_datetime = models.DateTimeField('Run Start DateTime (UTC)',
        null=True, editable=False)

    #consider to populate user value later.. middleware seems best approach
    # https://stackoverflow.com/questions/862522/django-populate-user-id-when-saving-a-model
    user = models.ForeignKey(User,related_name="subject_app_user", on_delete=models.CASCADE,
      db_index=True, blank=True, null=True)

    notes = SpaceTextField(max_length=2550, null=True, default='note',
      blank=True, help_text= ("General notes about this batch job run"),
      editable=True,
      )
    # Todo: batch job updates the end_datetime and status fields
    end_datetime = models.DateTimeField('End DateTime (UTC)',
        null=True,  editable=False)
    status = SpaceTextField('Run Status',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Status of ongoing or completed run. Check for status updates "
        "as packages are being built."),
      editable=True,
      )

    def save(self,*args,**kwargs):
        me = "SubjectJob.save()"

        super().save(*args, **kwargs)
        #if self.status is None or len(self.status) == 0:
        if self.status is None or len(self.status) == 0:
            # Only start this thread if status is not set
            # Note: we super-saved before this clause becaue
            # the thread uses/needs the autoassigne jp2batch.id value
            # Note: may prevent row deletions later to preserve history,
            # to support graphs of work history, etc.
            thread = threading.Thread(target=get_subject_from_thesis, args=(self,))
            thread.daemon = False
            #process.start()
            thread.start()
            print(f"{me}: started thread.")
            sys.stdout.flush()
            #utc_now = datetime.datetime.utcnow()
            utc_now = timezone.now()
            self.create_datetime = utc_now
            str_now = secsz_start = utc_now.strftime("%Y-%m-%dT%H-%M-%SZ")
            self.status = f"Started processing at {str_now}"
            # Save again so starting status appears immediately
            super().save(*args, **kwargs)

        # super().save(*args, **kwargs)
    # end def save()

    def __str__(self):
        return (
          f"{self.id}")


class Thesaurus(models.Model):
    '''
    Creating a thesaurus table which references subjects tables

    '''

    id = models.AutoField(primary_key=True)

    subject_job_id = models.ForeignKey(SubjectJob,related_name="thesaurus_ref_id", blank=False, null=False,
      db_index=True,
      help_text="Subject ID refrenced from SubjectJob Table",
      on_delete=models.CASCADE,)

    name = SpaceTextField('Name',max_length=2550, null=True, default='',
      blank=True, help_text= (
        "Enter Name for Thesaurus"),
      editable=True,
      )


class Parsed_Subject(models.Model):
    '''
    Creating a subject_description table which references subjects tables

    '''

    id = models.AutoField(primary_key=True)

    subject_batchset_id = models.ForeignKey(SubjectJob,related_name="subject_batchset_id", blank=False, null=False,
      db_index=True,
      help_text="Subject ID refrenced from SubjectJob Table",
      on_delete=models.CASCADE,)
    
    subject_term_scraped = SpaceTextField('subject_term_scraped',max_length=2550, null=True, default='',
      blank=True, editable=False,
      )

    subject_term_count = models.IntegerField(default=0, null=True,help_text='Total number of hits for the subject term')


    subject_term_hinted = SpaceTextField('subject_term_hinted',max_length=2550, null=True, default='',
      blank=True, editable=False,
      )

    subject_type = SpaceTextField('subject_type',max_length=2550, null=True, default='',
      blank=True, editable=False,
      )

    def __str__(self):
        return ""

