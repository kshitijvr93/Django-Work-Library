# maw_utils.py - misc MAW utilities of use across applications
import os
from django.db import models
import datetime
from django.utils import timezone



'''
Nice ExportCvsMixin class presented and covered, on 20180402 by:
https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
'''
import csv
from django.http import HttpResponse

class ExportCvsMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename={}.csv'.format(meta))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow(
                [getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

# end class ExportCvsMixin

#CUSTOM FIELD
'''
class SpaceTextField is a TextField that is modified to:
    (1) change newlines and tabs to spaces

    This facilitates saving models in tab-delimited text files that can
    be imported to Excel with minimum fuss.

    Problems averted:

    (1) Tab is used as the delimiter on output by the ExportTsvMixin class,
    and each occurrence of a tab will be replaced by a space character,
    so tabs  will not appear in the text data.
    Otherwise a tab in the data would make the output of the ExportTsvMixin
    un-importable to Excel

    (2) Newlines and returns will be replaced by a space character, which
    otherwise would make the ExportTsvMixin output unimportable to Excel.

    Even if the user or some other application modifies the correlated
    database field to include a tab, return, or newline, this will also replace
    it before appearing in the ExportTsvMixin's output file or in the
    SpaceTextField.

    A help_text may be apt to warn a user populating the field that any tab,
    newline, or return character will always be replaced by a space.

    A similar method may be used for SpaceCharField

'''
class SpaceTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate(self,value):
        v=(value.replace('\r','').replace('\n',' ').replace('\t',' ') )
        return v

    def from_db_value(self,value,expression,connection):
        if value is None:
            return value
        return(self.translate(value))

    def to_python(self, value):
        if value is None:
            return value;
        return(self.translate(value))


class SpaceCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate(self,value):
        if value is None:
            return ''
        else:
            v = value.replace('\r','').replace('\n',' ').replace('\t',' ')
        #return "pumpernickel"
        return v

    def from_db_value(self,value,expression,connection):
        if value is None:
            return value
        return(self.translate(value))

    def to_python(self, value):
        if value is None:
            #return value
            return value
        return value
#end class SpaceCharField

'''
field for "Plus" integers. So starting at 1, not 0.
'''
class PositiveIntegerField(models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate(self,value):
        # Disallow 0.
        # Just set 0 to 1 without generating an Exception.
        if value < 1:
            value = 1
        return value

    def from_db_value(self,value,expression,connection):
        if value is None:
            return value
        return(self.translate(value))

    def to_python(self, value):
        if value is None:
            return value;
        return(self.translate(value))
