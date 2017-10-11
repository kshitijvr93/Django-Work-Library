'''
make_draft.py
make the draft
'''
import sys, os, os.path, platform
def get_path_modules(verbosity=0):
  env_var = 'HOME' if platform.system().lower() == 'linux' else 'USERPROFILE'
  path_user = os.environ.get(env_var)
  path_modules = '{}/git/citrus/modules'.format(path_user)
  if verbosity > 1:
    print("Assigned path_modules='{}'".format(path_modules))
  return path_modules
sys.path.append(get_path_modules())
print("Sys.path={}".format(sys.path))
sys.stdout.flush()
import etl

print("Using python sys.version={}".format(sys.version))
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
print("sys.path={}".format(repr(sys.path)))
import datetime
import pytz
import os
import sys
from collections import OrderedDict

from pathlib import Path
import hashlib

from lxml import etree
from lxml.etree import tostring
from pathlib import Path
import etl

#Append to result_doc.html
def make_draft():

    doc_template = ''
    #Append cover_sheet to result_doc
    out_filename = 'SOP_MAW.html'

    with open(out_filename,mode='w', encoding='utf-8') as out_file:
        # Append cover sheet to result_doc
        with open(in_filename,mode='r', "part01_cover_sheet/cover_sheet.html") as in_file:
            for line in in_file:
                out_file.write(line)

        # Follow the template file for  the remainder of the document
        with open(in_filename, mode='r', "part02_main/template.html") as in_file:
            doc_remainder = ''
            for line in in_file:
                doc_template += line
        # got template
        # quick 'cheat', use knowledge of template vars and fill the
        # values first (could have parsed the template instead)
        var_names = ['project_description'
        ,'project_significance'
        ,'innovative_components'
        ,'similar_projects'
        ,'resources_plan_sustainability'
        ,'activity_timeline'
        ,'collections_benefitted'
        ,'metrics_permissions'
        ,'disseminate_share'
        ,'budget_narrative'
        ,'budget_table'
        ,'references_cited'
        ]

        d_var_val = {var: '' for var in var_names}
        # if a filename var.html exists, use it for the value of that var
        for var in var_names:
            val = ''
            with open(open(in_filename, mode='r', {part02_main/{}.html} as in_file):
                val = ''
                for line in in_file:
                    val += line
            d_var_val[var] = val
        # fill the template
        doc_remainder = doc_template.format(**d_var_val)
        #write the rest of the output file
        out_file.write(doc_remainder)
    #end output
    print("Wrote document fo file {}. Done!".format(out_filename))
