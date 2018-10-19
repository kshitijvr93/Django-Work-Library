from django.contrib import admin
from .models import Institution, Item
from django import forms
from django.forms import TextInput, Textarea
from django.db import models
from collections import OrderedDict

'''
Nice ExportCvsMixin class presented and covered, on 20180402 by:
https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
'''
import csv
from django.http import HttpResponse

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
from django.contrib.auth.models import User, Group
from profile.models import CubaLibro

import sys

'''
Get the profile_CubaLibro.agent field
object of the current request's user and return it.
'''
def get_agent(request):
        user = User.objects.get(username=request.user)
        #print(f'get_agent "{user}"...', file=sys.stdout)
        try:
            agent = CubaLibro.objects.get(user=user).agent
           # print(f'profile_cuba_libro.agent "{agent}"', file=sys.stdout)
        except:
           # print(f'user "{user}" not in cuba_libro.', file=sys.stdout)
            return ""
        #print(f'RETURN profile_cuba_libro.agent "{agent}"', file=sys.stdout)
        #sys.stdout.flush()
        return agent

from django.contrib import messages
def claim_by_agent(modeladmin, request, queryset):
    agent = get_agent(request)
    # print(f"claim: got user's agent={agent}", file=f)
    n_checked = len(queryset)
    items = queryset.filter(agent__exact='-')
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
    agent = get_agent(request)
    n_checked = len(queryset)
    items = queryset.filter(agent=agent)
    n_unclaimed = len(items)
    items.update(agent='-')
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
    search_fields = ['id','name20' ,'name', 'notes']

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
         'notes',
         ]

    # EXPLICIT - (but this is also done implicitly, but implies you can
    # one or more link fields, and also need not use than the first)
    list_display_links = [list_display[0],list_display[1]]
    fields = list_display

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

# see https://stackoverflow.com/questions/29310117/django-programming-error-1146-table-doesnt-exist#29310275
# queries are done before migration, so comment out the Item.objects.values_list
# line until migration is applied...
#class ItemListForm(forms.ModelForm):
class ItemListForm():
    '''
    This is the "Select" or admin "List" form for Cuba Libro object 'Item'
    It is created to substitute entirely for the default Item form used by
    the admin List or Select item page to allow/provide a dropdown widget filter
    instead of a lengthy filter that displays all options at once.
    See: https://stackoverflow.com/questions/21497044/filter-a-field-in-a-dropdown-lit-in-django-admin#21497167

    '''
    class Meta:
        model = 'Item'
        fields = '__all__'

    # This caused problem continue later after have model Institution working
    # see https://stackoverflow.com/questions/29310117/django-programming-error-1146-table-doesnt-exist#29310275
    # institutions = (Item.objects.values_list('institution', flat=True).
    #   order_by('institution').distinct() )

    choice_list = []
    #for institution in institutions:
    #    choice_list.append(institution)
    INSTITUTION_CHOICES = choice_list

    institution2 = (forms.ChoiceField(widget=forms.Select,
        choices=INSTITUTION_CHOICES))


class ItemAdmin(CubaLibroModelAdmin, ExportCvsMixin):
    # custom form defined above
    # comment out to cure migration woes 20181019
    # form = ItemListForm

    # admin change list display fields to search
    # CHANGE LIST VIEW
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
         'institution',
         'status',
         ]

    # EXPLICIT - (but this is also done implicitly, but implies you can
    # one or more link fields, and also need not use than the first)
    list_display_links = [list_display[0]]

    list_filter = [
        'institution',
        'holding',
        'agent',
        'status',
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
                 'institution':'mgmt',
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
