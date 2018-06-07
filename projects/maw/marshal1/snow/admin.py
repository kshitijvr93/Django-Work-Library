from django.contrib import admin
from django.contrib import admin
from .models import (
  Field, Genre,
  Relation, Restriction,
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
import sys
# Register your models here.

class GenreAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    readonly_fields = ('create_datetime',)
    list_display = [
        'name',
        'notes',
    ]
    list_display = list(readonly_fields) + list_display
    search_fields = list_display

    fields = list_display

# end class
admin.site.register(Genre, GenreAdmin)
