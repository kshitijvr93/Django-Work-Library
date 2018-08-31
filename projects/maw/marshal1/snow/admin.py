from django.contrib import admin
from django.contrib import admin
from .models import (
  Attribute,
  BatchSet,
  Batch,
  Field, Lookup, Match,
  Node, # display name is Element
  Regex, Relation,
  Role,
  Schema, Vocabulary, Word,
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
import sys

#Note: use nested_admin OR nested_inline

from nested_inline.admin import NestedStackedInline, NestedModelAdmin

from django_mptt_admin.admin import DjangoMpttAdmin

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


class AttributeInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = Attribute
    # A node may only contain only child nodes, and it is possible for
    # a node to have no attributes, so we set min_num = 0
    min_num = 0
    #classes = ['collapse','collapsed']
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }

    def get_filters(self, obj):
        return((''))


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

class BatchInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = Batch
    # It is possible to have 0 fields if the relation only contains
    # sub-relations
    min_num = 0
    #classes = ['collapse','collapsed']
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.

    def get_filters(self, obj):
        return((''))
# end class BatchInline


class BatchSetAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    inlines = [BatchInline, ]
#end class BatchSetAdmin

class RelationInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):

    model = Relation
    classes = ['collapse']
    min_num = 0
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }

    def get_filters(self, obj):
        return((''))
    # disble green plus on this admin form
    def has_add_permission(self, obj):
        return False

class SnowNestedModelAdmin(NestedModelAdmin):
    using = 'snow_connection'

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
class SnowModelAdmin(admin.ModelAdmin):
    using = 'snow_connection'

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'40'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }

class SchemaAdmin(
    #SnowNestedModelAdmin,
    SnowModelAdmin,
    ExportCvsMixin):
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
    # Just do NOT do RelationInline -- no easy way to disable the
    # green 'plus' near the parent field, and allowing it
    # there is too confusing for the user
    #inlines = [RelationInline, ]

# end class

# NB: Must stick to django 2.0.7 or visit to this model
# using django 2.1 failsnwhen
#using django-mptt version 0.91 latest on 20180828
# maybe recheck later. Tradeoff is we need django 2.1 to
# manage 'view' model permissions.. so keep checking.
class NodeAdmin(DjangoMpttAdmin):
    # stab in the dark... to provide sortable_by value...
    # https://github.com/django-mptt/django-mptt/search?q=sortable_by&unscoped_q=sortable_by
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    inlines = [AttributeInline, ]

    def get_sortable_by():
        return []
#end class NodeAdmin

class RoleAdmin(DjangoMpttAdmin):
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    def get_sortable_by():
        return []

    #sortable_by = super.list_display

#end class RoleAdmin

class BatchAdmin(admin.ModelAdmin):
    list_filter = ['name','received_imported_items', 'creator_role',
      'batch_set', 'create_datetime']
    list_display = list_filter
    search_fields = ['name', 'creator_role', 'batch_set']
    readonly_fields = ['item_count','create_datetime','received_imported_items']
    #ordering = ['batch_set','creator_role', 'received_imported_items',
    #  'name']
# end class BatchAdmin


class WordAdmin(admin.ModelAdmin):
    list_display = ['word','vocabulary']
    list_filter = ['vocabulary']
    search_fields = ['word','vocabulary']
    ordering = ['word']
# end class WordAdmin


class RelationAdmin( SnowModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]
    list_filter = ['schema']
    list_display = [
        'schema', 'parent', 'name', 'notes',
    ]
    search_fields = list_display
    fields = list_display + ['min_occurs','max_occurs']
    #INLINES
    inlines = [FieldInline, ]
# end class RelationAdmin


# { may drop these... in favor of element and attribute
# admin.site.register(Schema, SchemaAdmin)
# admin.site.register(Relation, RelationAdmin)
# admin.site.register(Field, admin.ModelAdmin )
# }

#admin.site.register(Batch, BatchAdmin)
admin.site.register(BatchSet, BatchSetAdmin)
admin.site.register(Lookup, admin.ModelAdmin )
admin.site.register(Match, admin.ModelAdmin )

# Verbose name for Node in Admin is Element
admin.site.register(Node, NodeAdmin)

admin.site.register(Regex, admin.ModelAdmin)
admin.site.register(Role, RoleAdmin)

admin.site.register(Vocabulary, admin.ModelAdmin)
admin.site.register(Word, WordAdmin)
