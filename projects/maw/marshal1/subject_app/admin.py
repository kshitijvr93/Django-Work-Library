from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    SubjectJob, Thesaurus
    )
import os, sys


from django.db import models
from django.forms import ModelForm, TextInput, Textarea, BaseInlineFormSet
from django import forms

class SubjectAppAdmin(admin.ModelAdmin):
    # Using should be a settings.py DATABASES key, a 'connection' name,
    # actually, as called in misc Django messages
    using = 'subject_app_connection'

    # Note, these overrides are for model fields withough explicit forms
    # Where a form is defined, its form.CharField(..widget params...) widgets
    # will NOT be overridden by these overrides.
    formfield_overrides = {
      models.CharField: { 'widget': TextInput( attrs={'size':'100'})},
      models.TextField: { 'widget': Textarea( attrs={'rows':1, 'cols':'100'})},
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

    '''
    From the django admin cookbook: method to delete an action from admin,
    and in this case it is the 'delete_selected' action.
    '''

    def get_actions(self, request):
        actions = super().get_actions(request)
        action_to_delete = 'delete_selected'
        if action_to_delete in actions:
            del actions[action_to_delete]
#end class SubjectAppAdmin


class SubjectJobThesaurusInline(admin.TabularInline):
    model = Thesaurus
    fields = ('subject_job_id','name')


class SubjectJobAdmin(SubjectAppAdmin):
    # Consider -- add user field in the future
    list_display = ('id','batch_set','thesaurus','status','create_datetime', 'end_datetime')
    fields = ('id','batch_set','thesaurus','notes','status','packages_created','jp2_images_processed', 'create_datetime', 'end_datetime',)
    readonly_fields = ('id','status','packages_created',
      'jp2_images_processed', 'create_datetime','end_datetime',)

    inlines = [SubjectJobThesaurusInline]

    def get_readonly_fields(self, request, obj=None):
        '''
        Allow some field value changes on inital add, but
        after initial insert, add them to readonly_fields.
        '''
        if obj: # editing an existing object
            return self.readonly_fields + ('batch_set', )
        return self.readonly_fields










class SubjectJobThesaurusAdmin(SubjectAppAdmin):
    # Consider -- add user field in the future
    list_display = ('id','subject_job_id','name',)
    fields = ('id','subject_job_id','name',)
    readonly_fields = ('id',)


    def get_readonly_fields(self, request, obj=None):
        '''
        Allow some field value changes on inital add, but
        after initial insert, add them to readonly_fields.
        '''
        if obj: # editing an existing object
            return self.readonly_fields + ('batch_set', )
        return self.readonly_fields


admin.site.register(SubjectJob, SubjectJobAdmin)
admin.site.register(Thesaurus, SubjectJobThesaurusAdmin)
