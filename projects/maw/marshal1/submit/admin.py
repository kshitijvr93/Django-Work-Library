from django.contrib import admin
from .models import (
  Affiliation, Author, File,
  LicenseType, MaterialType, MetadataType,
  NoteType, ResourceType,
  Submittal, SubmittalAuthor, SubmittalFile
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin
import sys

class SubmittalModelAdmin(admin.ModelAdmin):
    # Using value should be a settings.py DATABASES key,
    # actually called a 'connection' name in misc Django messages
    using = 'submit_connection'
    readonly_fields = ('submittal_datetime',)
    # Smaller text form regions
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'80'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'80'})},
    }

    #On admin change list page, show item name, not uuid(the default)
    #list_display = ('item_name',)

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

#end class SubmittalModelAdmin

def agent_available_to_uf(modeladmin, request, queryset):
        queryset.filter(agent='Available').update(agent='UF')

agent_available_to_uf.short_description = "Change Available to UF Partner"

def agent_uf_to_available(modeladmin, request, queryset):
        queryset.filter(agent='UF').update(agent='Available')

agent_uf_to_available.short_description = "Change UF partner to Available "

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

class AuthorAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    search_fields = [
        'surname',
        'given_name',
        'orcid',
        'email_address',
    ]

    list_display = [
        'surname',
        'given_name',
        'orcid',
        'email_address',
    ]

    fields = list_display
    fields.extend([
        'ufdc_user_info',
        ])

    readonly_fields = ['create_datetime',]
# end class Author


class SubmittalAuthorAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]
    search_fields = [
        'submittal',
        'author',
        'rank',
    ]

    list_display = search_fields
    fields = list_display
#end class SubmittalAuthorAdmin

class SubmittalAuthorInline( MinValidatedInlineMixIn, admin.TabularInline):
    model = SubmittalAuthor
    min_num = 1
    extra = 0 # Extra 'empty' rows to show to accommodate immediate adding.
    def get_filters(self, obj):
        return((''))


# { Start class TypeAdmin
class TypeAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    search_fields = [
        'name',
        'text',
    ]
    list_display = [
        'name',
        'text',
    ]
    fields = [
        'name',
        'text',
    ]

# } end class TypeAdmin


# Start class FileAdmin
class FileAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    readonly_fields = ('upload_datetime',)
    list_display = [
        'keywords',
        'description',
    ]
    list_display = list(readonly_fields) + list_display
    search_fields = list_display

    fields = list_display
#end class FileAdmin

# Start class SubmittalFileAdmin
class SubmittalFileAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    search_fields = [
        'submittal',
        'file',
        'rank',
    ]

    list_display = search_fields
    fields = list_display
# end class SubmittalFileAdmin

class FileInline(MinValidatedInlineMixIn,admin.TabularInline):
    model = File
    min_num = 1
    extra = 0


'''
Todo: deprecate
'''
class SubmittalFileInlineOrig(MinValidatedInlineMixIn,admin.TabularInline):
    model = SubmittalFile
    min_num = 1
    extra = 0

    def get_filters(self, obj):
        return((''))

#end class SubmittalFileInline

from django.urls import resolve

class SubmittalFileInline(MinValidatedInlineMixIn,admin.TabularInline):
    model = SubmittalFile
    min_num = 1
    extra = 0

    # Limit choices of files to ones already explicitly uploaded
    # to this submittal (rather than allow choice from all files).
    # This limits plagiarism a bit and makes choices simpler for the user.
    # Consider: It may be simpler to have no choices, as users should
    # add a new file each time, actually...
    # reconsider: maybe just put a submittal field back into the File model
    # and not allow choices as I do for authors...

    #also see: https://stackoverflow.com/questions/21337142/django-admin-inlines-get-object-from-formfield-for-foreignkey#28270041
    def xxformfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request,**kwargs)
        # 'change' is at -1, and id is at -2...
        obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
        print("GOT OBJ_ID={}".format(repr(obj_id)))
        # see also: https://stackoverflow.com/questions/32150088/django-access-the-parent-instance-from-the-inline-model-admin
        field_name = db_field.name
        print("ff_f_ff:Got field_name='{}'".format(field_name))
        if db_field.name =='file' and obj_id.isdigit():
            obj = self.get_object(request, obj_id)
            if obj:
                kwargs['queryset'] = File.objects.filter(submittal=obj )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    '''
    TODO: create a row save condition to REQUERY -- because if change the
    admin-field like keywords, the dd list will still have it...
    better: on admin do always use the id value ..? But a NAME is better to use
    because it is a ddlist... to make a choice... so probably should modify
    logic to re-compute the dd list when a new file is added or name is changed
    per submittal?
    '''
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # 'change' is at -1, and id is at -2...
        path_parts = request.META['PATH_INFO'].rstrip('/').split('/')
        operation = path_parts[-1]
        submittal_id = path_parts[-2]
        # if 'change' is the type, this is a good id
        # if 'change' is the type, this is a good id
        #sys.stdout.flush()
        #sf = SubmittalFile.objects.get(id=sf_id)
        # see also: https://stackoverflow.com/questions/32150088/django-access-the-parent-instance-from-the-inline-model-admin
        if operation == 'change' and db_field.name =='file' :
            try:
                print("TRY OBJ_ID={}".format(repr(submittal_id)))
                #kwargs['queryset'] = File.objects.filter(submittalfile__id=obj_id )
                qs_file = SubmittalFile.objects.filter(submittal_id=submittal_id)
                kwargs['queryset'] = File.objects.filter(id__in=qs_file)

            except IndexError:
                print("INDEX ERRROR")
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# { start class SubmittalAdmin
class SubmittalAdmin(SubmittalModelAdmin, ExportCvsMixin):

    #admin change list display fields to show
    # CHANGE LIST VIEW

    #date_hierarchy = 'agent_modify_date'

    inlines = [SubmittalAuthorInline, SubmittalFileInline]
    # Limit choices of files to ones already explicitly uploaded
    # to this submittal (rather than allow choice from all files).
    # This limits plagiarism a bit and makes choices simpler for the user.
    # Consider: It may be simpler to have no choices, as users should
    # add a new file each time, actually...
    # reconsider: maybe just put a submittal field back into the File model
    # and not allow choices as I do for authors...

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request,**kwargs)
        if db_field.name =='inside_room':
            if request._obj_ is not None:
                field.queryset = (field.queryset.filter(
                  submittal__exact=request._obj_))
            else:
                field.queryset = field.queryset.none()
        return field


# { start class SubmittalAdmin
class SubmittalAdmin(SubmittalModelAdmin, ExportCvsMixin):

    #admin change list display fields to show
    # CHANGE LIST VIEW

    #date_hierarchy = 'agent_modify_date'

    inlines = [SubmittalAuthorInline, SubmittalFileInline,]

    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    list_display = [
        'title_primary',
        'submittal_datetime',
        'license_type',
        'material_type',
        'resource_type',
        ]

    search_fields = [
        'title_primary',
        'license_type',
        'material_type',
        'resource_type',
        ]

    list_filter = [
        'license_type',
        'material_type',
        'resource_type',
        # 'reference_type'
        #,'language', 'place_of_publication',
        ]

    # admin item detailed view order of display fields

    # We also have 'Other Fields' in the database, but Jessica did not
    # select any as important fields to edit.
    # Consider setting editable=False for them?
    fieldsets = (
        ( None,
            {'fields':(
                 'bibid',
                 'language',
                 'title_primary',
                 'license_type',
                 'material_type',
                 'resource_type',
                 'abstract',
                 )
            },
        ),
        # DETAILED VIEW
        ( 'Other Fields', {
             'classes': ('collapse',),
             'fields': (
                 'publisher',
                 'publication_date',
                 )
            }
        )
    )
    '''
    From the django admin cookbook: method to delete an action from admin,
    and in this case it is the 'delete_selected' action.
    '''
    def get_actions(self, request):
        actions = super().get_actions(request)
        action_to_delete = 'delete_selected'
        if action_to_delete in actions:
            #print("actions='{}'".format(repr(actions)))
            del actions[action_to_delete]
        return actions

    '''
    More django admin cookbook tips: to delete add and delete buttons (as all
    BibItem data should be imported?)
    Remove the _exp method name suffix to implement.
    '''
    def has_add_permission_exp(self,request, obj=None):
        # With this, no 'add' button should appear per item
        return False

    def has_delete_permission_exp(self,request, obj=None):
        # With this, no 'delete' button should appear per item
        return False

#  end class SubmittalAdmin }


admin.site.register(Submittal, SubmittalAdmin)
admin.site.register(LicenseType, TypeAdmin)
admin.site.register(MaterialType, TypeAdmin)
admin.site.register(ResourceType, TypeAdmin)
#admin.site.register(MetadataType, TypeAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(SubmittalAuthor, SubmittalAuthorAdmin)
admin.site.register(SubmittalFile, SubmittalFileAdmin)
admin.site.register(File, FileAdmin)
#admin.site.register(SubmittalFile, SubmittalFileAdmin)
admin.site.register(Affiliation, TypeAdmin)

# Register your models here.
