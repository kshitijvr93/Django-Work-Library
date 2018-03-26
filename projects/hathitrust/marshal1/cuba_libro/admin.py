from django.contrib import admin
from .models import Item
from django.forms import TextInput, Textarea
from django.db import models

'''
todo: complete testing of class UsingModelAdmin(admin.ModelAdmin)
where the __init__.py takes the using argument
class UsingModelAdmin(admin.ModelAdmin):
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

class CubaLibroModelAdmin2(UsingModelAdmin):
    using = 'cuba_libro_connection'

#end class

'''

class CubaLibroModelAdmin(admin.ModelAdmin):
    # Using should be a settings.py DATABASES key, a 'connection' name,
    # actually, as called in misc Django messages
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


def agent_available_to_uf(modeladmin, request, queryset):
        queryset.filter(agent='Available').update(agent='UF')

agent_available_to_uf.short_description = "Change Available agent to UF agent"

def agent_uf_to_available(modeladmin, request, queryset):
        queryset.filter(agent='UF').update(agent='Available')

agent_uf_to_available.short_description = "Change UF agent to Available agent"

class ItemAdmin(CubaLibroModelAdmin):

    #admin change list display fields to show
    # CHANGE LIST VIEW
    search_fields = ['accession_number'
        ,'reference_type', 'language'
        ,'authors_primary', 'title_primary'
        ,'pub_year_span', 'place_of_publication'
        ,'isbn_issn', 'call_number','doi', 'pmid','pmcid'
        ]

    date_hierarchy = 'agent_modify_date'
    # See raw_id_fiels = ('some foreigh key') when you have a foreign key
    #
    actions = [agent_uf_to_available, agent_available_to_uf]
    list_display = [
         'accession_number',
         'title_primary',
         'pub_year_span',
         'reference_type',
         'holding',
         'agent',
         'agent_modify_date',
         ]

    list_filter = ['agent', 'reference_type'
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
                 'holding',
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



admin.site.register(Item, ItemAdmin)

# Register your models here.
