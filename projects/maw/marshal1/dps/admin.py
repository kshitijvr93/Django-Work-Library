#
from django.contrib import admin

#import_export docs: https://django-import-export.readthedocs.io/en/latest/
from import_export import resources
from import_export import fields
from import_export.admin import ImportExportModelAdmin
import sys

from .models import (
    BatchItem,
    BatchSet,
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

from django.forms import ModelForm, TextInput, Textarea, BaseInlineFormSet
from django.db import models

from maw_utils import ExportCvsMixin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin

import csv
from django.http import HttpResponse
import uuid

def get_candidate_by_candidates_matches(
    l_candidates=None, l_matches=None,verbosity=0):
    '''
    Given a list of candidate strings and 'match' strings:
    For each candidate string, convert it to lower case and seek the
    first match among the match strings.
    If no match is found, return None.
    If a match is found, return the original candidate string (before
    lower-casing)
    NOTE: it is caller's responsibilty to ensure that all strings in l_match
    are already lower-cased.

    This is used to find the best candidate import file field name that
    should be used to extract an expected database value.
    '''
    for cand in l_candidates:
        if cand.lower() in l_matches:
            return cand
    return None

class BatchItemResource(resources.ModelResource):
    def __init__(self):
        '''
        '''
        # user and import_filename are set in before_import()
        self.my_id = 0
        self.row_count = 0
        self.user = None
        self.import_filename = None
        self.import_username = None

        # bibid_import_field and vid_import_field are set in the first call to
        # before_import_row()
        self.bibid_import_field = None
        self.vid_import_field = None
        self.bibid_import_field = None
        self.vid_import_field = None

        # List of potential import file  fieldnames
        self.d_dbcol_matches = {
            'bibvid': [ 'bibvid', 'bib_vid', 'uf_bibvid',
            'uf_bib_vid',
            ],
            'bibid': [ 'bib','bibid', 'bib_id', 'bibliographic_id',
            'bibliographicid', 'uf_bib',
            ],

            'vid': [ 'vid','vol_id','volid','volume_id','volumeid',
            ]
        }

        super().__init__()
    # end __init__


    def before_import(self,dataset, using_transactions, dry_run, **kwargs):
        '''
        Consider: Here, create a new row in BatchSet with just the
        current datetime - (maybe a filename from this dataset too and the
        request user, if avalable ?)
        Use the created BatchSet id as a field here.
        Also, from another table, or maybe a method to create on model
        BatchItem, get the max BatchItem id and set it heree, instead of
        using 0.
        '''
        self.batch_set = BatchSet()

        user = kwargs['user']
        self.batch_set.import_username = user.username
        self.import_filename = kwargs['file_name']
        self.batch_set.import_filename = kwargs['file_name']

        #print(
        #  f"username={self.user.get_username()}, file_name={self.file_name}")
        # Consider: set self.db_ss{} dict with key bibid to the name of one of
        # the ss columns,
        # and set dict with key vid to one of the ss columns or None

        # temp setups for testing a import file  with column BibID and no vid column
        print(f"kwargs='{kwargs}',headers={dataset.headers}")
        sys.stdout.flush()
    # end def before_import()

    def before_import_row(self, row, **kwargs):
        print(f"before_import_row: row='{row}'")
        sys.stdout.flush()
        if self.bibid_import_field is None:
            # This is the first call to get a import file  row, and the first
            # access to the 'row' object during an import.
            # Now seek matches in import file  column names for db columns
            # First, seek ss field to use for 'bibid' db column
            self.import_bibfield = get_candidate_by_candidates_matches(
                l_candidates = row.keys(),
                l_matches = self.d_dbcol_matches['bibid'] )

            if self.import_bibfield is None:
               # todo? Add a nicer error message or error handling.
                msg = (f"Could not find a bibfield in this import file")
                raise ValueError(msg)
            self.batch_set.bibid_field = self.import_bibfield

            self.import_vidfield = get_candidate_by_candidates_matches(
                l_candidates = row.keys(),
                l_matches = self.d_dbcol_matches['vid'])
            self.batch_set.vid_field = self.import_vidfield
            # Save this now to define the primary key batch_set.id for use
            # below as a'batch_set'  foreignkey value for batchItems
            self.batch_set.save()
        # end if bibidimprt field is None (First import row)

        self.my_id += 1
        self.row_count += 1

        # Row key-values are stored as column values in aBatchItem
        # These row keys must also appear in Meta.fields list
        my_uuid = uuid.uuid4()
        row['uuid'] = my_uuid
        # Quirky bug of django import-export, must set id in row
        # though not in the table BatchItem
        row['batch_set'] = self.batch_set.id
        row['row_count'] = self.row_count

        row['bibid'] = row[self.import_bibfield]

        vid = self.import_vidfield
        row['vid' ] = '00001' if vid is None or len(vid) == 0 else row[vid]
    # end before_import_row()

    def after_import(self, dataset, result, using_transactions,
        dry_run, **kwargs):

        if dry_run == False:
            self.batch_set.item_count = self.row_count
            self.batch_set.save()
    # end def after_import

    class Meta:
        model = BatchItem
        # Note import-export expects id field so must EXCLUDE it here
        # else it complains because BathSet uses uuid, not id
        import_id_fields = ['uuid',]
        exclude = ['id',]
        fields = [ 'uuid', 'batch_set', 'row_count', 'bibid', 'vid',]
        report_skipped = True

# end class BatchItemResource

class BatchSetAdmin(admin.ModelAdmin):
    list_display = ["id", "import_datetime","import_username","name",
      "import_filename", ]
    list_display_links = ["id", "import_datetime","import_username",
      "import_filename"]
    search_fields = ["id", "name", "notes", "import_datetime","import_username",
      "import_filename", ]
    fields = ["id", "name", "notes", "import_datetime", "import_filename",
      "import_username", "bibid_field", "vid_field", "item_count", ]
    readonly_fields = ["id", "import_datetime", "import_username",
      "import_filename", "bibid_field" , "vid_field", "item_count",]

    list_filter = ['import_username','import_datetime','import_filename',]

    class Meta:
        ordering = ['-import_datetime','import_username','import_filename']

#end class BatchSetAdmin
admin.site.register(BatchSet, BatchSetAdmin)

class BatchItemAdmin(ImportExportModelAdmin):
    # note: commenting this has shown no bad effects but leaving
    # uncommented to match some docs
    resource_class = BatchItemResource

    list_display = ['batch_set','row_count','bibid','vid']
    list_display_links = ['row_count','bibid','vid']

    search_fields = ['batch_set__name', 'bibid','vid']
    fields = ['batch_set', 'row_count','bibid','vid']
    readonly_fields = ['batch_set','row_count',]
    ordering = ['-batch_set', 'row_count']


#end class BatchItemAdmin

admin.site.register(BatchItem, BatchItemAdmin)


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
#  `admin.site.register(Bibvid, BibvidAdmin)
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
        fields = ['thesis', 'subject', 'term', 'matches','source','keep',
          'marc', 'ind1', 'ind2' ]
        xwidgets = {
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
    #formset = SubjectFormSet
    show_change_link = True
    extra = 0
    fields = ('xtag','term','keep','matches','source','marc',
        'ind1', 'ind2')
    ordering = [ 'term', '-keep']
    # These can/do control inline form field sizes.
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }

    def has_delete_permission(self, request, obj=None):
        return False

    ''' 20181001 - rvp: just tried this on a lark, and this method is also
    apparently working somewhat for inline fields. The term field has too
    much empty space after it on the form though.
    '''
    def formfield_for_dbfield(self, db_field, **kwargs):
        me = 'SubjectAdmin:formfield_for_dbfield'
        # Set form to upload form to use for adding..  .
        #form_field = super(FileModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        form_field = super().formfield_for_dbfield(db_field, **kwargs)
        #dict of field widget attributes
        dw = form_field.widget.attrs
        fname= db_field.name
        # Dict of TextInput fields needing overrides
        d_input_size = {
          'term': 40, 'xtag': 8, 'keep':1, 'source':12,
          'ind1':1, 'ind2':1, 'marc':3, }

        if fname in d_input_size or fname == 'term':
            size = d_input_size[fname]
            dw['size'] = str(size)
            dw['class'] = 'special'
        else:
            pass

        return form_field
    # end def formfield_for_dbfield

'''
Review later: attempt to support different field sizes within the
subject inlne form so 'keep' has size 1, term has size 40, etc custom
sizes per each field, marc has 3, etc.
from django.forms import inlineformset_factory
See also: https://docs.djangoproject.com/en/2.0/topics/forms/modelforms/#specifying-widgets-to-use-in-the-form-with-widgets
Also: https://stackoverflow.com/questions/9945844/django-change-a-fields-widget-in-subclass-of-baseinlineformset#9946248

'''

#class CustomInlineFormSet(BaseInlineFormSet):
#    pass

#SubjectInlineFormSet=inlineformset_factory(X2018Thesis, X2018Subject,
# fields=['keep'])

'''
NOTE: django 2.0 docs say import BaseInlineFormset from models, incorrect,
but 2.1 docs say import form forms, which is correct (done above).
'''
class SubjectFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        #super (ReferenceForm, self).add_fields(form,index)
        form.fields['keep'] = forms.charField(
            widgets=forms.TextInput(attrs={'size':30, 'rows':1})
        )

    class Meta:
        xwidgets = {
            'subject' : TextInput(attrs={'size':4, 'rows':1}),
            'term' : TextInput(attrs={'size':40, 'rows':1}),
            'keep' : TextInput(attrs={'size':1, 'rows':1}),
            'marc' : TextInput(attrs={'size':3, 'rows':1}),
            'ind1' : TextInput(attrs={'size':1, 'rows':1}),
            'ind2' : TextInput(attrs={'size':1, 'rows':1}),
        }

class ThesisAdmin(admin.ModelAdmin):
    form = X2018ThesisForm
    search_fields =['uf_bibvid','thesis', 'title','au_fname','au_lname']
    list_display = ['thesis','uf_bibvid','title', 'au_fname', 'au_lname',
        ]
    list_display_links = list_display[0:3]
    inlines = [SubjectInline]

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
    ordering = ['thesis']
#end class ThesisAdmin


class SubjectAdmin(admin.ModelAdmin):
    form = X2018SubjectForm
    search_fields =['term','thesis__uf_bibvid']
    list_filter = ['xtag', 'keep', 'marc']
    list_display = ['thesis','subject','xtag', 'term', 'keep',
        'matches','source', 'marc','ind1', 'ind2']
    list_display_links = list_display[0:3]

    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'40'})},
    }
    ordering = ['thesis','xtag','subject']

    def formfield_for_dbfield(self, db_field, **kwargs):
        me = 'SubjectAdmin:formfield_for_dbfield'
        # Set form to upload form to use for adding..  .
        #form_field = super(FileModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        form_field = super().formfield_for_dbfield(db_field, **kwargs)
        #dict of field widget attributes
        dw = form_field.widget.attrs
        fname= db_field.name

        # Dict of TextInput fields needing overrides
        d_input_size = {
          # 'term': 20, changed to SpaceTextField due to long inputs
          'xtag': 8,
          'source': 12,
          'keep':1,
          'ind1':1,
          'ind2':1,
          'marc':3,
          #'thesis':20,
          #'subject':20,
          }

        msg = f"{me}: field name is {fname}"
        print(msg, file=sys.stdout)
        if fname in d_input_size:
            size = d_input_size[fname]
            dw['size'] = str(size)
            dw['class'] = 'special'
        else:
            pass

        return form_field
    # end def formfield_for_dbfield
     #Note: if this is needed also for TextAreas or another field type, adjust
     #the pattarn used above for TextInput type fields
# end class SubjectAdmin

#admin.site.register(TermSuggestion, TermSuggestionAdmin)
admin.site.register(X2018Thesis, ThesisAdmin)
# Maybe retire this SubjectAdmin permanently, as the Thesis inlines work OK.
admin.site.register(X2018Subject, SubjectAdmin)
# } Admin code
