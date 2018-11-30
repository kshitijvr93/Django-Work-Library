#

import sys

from django.contrib import admin
from django.db import models
from django.forms import ModelForm, TextInput, Textarea, BaseInlineFormSet

from .models import (
    Aggregation,
    AggTree,
    )

from maw_utils import ExportCvsMixin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin

import csv
from django.http import HttpResponse
import uuid

class AggTreeAdmin(DjangoMpttAdmin):
    mptt_level_indent = 100
    # stab in the dark... to provide sortable_by value...
    # https://github.com/django-mptt/django-mptt/search?q=sortable_by&unscoped_q=sortable_by
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    inlines = [RelatedTermInline, ]
    def get_sortable_by():
        return []
# end class AggTreeAdmin(DjangoMpttAdmin)


#admin.site.register(TermSuggestion, TermSuggestionAdmin)
admin.site.register(Aggregation, Admin.modelAdmin)
# Maybe retire this SubjectAdmin permanently, as the Thesis inlines work OK.
admin.site.register(AggTree, AggTreeAdmin)
# } Admin code
