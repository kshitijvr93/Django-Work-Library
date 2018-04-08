from django.contrib import admin
from .models import (Location, Project,
  SensorType, Sensor, SensorService, SensorDeploy, WaterObservation
  )

# from .views import FormUploadFile
from django.db import models
from django.forms import TextInput, Textarea
from django import forms #For ModelForm

import csv
from django.http import HttpResponse

'''
requires:
   import csv
   from django.http import HttpResponse
'''
class ExportCvsMixin:

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename={}.csv'.format(meta))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow(
                [getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

#end class ExportCvsMixin


class LcroysterModelAdmin(admin.ModelAdmin):
    # Using should be a settings.py DATABASES key, a 'connection' name,
    # actually, as called in misc Django messages
    using = 'lcroyster_connection'

    # Note, these overrides are for model fields withough explicit forms
    # Where a form is defined, its form.CharField(..widget params...) widgets
    # will NOT be overridden by these overrides.
    formfield_overrides = {
      models.CharField: { 'widget': TextInput( attrs={'size':'60'})},
      models.TextField: { 'widget': Textarea( attrs={'rows':1, 'cols':'60'})},
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

#end class LcroysterModelAdmin


class ProjectModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    using = 'lcroyster_connection'
    list_display = [
      'project_id','name','principal_investigators'
      ]

    actions = [
      'export_as_csv',
    ]

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
# end class ProjectModelAdmin

admin.site.register(Project, ProjectModelAdmin)

class LocationModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    #Maybe need this to show action list ?
    using = 'lcroyster_connection'

    # Field order for admin 'ADD' Form
    fields = [
        'location_id',
        'name',
        'alias1',
        'alias2',
        'notes',
        'latitude',
        'longitude',
        'tile_id',
        ]

    search_fields = [
        'name', 'alias1', 'alias2', 'tile_id'
    ]

    list_display = ['location_id','name','alias1', 'latitude','longitude']

    actions = [
      'export_as_csv',
    ]

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
# end class LocationModelAdmin


admin.site.register(Location, LocationModelAdmin)

class SensorTypeModelAdmin(LcroysterModelAdmin, ExportCvsMixin):

    actions = [
      'export_as_csv',
    ]

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

admin.site.register(SensorType, SensorTypeModelAdmin)

class SensorModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    list_display = [
        'sensor_type','serial_number',
        'location_id',
      ]

    actions = [
      'export_as_csv',
    ]

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

admin.site.register(Sensor, SensorModelAdmin)

class SensorServiceModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    actions = [
      'export_as_csv',
    ]

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

# end class SensorServiceModelAdmin
admin.site.register(SensorService, SensorServiceModelAdmin)

class SensorDeployModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    list_display = ['sensor_id', 'deploy_datetime','location_id']

    actions = [
      'export_as_csv',
    ]

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

#end class SensorDeployModelAdmin


admin.site.register(SensorDeploy, SensorDeployModelAdmin)

class WaterObservationModelAdmin(LcroysterModelAdmin, ExportCvsMixin):
    actions = [
      'export_as_csv',
    ]

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
# end class WaterOvservationModelAdmin

admin.site.register(WaterObservation, WaterObservationModelAdmin)
