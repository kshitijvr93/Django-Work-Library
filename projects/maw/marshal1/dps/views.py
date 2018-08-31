# Create your views here.
from django.conf import settings
import maw_settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Item

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
