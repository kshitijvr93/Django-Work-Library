from django.contrib import admin
from .models import (
  Author, MaterialType, MetadataType, NoteType, ResourceType, Submittal,
  SubmittalAuthor, File, SubmittalFile
  )

from django.forms import TextInput, Textarea
from django.db import models
from maw_utils import ExportCvsMixin

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


# { start class SubmittalAdmin
class SubmittalAdmin(SubmittalModelAdmin, ExportCvsMixin):

    #admin change list display fields to show
    # CHANGE LIST VIEW

    #date_hierarchy = 'agent_modify_date'

    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    list_display = [
        'title_primary',
        'submittal_datetime',
        'material_type',
        'resource_type',
        'metadata_type',
        ]

    search_fields = [
        'title_primary',
        'material_type',
        'resource_type',
        'metadata_type',
        ]

    list_filter = [
        'material_type',
        'resource_type',
        'metadata_type',
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
                 'author',
                 'material_type',
                 'resource_type',
                 'metadata_type',
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

# { Start class TypeAdmin
class TypeAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    search_fields = [
        'name',
        'description',
    ]
    list_display = [
        'name',
        'description',
    ]
    fields = [
        'name',
        'description',
    ]

# } end class TypeAdmin

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

# class
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


# Start class SubmittalFileAdmin
class FileAdmin(admin.ModelAdmin, ExportCvsMixin):
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]
    search_fields = [
        'submittal',
        'description',
        'solitary_download_name',
        'submittal_download_name',
    ]

    list_display = search_fields
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
#end class SubmittalFileAdmin

admin.site.register(Submittal, SubmittalAdmin)
admin.site.register(MaterialType, TypeAdmin)
admin.site.register(ResourceType, TypeAdmin)
admin.site.register(MetadataType, TypeAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(SubmittalAuthor, SubmittalAuthorAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(SubmittalFile, SubmittalFileAdmin)

# Register your models here.
