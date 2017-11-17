#etl - extract transform load tools.
import datetime
import pytz
import os
import platform
import sys
import re

from pathlib import Path
import hashlib
from collections import OrderedDict
from lxml import etree
from lxml.etree import tostring
from pathlib import Path
import shutil
import stat


def get_json_result_by_url(url,verbosity=1):
    import urllib
    import json

    me = 'get_json_result_by_url'
    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        print("{}:starting with url={}".format(me,url))
        get_request = urllib.request.Request(url, data=None)
    except Exception as exc:
        raise Exception("{}:Cannot send a request to url={}. exc={}".format(me,url,exc))

    try:
        response = urllib.request.urlopen(get_request)
    except Exception as e:
        print("{}: Got exception instead of response for"
              "\n url='{}',\nget_request={}, exception={}"
              .format(me,url, repr(get_request), repr(e)))
        raise
    json_result = json.loads(response.read().decode('utf-8'))
    return json_result
#end get_json_result_by_url

# return name of current python method
def i_am():
    me = inspect.stack()[0][3]

'''
Given arguments start and end day strings, interpretted by the fmt argument,
return a generator for a sequence that yields for each day in the sequence,
two values: the cymd string for the day and the datetime object for the day.

yield cymd_day and datetime object for the day
'''
def sequence_days(cymd_start=None, cymd_end=None,fmt='%Y%m%d'):
    dt_day = datetime.datetime.strptime(cymd_start, fmt )
    dt_end = datetime.datetime.strptime(cymd_end, fmt )
    day_delta = datetime.timedelta(days=1)
    while dt_day <= dt_end:
        cymd_day = dt_day.strftime('%Y%m%d')
        yield cymd_day, dt_day
        dt_day += day_delta
    return

'''
NOTE: for the morning of 20170810, my WIN7 'update' on my UF PC had a 'HOME'
variable defined to U:, which changed the expanduser() return value unexpectedly
because expanduser() has been relying on the USERPROFILE windows env variable because
HOME was not defined. This caused some development snags. Since then, a new restart was
done and HOME is again not defined, but use below code as protection against future outages.

So now we rely specifically on USEPROFILE on non-windows to return path_modules
In all project source code files, must use this to append to sys.path before importing
this etl module and all others in this group

#Get local pythonpath of modules from 'citrus' main project directory
import sys, os, os.path, platform
def get_path_modules(context='debug',verbosity=0):
    if context == 'debug':
        user_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
        user_folder = os.environ.get(user_var)
        path_modules = '{}/git/citrus/modules'.format(user_folder)
    else:
        raise Exception("get_path_modules: context'{}' not supported'".format(context))

    if verbosity > 1:
        print("Assigned path_modules='{}'".format(path_modules))
    return path_modules

sys.path.append(get_path_modules())
# the etl.py module resides under get_path_modules()
import etl
'''

'''
Method remove_readonly() is for windows -- may need to also detect platform and avoid using it
on non-windows OSes

See the rmtree code example at: https://docs.python.org/3/library/shutil.html#shutil.rmtree
'''
def remove_readonly(func, path, _):
    "Clear the readonly bit and reattemt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remake_dir(folder):
    # REMOVE the xml output directory if extant and then recreate it.
    os.makedirs(folder, exist_ok=True)
    shutil.rmtree(folder)
    # Get error on next line if do not set exist_ok to True?
    # Seems inscrutable, but let it be.
    os.makedirs(folder, exist_ok=True)

def utc_now():
    return datetime.datetime.utcnow()

def utc_now_secs():
     now = utc_now = datetime.datetime.utcnow()
     now_secs_str = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")
     return now, now_secs_str


'''
Get an api result for a url decoded as utf-8.
If json_loads is True, read the API result as a JSON result,
so decode it to a Python result and return that.
Otherwise just return the utf-8 result.
'''
def get_result_by_url(url=None, json_loads=True, send_user_agent=True, verbosity=0):
    import urllib, json
    me = 'get_result_by_url'
    if url is None or url=="":
        raise Exception("Cannot send a request to an empty url.")
    try:
        if verbosity > 0:
            print("*** BULDING GET REQUEST FOR API RESULTS FOR URL='{}' ***"
              .format(url))
        if (send_user_agent):
            get_request = urllib.request.Request(url, data=None, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                })
        else:
            get_request = urllib.request.Request(url, data=None)

    except Exception as exc:
        raise Exception("Cannot create a request for \nurl='{}', exc={}".format(url,repr(exc)))
    try:
        print("{}:*** GET REQUEST='{}' ***".format(me,repr(get_request)))
        response = urllib.request.urlopen(get_request)
    except Exception as e:
        if verbosity > 0:
            print("{}:get_result_by_url: Got exception instead of response for"
                " \nurl='{}',\nget_request={} , exception={}"
                .format(me,url, repr(get_request), e))
        raise
    result = response.read().decode('utf-8')
    if json_loads == True:
        result = json.loads(result)
    return result

'''
Somewhat better name ... same functionality to replace more poorly named method data_folder()
'''
def platform_output_folder(
       linux_base_folder=None
       ,windows_base_folder=None
       , output_subfolder=None, exist_ok=True, verbosity=0 ):
    rparams = ['linux_base_folder','windows_base_folder']
    if not all(rparams):
        raise ValueError('All required params({}) were not given'.format(rparams))
    if platform.system().lower() == 'linux':
        folder = linux + data_relative_folder
    else:
        folder = windows + data_relative_folder
    os.makedirs(folder, exist_ok=exist_ok)
    return folder

def data_folder(linux='/tmp/data/', windows='c:/data/',
    data_relative_folder='', exist_ok=True, verbosity=0):
    if platform.system().lower() == 'linux':
        folder = linux + data_relative_folder
    else:
        folder = windows + data_relative_folder
    os.makedirs(folder, exist_ok=exist_ok)
    return folder

def user_folder_name():
    user_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
    user_folder = os.environ.get(user_var)
    return user_folder

def home_folder_name():
    from os.path import expanduser
    print("*** home_folder_name() is DEPRECATED ***: Use method user_folder_name instead")
    return expanduser("~")

def make_home_relative_folder(home_relative_folder='',exist_ok=True, verbosity=0):
    raise("*** make_home_relative_folder() is DEPRECATED ***: Use method data_folder() instead")
    if home_relative_folder.startswith('/'):
        home_relative_folder.replace('/','')
    folder = home_folder_name() + "/" + home_relative_folder
    if verbosity > 0:
        print("Making folder {}".format(folder))
    os.makedirs(folder, exist_ok=exist_ok)
    return folder

''' Generic utility excape_xml_text:
Given a str, replace embedded 'special xml characters' with their xml quotable formats.
Also replace tabs with space for easier conversion of multiple fields later
to tab-separated values.
'''
def escape_xml_text(str):
    str = str.replace("<", "&lt;")
    str = str.replace(">", "&gt;")
    str = str.replace("&", "&amp;")
    str = str.replace("\"", "&quot;")
    str = str.replace("\t", " ")
    return str
'''
Method html_escape(str)

Replace text xml characters in given 'str' with their 'xml quotable' formats.
Also replace tabs with space for easier conversion of multiple fields later
to tab-separated values.

Return the altered str
'''
def html_escape(text):
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        "\t": " ", # extra:replace tabs to create tab-delimited outputs when needed
    }
    #text = str(text.encode('ascii', 'xmlcharrefreplace'))
    text_out = ""
    for c in text:
        text_out += str(html_escape_table.get(c,c) )
    #text_out = text_out.encode('utf-8', 'xmlcharrefreplace')
    return text_out

class FilePaths():
    def __init__(self, input_folders=None, input_path_glob=None ):
        if (input_folders is None or input_path_glob is None):
            raise Exception(ValueError, )
        if (input_folders is not None and input_path_glob is not None):
            # compose input_path_list over multiple input_folders
            input_path_list = []
            for input_folder in input_folders:
                print("FiePaths(): Gathering files in input_folder='{}' that match {}\n"
                .format(input_folder, input_path_glob))
                input_path_list.extend(list(Path(input_folder).glob(input_path_glob)))
            self.paths = input_path_list
            print('FilePaths: found {} file paths matching {}'.format(len(self.paths), input_path_glob))
        self.file_index = 0
        return
#end class FilePaths


'''Method add_subelements():
Generic logging utility helper:

Given an lxml element, add subelements recursively from nested python data structures
This may be used to generate xml log files, however, it can take up too much core if used to
report per-input-file messages, and if so, it may be
better to disable for 'big' batches of xml files to convert, or break up to create multiple log files.
'''
def add_subelements(element, subelements, item_ids=False):
    if isinstance(subelements, dict):
        d_subelements = OrderedDict(sorted(subelements.items()))
        for key, value in d_subelements.items():
            # Check for valid xml tag name:
            # http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
            # poor man's check: just prefix with Z if first character is a digit..
            # the only bad type of tagname found ... so far ...
            if key[0] >= '0' and key[0] <= '9':
                key = 'Z' + key
            try:
                subelement = etree.SubElement(element, key)
            except Exception as e:
                print("Skipping etree.SubElement error='{}' for key='{}'"
                     .format(e,key))
                continue
            add_subelements(subelement, value, item_ids=item_ids)
    elif isinstance(subelements, list):
        # Make a dict indexed by item index/count for each value in the 'value' that is a list
        for i, value in enumerate(subelements):
            id_filled = str(i+1).zfill(8)
            if item_ids:
                subelement = etree.Element("item")
                subelement.attrib['id'] = id_filled
                element.append(subelement)
            else:
                #encode the ID as a suffix to to element tag name itself
                subelement = etree.SubElement(element, 'item-{}'.format(id_filled))

            add_subelements(subelement, value, item_ids=item_ids)
    else: # Assume it is a string-like value. Just set the element.text and do not recurse.
        element.text = str(subelements)
    return True
# end def add_subelements()
'''
 From given dictionary, return a list of lxml tree elements, one per dictionary item.
 Arguments are: A root lxml element, and a dictionary where each item represents a sub-element.
 Add a sub-element for each item using the item key as the sub-element name.
 If the item value is a dictionary, then do a recursive call using the new sub_element as d_root and
 the item value as the d_elts parameter.
'''
def add_subelements_from_dict(element, d_subelements):
    # Use an OrderedDct that is sorted by key for easier human-reading
    # First argument must be an lxml element
    # second argument must be a dictionary with
    #  (1) keys being legal XML tag names (not checked here),
    #  but note that they should begin with an alphabetic character, not a digit nor special character.
    # and (2) values being either
    # (a) a string or
    # (b) another dictionary of key values pairs, or
    # (c) a list of dicts with key-value pairs
    d_subelements = OrderedDict(sorted(d_subelements.items()) )
    for key, value in d_subelements.items():
        #For given element, create a new sub-element from this key
        # Check for valid xml tag name: http://stackoverflow.com/questions/2519845/how-to-check-if-string-is-a-valid-xml-element-name
        # poor man's check: just prefix with Z if first character is a digit.. the only bad type of tagname found so far...
        if key[0] >= '0' and key[0] <= '9':
            key = 'Z' + key
        subelement = etree.SubElement(element, key)

        if isinstance(value, dict):
            # Add  value-dict's subelements to this element
            add_subelements_from_dict(subelement, value)
        elif isinstance(value, list):
            #Use the key value as a parent element and the list index(plus 1) as a count attribute
            for i,value2 in enumerate(value):
                subelement2 = etree.SubElement(subelement, 'item')
                subelement2.attrib['count'] = str(i+1)
                add_subelements_from_dict(subelement2, value2)
        else:
            # Assume the value is a string for this element's text value
            subelement.text = str(value)
# end add_subelements_from_dict

def has_digit(inputString):
    return bool(re.search(r'\d', inputString))
def has_upper(inputString):
    return any(i.isupper() for i in inputString)
''' See https://www.loc.gov/standards/iso639-2/php/code_list.php
Add more later...as needed. Just some basic ones here to start..
value should be a iso639-2b language code.
Key can be anything (codes mostly) in source data that might represent a spoken language
'''
d_language_639_2b = {
    'ang':'ang',
    'ara':'ara',
    'ar': 'ara',
    'chi':'chi',
    'cpe':'cpe',
    'cpf':'cpf',
    'cs': 'cze',
    'cze':'cze',
    'da': 'dan',
    'dan':'dan',
    'de':'ger',
    'dut':'dut',
    'en' : 'eng',
    'eng': 'eng',
    'es' : 'spa',
    'fr' : 'fra',
    'fra' : 'fra',
    'fro' : 'fro',
    'ga':'gle',
    'gle':'gle',
    'el':'gre',
    'fa':'per',
    'ger':'ger',
    'ht':'hai',
    'hai':'hai',
    'he':'heb',
    'heb':'heb',
    'hat':'hat',
    'hi':'hin',
    'hin':'hin',
    'ht':'hat',
    'is':'ice',
    'ice':'ice',
    'it':'ita',
    'ita':'ita',
    'ja':'jpn',
    'jpn':'jpn',
    'ko':'kor',
    'kor':'kor',
    'id':'ind',
    'mn':'mon',
    'mon':'mon',
    'ne':'nep',
    'nep':'nep',
    'nl':'dut',
    'no':'nor',
    'nor':'nor',
    'pa':'pan',
    'pan':'pan',
    'per':'per',
    'po':'pol',
    'pol':'pol',
    'pt':'por',
    'por':'por',
    'ro':'rum',
    'ru':'rus',
    'rus':'rus',
    'ru':'rum',
    'rum':'rum',
    'sa':'san',
    'san':'san',
    'spa': 'spa',
    'sv': 'swe',
    'swe': 'swe',
    'th': 'tha',
    'tha': 'tha',
    'tr':'tur',
    'tur':'tur',
    'vi':'vie',
    'vie':'vie',
    'cy':'wel',
    'wel':'wel',
    'yi':'yid',
    'yid':'yid',
    'zh':'chi',
}
d_langcode_langtext = {
    'cpe':'Creoles and pidgins, English-based',
    'cpf':'Creoles and pidgins, French-based',
    'dut':'Dutch',
    'eng':'English',
    'fra':'French',
    'fro':'French, Old (842-ca. 1400)',
    'ger':'German',
    'hat':'Haitian',
    'por':'Portuguese',
    'spa':'Spanish',
}

# TEST
def test():
    days = sequence_days(cymd_start='20170715', cymd_end='20170825')
    for day,dt_day in days:
        print("Got day={}".format(day))

#test()
