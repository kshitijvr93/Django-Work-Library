from django.contrib import admin
from django.contrib import admin
from .models import (
  Field, Schema, Lookup, Match,
  Regex, Relation, Vocabulary, Word,
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
import sys
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

'''
Nice solution to validate minimum populated inline (foreign
key-selected authors) of 1 for at least 1 primary author author,
file inlines, etc.
See 20180406t0732 answer from Klimenko at:
https://stackoverflow.com/questions/877723/inline-form-validation-in-django
'''
class MinValidatedInlineMixIn:
    validate_min = True
    def get_formset(self, *args, **kwargs):
        return super().get_formset(
            validate_min=self.validate_min, *args, **kwargs)

class SnowNestedStackedInline(NestedStackedInline):

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
    classes = ['collapse','collapsed']


class FieldInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = Field
    # It is possible to have 0 fields if the relation only contains
    # sub-relations
    min_num = 0
    #classes = ['collapse','collapsed']
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.

    def get_filters(self, obj):
        return((''))

class RelationInline(
    MinValidatedInlineMixIn, SnowNestedStackedInline):
    model = Relation
    classes = ['collapse']
    min_num = 0
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.
    #inlines = [FieldInline]

    def get_filters(self, obj):
        return((''))

class SnowNestedModelAdmin(NestedModelAdmin):
    using = 'snow_connection'

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }

class SchemaAdmin(SnowNestedModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    readonly_fields = ('create_datetime',)
    list_display = [
        'name',
        'notes',
    ]
    list_display = list_display + list(readonly_fields)
    search_fields = list_display

    fields = list_display

    #INLINES
    inlines = [RelationInline, ]

# end class

admin.site.register(Schema, SchemaAdmin)

class WordAdmin(admin.ModelAdmin):
    list_display = ['word','vocabulary']
    list_filter = ['vocabulary']
    search_fields = ['word','vocabulary']
    ordering = ['word']

admin.site.register(Word, WordAdmin)

class RelationAdmin(SnowNestedModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]
    list_filter = ['schema']

    list_display = [
        'schema',
        'name',
        'parent',
        'local_name',
        'min_occurs',
        'max_occurs',
        'notes',
    ]
    search_fields = list_display
    fields = list_display

    #INLINES
    inlines = [FieldInline, ]
# end class

admin.site.register(Relation, RelationAdmin)
admin.site.register(Field, admin.ModelAdmin )
admin.site.register(Lookup, admin.ModelAdmin )
admin.site.register(Match, admin.ModelAdmin )
admin.site.register(Regex, admin.ModelAdmin)
admin.site.register(Vocabulary, admin.ModelAdmin)
