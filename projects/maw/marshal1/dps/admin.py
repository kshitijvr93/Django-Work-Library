from django.contrib import admin
from .models import (
    Bibvid,
    RelatedTerm,
    TermEval,
    TermResponse,
    Thesauri,
    Thesaurus,
    )

from django.forms import TextInput, Textarea
from django.db import models

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


'''
TODO: move to common module - used also in other MAW apps
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

#Modeled after snow's admin.py class AttributeInline
class RelatedTermInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = Attribute
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
class TermEvalInline(
    #MinValidatedInlineMixIn, SnowNestedStackedInline):
    MinValidatedInlineMixIn, admin.TabularInline):
    model = Attribute
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

# { Admin for model Thesauri
# NB: Must stick to django 2.0.7 or visit to this model
# using django 2.1 fails when
#using django-mptt version 0.91 latest on 20180828
# maybe recheck later. Tradeoff is we need django 2.1 to
# manage 'view' model permissions.. so keep checking.
#
class ThesauriAdmin(DjangoMpttAdmin):
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
# end class ThesauriAdmin(DjangoMpttAdmin)
admin.site.register(Thesauri, ThesauriAdmin)

# } Admin for model Thesauri

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
class BibvidAdmin:
    pass
admin.site.register(Bibvid, BibVidAdmin)
# } Admin for model Bibvid}

# { Admin code
class TermReponseAdmin:
    formfield_overrides = {
        models.CharField: { 'widget': TextInput(
          attrs={'size':'20'})},
        models.TextField: { 'widget': Textarea(
          attrs={'rows':1, 'cols':'60'})},
    }
    inlines = [TermEvalInline, ]
    def get_sortable_by():
        return []
    pass
admin.site.register(TermResponse, TermResponseAdmin)
# } Admin code
