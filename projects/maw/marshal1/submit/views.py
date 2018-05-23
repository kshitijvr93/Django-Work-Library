# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .models import Item

def detail (request, item_id):
    item = get_object_or_404(Item, pk=item_id)

@login_required
def home(request):
    return render(request, 'cuba_libro/cuba_libro_home.html')


########################### IMPORT
from sqlalchemy_tools.core.import_selected_spreadsheet_to_table import spreadsheet_to_table
from collections import OrderedDict
from sqlalchemy import (
  Boolean, create_engine,
  CheckConstraint, Column, Date, DateTime,Float, FLOAT, ForeignKeyConstraint,
  inspect, Integer,
  MetaData, Sequence, String, Table, Text, UniqueConstraint,
  )
def import20180503(request):
    import io
    log_output = io.StringIO()

    od_index_column = OrderedDict({
          # skip 'a' - moved to queue...
          'a': Column('holding',String(20)),
          'b': Column('reference_type',String(20)),
          'c': Column('authors_primary', Text),
          'd': Column('title_primary', Text),
          'e': Column('periodical_full', Text),
          'f': Column('periodical_abbrev', Text),
          'g': Column('pub_year_span',String(50)),
          'h': Column('pub_date_free_from', Text),
          'i': Column('volume', String(30)),
          'j': Column('issue', String(30)),
          'k': Column('start_page', String(30)),
          'l': Column('other_pages', String(30)),
          'm': Column('keywords', Text),
          'n': Column('abstract', Text),
          'o': Column('notes', Text),
          'p': Column('personal_notes', Text),
          'q': Column('authors_secondary', Text),
          'r': Column('title_secondary', Text),
          's': Column('edition', String(80)),
          't': Column('publisher', String(255)),
          'u': Column('place_of_publication', String(255)),
          'v': Column('authors_tertiary', Text),
          'w': Column('authors_quaternary', Text),
          'x': Column('authors_quinary', Text),
          'y': Column('title_tertiary', Text),
          'z': Column('isbn_issn', String(255)),
          'aa' : Column('availability', Text),
          'ab': Column('author_address', Text),
          'ac': Column('accession_number', Text),
          'ad': Column('language', Text),
          'ae': Column('classification', Text),
          'af': Column('sub_file_database', Text),
          'ag': Column('original_foreign_title', Text),
          'ah': Column('links', Text),
          'ai': Column('url', Text),
          'aj': Column('doi', Text),
          'ak': Column('pmid', Text),
          'al': Column('pmcid', Text),
          'am': Column('call_number', Text),
          'an': Column('database', Text),
          'ao': Column('data_source', Text),
          'ap': Column('identifying_phrase', Text),
          'aq': Column('retrieved_date', Text),
          'ar': Column('shortened_title', Text),
          'as': Column('user_1', Text),
         })

    # This is the db with the table to put the data.
    engine_nickname = 'uf_local_mysql_maw1_db'
    table_name = 'cuba_libro_item'

    # This is the workbook to import from
    workbook_path = ('C:\\rvp\\downloads\\'
          'cuba_libro_item_20180503.xlsx')

    # Sheet index values start at 0.
    # Worksheets indexes for those we want to use to import table data
    l_sheet_index = [0,1,2,4,5,6]
    #l_sheet_index = [0

    #All 7 sheets here have column name strings in row count 1, so skip,
    #because od_index_column is used as a map below instead
    row_count_values_start = 2
    is_index_xls = True

    # Import the rows from each spreadsheet of interest:
    log_contents = ''
    for sheet_index in l_sheet_index:
        spreadsheet_to_table(
          # Identify the workbook pathname of the input workbook
          input_workbook_path=workbook_path,
          sheet_index=sheet_index,
          # Map the input workbook first spreadsheet's row's column
          # indices to the output table's sqlalchemy columns
          od_index_column=od_index_column,
          column_index_offset=0,
          row_count_values_start=row_count_values_start,
          is_index_xls=is_index_xls,

          engine_nickname=engine_nickname,
          table_name=table_name,
          create_table=False,

          log_output=log_output,
          #Set the desired output engine/table_name
          verbosity=1,
          )
        log_contents += log_output.getvalue()

    #end for sheet_index in l_sheet_index

    html='''
    <h3>Importing 20180503 data...</h3>
    {}
    <p>Import is finished.</p>
    '''.format(log_contents)

    return (HttpResponse(html))

def index(request):

    msg = ("UFDC Cuba Libro Project Index:")

    #admin_href = "localhost:8000/admin/hathitrust"
    #msg += "</br><a href='{}''>Hathitrust Administration</a>".format(admin_href)
    context = {
        'msg' : msg,
    }
    #return HttpResponse(template.render(context, request))
    return render(request, "cuba_libro/index.html", context)
