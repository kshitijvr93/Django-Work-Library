# Create your views here.
from django.conf import settings
import maw_settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Bibvid, X2018Thesis, X2018Subject

########################### IMPORT
# NB; WARNING - canNOT use parens to make an import multiline in python
# yet. Must use bakslash.
from sqlalchemy_tools.core.import_selected_spreadsheet_to_table \
  import spreadsheet_to_table

#from sqlalchemy_tools.core import spreadsheet_to_table
from collections import OrderedDict
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )

'''
Method out_mets(request):

Read the contents of X2018Thesis and input the rows, each representing a uf
bibvid item, with some basic uf_bibivid info
and AI-supplied info exported from a XIS export of UF Electronic Theses and
Dissertatino (ETD) items that were
exported by Xiaoli Ma circa August 2018).

For each,
(1) retrieve and store in core the subjects data from table X2018Subject
    where 'keep' == 'y'.
(2) read the associated METS file in ufdc resources, parse with lxml and store
    the doc tree in local core.
    (a) If option reset_subjects = True, delete all current lxml nodes for subjects
    (b) insert all 'keep' subjects
(3) Generate a new output mets file for the item in an  output folder
    given by a django setting.py (which in turn is defined in the local
    maw_settings.py file on the instance of the Django MAW webserver):

'''

def mets_folder_by_bibvid(bibvid=None, verbosity= 0):
    pass
#end def

def out_mets(request):

    out_html = '<ol>'
    max_bibvids = 5
    od_bibvid = OrderedDict()
    # Retrieve the bibvid items from table Thesis.
    # Report and Skip any duplicate items.
    n_thesis = 0
    for thesis in X2018Thesis.objects.all():
    #for thesis in Bibvid.objects.all():
        n_thesis += 1
        out_html += f"<li>{thesis.uf_bibvid}</li><ol>"
        # Get the subjects
        n_subject = 0
        for subject in X2018Subject.objects.filter(thesis=thesis, keep='y'):
            n_subject += 1
            out_html += f"<li>{subject.term}</li>"
            pass
        out_html += '</ol>'

        if n_thesis > max_bibvids:
            break;


    out_html += f"</ol><p>Found {n_thesis} bibvids</p>"
    print(out_html)
    return HttpResponse(out_html)

# end def out_metsi




    pass
#end def  out_mets
