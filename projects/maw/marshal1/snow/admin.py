from django.contrib import admin
from django.contrib import admin
from .models import (
  Field, Genre, Lookup,
  Regex, Relation, Vocabulary, Word,
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
import sys
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

'''
Nice solution to validate minimum populated inline (foreign key-selected
authors) of 1 for at least 1 primary author author, file inlines, etc.
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
    classes = ['collapse']


class FieldInline(
    MinValidatedInlineMixIn, SnowNestedStackedInline):
    classes = ['collapse']
    xformfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
    model = Field
    min_num = 1
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.
    def get_filters(self, obj):
        return((''))

class RelationInline(
    MinValidatedInlineMixIn, SnowNestedStackedInline):
    model = Relation
    classes = ['collapse']
    min_num = 1
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.
    inlines = [FieldInline]

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


class GenreAdmin(SnowNestedModelAdmin, ExportCvsMixin):
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

    # Next line may not be apt.
    classes = ['collapse']
    #INLINES
    inlines = [RelationInline, ]

# end class

admin.site.register(Genre, GenreAdmin)

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

    readonly_fields = ('create_datetime',)
    list_display = [
        'name',
        'max_length',
        'notes',
    ]
    list_display = list(readonly_fields) + list_display
    search_fields = list_display

    fields = list_display

    #INLINES
    inlines = [RelationInline, ]

# end class


admin.site.register(Lookup, admin.ModelAdmin )
admin.site.register(Regex, admin.ModelAdmin)
admin.site.register(Vocabulary, admin.ModelAdmin)
