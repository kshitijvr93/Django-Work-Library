from django.contrib import admin
from .models import Item, File
from django.db import models
from django.forms import TextInput, Textarea

class HathiModelAdmin(admin.ModelAdmin):
    # Using should be a settings.py DATABASES key, a 'connection' name,
    # actually, as called in misc Django messages
    using = 'hathitrust_connection'

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
        if action in actions:
            del actions[action_to_delete]

#end class HathiRouter


class ItemModelAdmin(HathiModelAdmin):
    list_display = ['name', 'status', 'folder_path', 'modify_date',]
    search_fields = ['name','status',]

admin.site.register(Item, ItemModelAdmin)


from django import forms

class FileModelAdmin(HathiModelAdmin):
  #{{{ custom field widget settings
  def formfield_for_dbfield(self, db_field, **kwargs):
    form_field = super(FileModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    dw = form_field.widget.attrs

    if db_field.name == 'topic':
       dw['class'] = 'special'
       dw['size'] = '128'

    elif db_field.name == 'up_name':
       dw['class'] = 'special'
       dw['size'] = '128'

    elif db_field.name == 'down_name':
       dw['class'] = 'special'
       dw['size'] = '128'

    elif db_field.name == 'link_name':
       dw['class'] = 'special'
       dw['size'] = '128'

    elif db_field.name == 'url':
       dw['class'] = 'special'
       dw['size'] = '128'

    return form_field
  # end def formfield-for_dbfield

  readonly_fields = ('date_time',)

  # fields to display on the 'select' list
  list_display = ('id','department','topic','public','date_time')
  search_fields = [ 'topic' ]

  list_filter = ['date_time','department','public']
  ordering = ['-date_time']

#{{{ fieldsets for edit-form display
  fieldsets = (
    ('Header', {
      'classes': ('collapse',),
      'fields': ('department','public','date_time')
    }),
    (None, {
      'fields': ('url','down_name','topic','description',)
    }),
    ('Details', {
      'classes': ('collapse',),
      'fields': ('up_name','content_type','charset','size', 'sha512')
    }),
    )
  # end fieldsets

  # classes Meta, Media
  class Meta:
    ordering = ('-date_time', 'department',)

  class Media:
    js = ('jquery/jquery.js',
          'wymeditor/jquery.wymeditor.js',
          'admin_textarea.js')

  # classes Media, Meta
# end FileModelAdmin

admin.site.register(File,FileModelAdmin)


#admin.site.register(Upload, HathiModelAdmin)
