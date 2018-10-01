#
from django.contrib import admin

from .models import (
    Bibvid,
    BibvidTerm,
    RelatedTerm,
    TermEval,
    TermSuggestion,
    ThesTree,
    X2018Subject,
    X2018Thesis,

    #Thesaurus,
    )

from django.forms import ModelForm, TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin

'''
TODO: move to common module - used also in other MAW apps
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
# end class MinValidatedInlineMixIn

import csv
from django.http import HttpResponse

#Modeled after snow's admin.py class AttributeInline
class RelatedTermInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = RelatedTerm
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
# end class RelatedTermInline

class BibvidTermInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = BibvidTerm
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
# end class RelatedTermInline

#Modeled after snow's admin.py class AttributeInline
class TermEvalInline0(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = TermEval

#Modeled after snow's admin.py class AttributeInline
class TermEvalInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = TermEval
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
# end class TermEvalInline

# { Admin for model ThesTree
# NB: Must stick to django 2.0.7 or visit to this model
# using django 2.1 fails when
#using django-mptt version 0.91 latest on 20180828
# maybe recheck later. Tradeoff is we need django 2.1 to
# manage 'view' model permissions.. so keep checking.
#
class ThesTreeAdmin(DjangoMpttAdmin):
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
# end class ThesTreeAdmin(DjangoMpttAdmin)
admin.site.register(ThesTree, ThesTreeAdmin)

# } Admin for model ThesTree

class DpsModelAdmin(admin.ModelAdmin):
    # Using value should be a settings.py DATABASES key,
    # actually called a 'connection' name in misc Django messages
    using = 'dps_connection'
    # Smaller text form regions
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'80'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'80'})},
    }

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request,
            using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request,
            using=self.using, **kwargs)
    # end def formfield_for_manytomany
# end class DpsModelAdmin(admin.ModelAdmin)

# { Admin for model Bibvid}
class BibvidAdmin(admin.ModelAdmin):
    inlines = [BibvidTermInline, ]
    pass
#end class BibvidAdmin()

admin.site.register(Bibvid, BibvidAdmin)
# } Admin for model Bibvid}

# { Admin code
class TermSuggestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    inlines = [TermEvalInline, ]
    def get_sortable_by():
        return []
#end class TermSuggestionAdmin

# Thesis and Subject Admin
class X2018ThesisForm(ModelForm):
    model = X2018Thesis

    class Meta:
        model = X2018Thesis
        fields = ['thesis','uf_bibvid','title', 'au_fname', 'au_lname',
          'pub_year', ]
        widgets = {
            'thesis' : TextInput(attrs={'size':8, 'rows':1}),
            'uf_bibvid' : TextInput(attrs={'cols':10, 'rows':1}),
            'title' : Textarea(attrs={'cols':40, 'rows':1}),
            'au_fname' : TextInput(attrs={'size':40, 'rows':1}),
            'au_lname' : TextInput(attrs={'size':40, 'rows':1}),
            'pub_year' : TextInput(attrs={'size':10, 'rows':1}),
            'add_initials' : TextInput(attrs={'size':4, 'rows':1}),
            'add_ymd' : TextInput(attrs={'size':10, 'rows':1}),
            'change_initials' : TextInput(attrs={'size':4, 'rows':1}),
            'change_ymd' : TextInput(attrs={'size':10, 'rows':1}),

        }
#end class X2018ThesisForm

class X2018SubjectForm(ModelForm):
    model = X2018Subject

    class Meta:
        model = X2018Subject
        fields = ['thesis', 'subject', 'term', 'keep',
          'marc', 'ind1', 'ind2' ]
        widgets = {
            'sn' : TextInput(attrs={'cols':10, 'rows':1}),
            'thesis' : TextInput(attrs={'size':8, 'rows':1}),
            'subject' : TextInput(attrs={'size':4, 'rows':1}),
            'term' : TextInput(attrs={'size':40, 'rows':1}),
            'keep' : TextInput(attrs={'size':1, 'rows':1}),
            'marc' : TextInput(attrs={'size':3, 'rows':1}),
            'ind1' : TextInput(attrs={'size':1, 'rows':1}),
            'ind2' : TextInput(attrs={'size':1, 'rows':1}),
        }
#end class X2018SubjectForm

class SubjectInline(admin.TabularInline):
    model = X2018Subject
    show_change_link = True
    extra = 0
    fields = ('xtag','term','keep','marc',
        'ind1', 'ind2')


class ThesisAdmin(admin.ModelAdmin):
    form = X2018ThesisForm

    search_fields =['uf_bibvid','thesis', 'title','au_fname','au_lname']
    list_display = ['thesis','uf_bibvid','title', 'au_fname', 'au_lname',
        ]
    list_display_links = list_display[0:3]
    inlines = [SubjectInline]

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'40'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
#end class ThesisAdmin
class SubjectAdmin(admin.ModelAdmin):

    form = X2018SubjectForm
    search_fields =['term']
    list_filter = ['xtag', 'keep', 'marc']
    list_display = ['thesis','subject','xtag', 'term', 'keep',
        'marc','ind1', 'ind2']
    list_display_links = list_display[0:3]
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'40'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
#end class SubjectAdmin

admin.site.register(TermSuggestion, TermSuggestionAdmin)
admin.site.register(X2018Thesis, ThesisAdmin)
admin.site.register(X2018Subject, SubjectAdmin)
# } Admin code
