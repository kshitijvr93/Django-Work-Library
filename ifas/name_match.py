'''
name_match.py
tools and a main program to compile a file of reference names and to read a
separate set of input files with input names and for each input name,
it outputs the best matching name and a percentage match evaluation metric
between the input and the best match.

Also it scans the reference names and warns if any of those names are 'close'
matches with each other.
'''
import sys, os, os.path, platform
sys.path.append('{}/git/citrus/modules'.format(os.path.expanduser('~')))
from pathlib import Path
from etl import html_escape, has_digit, has_upper, make_home_relative_folder
import xlrd, xlwt
from xlwt import easyxf
from xlrd import open_workbook
