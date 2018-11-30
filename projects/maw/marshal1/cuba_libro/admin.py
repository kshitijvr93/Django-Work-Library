from django.contrib import admin
from .models import (Institution, Item, Profile, )
from django import forms
from django.forms import TextInput, Textarea
from django.db import models
from collections import OrderedDict
from django.contrib.auth import get_user_model
#User = get_user_model()
from django.contrib.auth.models import User

'''
Nice ExportCvsMixin class presented and covered, on 20180402 by:
https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
'''
import csv
from django.http import HttpResponse
from django_admin_listfilter_dropdown.filters import (
    RelatedDropdownFilter, DropdownFilter,
)

class ExportCvsMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        #response = HttpResponse(content_type='text/csv')
        response = HttpResponse(content_type='text/csv charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename={}.csv'.format(meta))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow(
                [getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

# end class ExportCvsMixin

class CubaLibroModelAdmin(admin.ModelAdmin):
    # Using value should be a settings.py DATABASES key,
    # actually called a 'connection' name in misc Django messages
    using = 'cuba_libro_connection'
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
    # end def formfield_for_manytomany
#end class CubaLibroModelAdmin

import sys

'''
Get and return this request's user's profile.agent field
'''
from django.contrib import messages
def get_agent(request=None, verbosity=0):
    me = 'get_agent'
    username = request.user
    if verbosity > -1:
      print(f"{me}: username is {username}", file=sys.stdout)
    #user = User.objects.get(username=username)
    #print(f'get_agent "{user}"...', file=sys.stdout)
    try:
        profile = Profile.objects.get(username=username)
    except Exception as e:
        msg = (f'{me}:e={e}. Did not find {username} in Profile.username')
        messages.error(request, msg)
        return None

    if profile is None:
        profile_username = 'None'
        agent = None
        # for now, return None - because we cannot use a fkey to
        # another db, so allow for human naming errors
        # Just write msg to stdout now ....
        # later:generate nice message if not found
        print(msg, file=sys.stdout)
        msg = (f'{me}:e={e}. Did not find {username} in Profile.username')
        messages.error(request, msg)
        return None
    else:
        profile_username = profile.username
        agent = profile.agent

    if verbosity > 0:
      print(f'{me}:Found {profile_username} in Profile.username',
        file=sys.stdout)
    if verbosity > 0:
        agent_name = 'None' if profile is None else agent.name
        if verbosity > 0:
          print(f'{me}:Found {username} in Profile.username with '
            f'institution/agent.name={agent_name}', )
    #print(f'RETURN profile.agent "{agent}"', file=sys.stdout)
    #sys.stdout.flush()
    return agent

def claim_by_agent(modeladmin, request, queryset, verbosity=1):
    me = 'claim_by_agent'
    '''
    try:
        profile = Profile.objects.get(username=username)
    except Exception as e:
      msg = (f'{me}:e={e}. Did not find {username} in Profile.username')
      messages.warning(request, msg)
      return None
    '''

    agent = get_agent(request=request, verbosity=1)
    n_checked = len(queryset)
    items = queryset.filter(agent__exact=None)
    n_claimed = len(items)
    #  UPDATE the items
    items.update(agent=agent)
    n_not_claimed = n_checked - n_claimed

    if n_claimed > 0:
        msg = (f"Of your {n_checked} checked items, you just now "
          f"claimed {n_claimed} items.")
        messages.info(request,msg)

    if n_not_claimed > 0:
        msg = (
          f"Of your {n_checked} checked items, {n_not_claimed} items "
          "were not just now claimed by you because those are already "
          "claimed by an institution. "
          )
        messages.warning(request,msg)
# end def

claim_by_agent.short_description = "Claim by my institution "
#end

def unclaim_by_agent(modeladmin, request, queryset):
    username = request.user
    '''
    try:
        profile = Profile.objects.get(username=username)
    except Exception as e:
      print(f'{me}:e={e}. Did not find {username} in Profile.username',
        file=sys.stdout)
      return None
    '''
    agent = get_agent(request=request, verbosity=1)
    n_checked = len(queryset)
    items = queryset.filter(agent=agent)
    n_unclaimed = len(items)
    items.update(agent=None)
    n_not_unclaimed = n_checked - n_unclaimed

    if n_unclaimed > 0:
        msg = (f"Of your {n_checked} checked items, you just "
          f"unclaimed {n_unclaimed} items.")
        messages.info(request,msg)
    if n_not_unclaimed > 0:
        msg = (
          f"Of your {n_checked} checked items, {n_not_unclaimed} items "
          "were not just now unclaimed by you because those are not "
          "claimed by your institution. "
          )
        messages.warning(request,msg)

# end def unclaim_by_agent

unclaim_by_agent.short_description = "Unclaim by my institution"
#end

class InstitutionAdmin(CubaLibroModelAdmin, ExportCvsMixin):

    # admin change list display fields to search
    # CHANGE LIST VIEW
    search_fields = ['id','name20' ,'name', 'oclc_name','notes']

    #date_hierarchy = 'agent_modify_date'
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
    ]

    list_display = [
         # 'id',
         # 'accession_number',
         'name20',
         'name',
         'oclc_name',
         ]

    # EXPLICIT - (but this is also done implicitly, but implies you can
    # one or more link fields, and also need not use than the first)
    # list_display_links = [list_display[0],list_display[1]]
    list_display_links = list_display
    fields = list_display + ['link_url','notes']

    # Control the admin change list order of displayed rows
    def get_ordering(self, request):
        return['name20']

    '''
    From the django admin cookbook: method to delete an action from admin,
    and in this case it is the 'delete_selected' action.
    Also can allow only certain actions for users in certain groups.
    '''
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions_to_delete = ['delete_selected']

        # change this logic later
        for action_to_delete in actions_to_delete:
            if action_to_delete in actions:
                #print("actions='{}'".format(repr(actions)))
                del actions[action_to_delete]
        return actions
    #end def get_actions

    '''
    More django admin cookbook tips: to delete add and delete buttons (as all
    CubaLibro data should be imported?)
    Remove the _exp method name suffix to implement.
    '''
    def has_add_permission_exp(self,request, obj=None):
        # With this, no 'add' button should appear per item
        return False

    def has_delete_permission_exp(self,request, obj=None):
        # With this, no 'delete' button should appear per item
        return False
# end InstitutionAdmin

admin.site.register(Institution, InstitutionAdmin)


class ProfileAdmin(CubaLibroModelAdmin):
    list_display = ['id','username','agent',]
    # Note
    pass
# NB: Django 2.1 does NOT support foreign key to other db, so
# Here we just use username to match auth_user, but there cannot be
# a foreign key to auth_user to achieve automatic value validations.
admin.site.register(Profile, ProfileAdmin)

class ItemAdmin(CubaLibroModelAdmin, ExportCvsMixin):

    search_fields = ['id','accession_number'
        ,'reference_type', 'language'
        ,'authors_primary', 'title_primary'
        ,'pub_year_span', 'place_of_publication'
        ,'isbn_issn', 'call_number','doi', 'pmid','pmcid'
        ]

    #date_hierarchy = 'agent_modify_date'
    actions = [
        'export_as_csv', # Mixin: so set the method name string value.
                         # Need reference doc?
        unclaim_by_agent, #External, so set the function value
        claim_by_agent, #External, so set the function value
    ]

    list_display = [
         # 'id',
         # 'accession_number',
         'title_primary',
         'holding',
         'pub_year_span',
         'agent',
         # 'institution',
         'status',
         ]

    # EXPLICIT - (but this is also done implicitly, but implies you can
    # one or more link fields, and also need not use than the first)
    list_display_links = [list_display[0]]

    list_filter = [
        ('agent', RelatedDropdownFilter),
        ('holding', DropdownFilter),
        ('status', DropdownFilter),
        # 'reference_type'
        #,'language', 'place_of_publication',
        ]

    # Now for 'CHANGE ITEM" view'
    # admin item detailed view order of display fields
    # We also have 'Other Fields' in the database, but Jessica did not
    # select any as important fields to edit.
    # Consider setting editable=False for them?
    # field type:
    #    ed is editable, ro is readonly (aka display only)
    #    hed is default hidden editable, hros default hidden and readonly
    d_field_type = OrderedDict({
                 'title_primary':'title',
                 #Some posts say next syntax puts multi fields on one display
                 #line, but does not work. Leave as is for posterity.
                 ('pub_year_span','link_url'):'title',
                 'accession_number': 'title_ro',
                 # 'agent' field is readonly as it should be edited only by
                 # user actions on 'change list' admin page
                 # and also need not be displayed here.
                 'agent':'mgmt_ro',
                 'status':'mgmt',
                 'status_notes':'mgmt',
                 'authors_primary':'ed',
                 'notes':'ed',
                 'personal_notes':'ed',
                 'place_of_publication':'ed',
                 'publisher':'ed',
                 'language':'ed',
                 'links':'ed',
                 'edition_url':'ed',
                 'sub_file_database':'ed',
                 'reference_type':'ed',
                 'holding':'mgmt_ro',
                 # 'id':'ed',
                 'periodical_full':'hro',
                 'periodical_abbrev':'hro',
                 'pub_date_free_from':'hro',
                 'volume':'hro',
                 'issue':'hro',
                 'start_page':'hro',
                 'other_pages':'hro',
                 'keywords':'hro',
                 'abstract':'hro',
                 'title_secondary':'hro',
                 'titles_tertiary':'hro',
                 'authors_secondary':'hro',
                 'authors_tertiary':'hro',
                 'authors_quaternary':'hro',
                 'authors_quinary':'hro',
                 'edition':'hro',
                 'isbn_issn':'hro',
                 'availability':'hro',
                 'author_address':'hro',
                 'classification':'hro',
                 'original_foreign_title':'hro',
                 'doi':'hro',
                 'pmid':'hro',
                 'call_number':'hro',
                 'database':'hro',
                 'data_source':'hro',
                 'identifying_phrase':'hro',
                 'retrieved_date': 'hro'
    })

    # Must include names of all model-defined uneditable (editable=False)
    #  fields in the readonly_fields[] list  below, else get runtime error.
    # Now 'holding' is the only model-defined editable=False field.
    # So it -must- appear in this readonly_fields list.
    # However it is OK, as done here, to also add some editble=True fields
    # to the readonly_fields list. Later I might change those, too,
    # in the database model to set editible=False.
    readonly_fields = ( [ k for k,v in d_field_type.items() if v == 'title_ro']
         + [ k for k,v in d_field_type.items() if v == 'mgmt_ro']
         + [ k for k,v in d_field_type.items() if v == 'hro']
    )

    fieldsets = (
        ( 'Identity', # Editible 'normal' form fields
            {'fields': tuple([ k for k,v in d_field_type.items() if v == 'title']
            + [ k for k,v in d_field_type.items() if v == 'title_ro']) }
        ),
        ( 'Item Management', # Editible 'normal' form fields
            {'fields': [ k for k,v in d_field_type.items() if v == 'mgmt']
            + [ k for k,v in d_field_type.items() if v == 'mgmt_ro'] }
        ),
        ( 'Editable Fields', # Editible 'normal' form fields
            {'fields': [ k for k,v in d_field_type.items() if v == 'ed'] }
        ),
        ( 'Other Fields', {
             'classes': ('collapse',),
             'fields': [ k for k,v in d_field_type.items() if v == 'hro']
            }
        ),
    )
    # Control the admin change list order of displayed rows
    def get_ordering(self, request):
        return['title_primary']

    '''
    From the django admin cookbook: method to delete an action from admin,
    and in this case it is the 'delete_selected' action.
    Also can allow only certain actions for users in certain groups.
    '''
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions_to_delete = ['delete_selected']

        # change this logic later
        for action_to_delete in actions_to_delete:
            if action_to_delete in actions:
                #print("actions='{}'".format(repr(actions)))
                del actions[action_to_delete]
        return actions
    #end def get_actions

    '''
    More django admin cookbook tips: to delete add and delete buttons (as all
    CubaLibro data should be imported?)
    Remove the _exp method name suffix to implement.
    '''
    def has_add_permission_exp(self,request, obj=None):
        # With this, no 'add' button should appear per item
        return False

    def has_delete_permission_exp(self,request, obj=None):
        # With this, no 'delete' button should appear per item
        return False

#end class ItemAdmin

admin.site.register(Item, ItemAdmin)
