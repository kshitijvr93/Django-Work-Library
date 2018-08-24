from django.contrib import admin
from .models import Item
from django.forms import TextInput, Textarea
from django.db import models

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
def get_agent(request):
        user = User.objects.get(username=request.user)
        print(f'get_agent "{user}"...', file=sys.stdout)
        try:
            agent = CubaLibro.objects.get(user=user).agent
            print(f'profile_cuba_libro.agent "{agent}"', file=sys.stdout)
        except:
            print(f'user "{user}" not in cuba_libro.', file=sys.stdout)
            return ""

        print(f'RETURN profile_cuba_libro.agent "{agent}"', file=sys.stdout)

        sys.stdout.flush()
        return agent

        institution = 'XX' #default for now
        for group in request.user.groups.filter(name__startswith='Cuba Libro '):
            # ASSUME exactly one group starts with cuba_libro_
            # Admin Superuser must manage users and assign exactly one group
            # that startswith cuba_libro_ and endswith one of the item.agent
            # choice codes
            try:
                # print(f'Loop group name "{group.name}"' ,file=sys.stdout)
                institution = group.name.split(' ')[2].upper()
                # print(f'Loop institution "{institution}"' ,file=sys.stdout)
            except:
                continue
        # sys.stdout.flush()
        #return institution
        return agent

def claim_by_agent(modeladmin, request, queryset):
    n_checked = len(queryset)
    print(f"claim: N_checked={n_checked}", file=sys.stdout)
    agent = get_agent(request)
    queryset = queryset.filter(agent='-')
    lq = len(queryset)
    queryset = queryset.update(agent=agent)
    print(f"claim: found count {lq} to change to {agent}"
        ,file=sys.stdout)
    sys.stdout.flush()

    lq = len(queryset)
    print(f"claim: found count {lq} to change",file=sys.stdout)
    sys.stdout.flush()

    queryset.update(agent=my_institution_code)
# end def
claim_by_agent.short_description = "Claim for my institution "
#end

def unclaim_by_agent(modeladmin, request, queryset):
    agent = get_agent(request)
    queryset=queryset.filter(agent=agent).update(agent='-')
unclaim_by_agent.short_description = "Unclaim from my institution"
#end

class ItemAdmin(CubaLibroModelAdmin, ExportCvsMixin):

    readonly_fields = ['id',
                 'holding',
                 ]
    #admin change list display fields to show
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
         'id',
         # 'accession_number',
         'title_primary',
         'holding',
         'pub_year_span',
         'agent',
         'status',
         ]

    list_filter = [
        'agent',
        'status',
        'holding',
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
                 'accession_number',
                 'title_primary',
                 'pub_year_span',
                 'agent',
                 'status',
                 'authors_primary',
                 'notes',
                 'personal_notes',
                 'place_of_publication',
                 'publisher',
                 'language',
                 'link_url',
                 'links',
                 'edition_url',
                 'sub_file_database',
                 'reference_type',
        )}),

        # DETAILED VIEW
        ( 'Other Fields', {
             'classes': ('collapse',),
             'fields': (
                 'reference_type',
                 'periodical_full',
                 'periodical_abbrev',
                 'pub_date_free_from',
                 'volume', 'issue', 'start_page', 'other_pages',
                 'keywords','abstract',
                 'title_secondary', 'titles_tertiary',
                 'authors_secondary', 'authors_tertiary',
                 'authors_quaternary', 'authors_quinary',
                 'edition',
                 'isbn_issn', 'availability', 'author_address',
                 'classification', 'original_foreign_title',
                 'doi', 'pmid','pmcid', 'call_number',
                 'database', 'data_source', 'identifying_phrase',
                 'retrieved_date',
                 )
            }
        )
    )
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
