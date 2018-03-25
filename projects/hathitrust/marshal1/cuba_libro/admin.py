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
    list_display = ['accession_number', 'agent',
         'agent_modify_date',
         'title_primary',
         'pub_year_span',
         'data_source',
         ]
    search_fields = ['accession_id', 'reference_type',
        'authors_primary', 'title_primary','call_number']
    list_filter = ['agent', 'reference_type', 'data_source',
         ]
    date_hierarchy = 'agent_modify_date'
    # See raw_id_fiels = ('some foreigh key') when you have a foreign key
    #
    actions = [agent_uf_to_available, agent_available_to_uf]


admin.site.register(Item, ItemAdmin)

# Register your models here.
