from django.contrib import admin
from .models import Item, File, Yaml, PrintScanYaml, DigitalBornYaml
from .views import FormUploadFile
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
        if action_to_delete in actions:
            del actions[action_to_delete]

#end class HathiModelAdmin

class FileInline(admin.TabularInline):
    model = File
    show_change_link = True
    extra = 0 # show no extra blank rows to enter data
    fields = ('topic','content_type','size')
    readonly_fields = ('content_type','size')

    def has_add_permission(self,request, obj=None):
        # With False, no 'add' button/link should appear for this inline table.
        return True


class ItemModelAdmin(HathiModelAdmin):
    list_display = ['name', 'status', 'bib_vid', 'modify_date',]
    search_fields = ['name','status',]
    inlines = (FileInline,)



from django import forms

class FileModelAdmin(HathiModelAdmin):
  #{{{ custom field widget settings
  def formfield_for_dbfield(self, db_field, **kwargs):
    # Set form to upload form to use for adding...
    #form_field = super(FileModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    form_field = super().formfield_for_dbfield(db_field, **kwargs)
    dw = form_field.widget.attrs

    if db_field.name in ('topic', 'up_name', 'down_name', 'link_name', 'url'):
       dw['class'] = 'special'
       dw['size'] = '128'

    return form_field
  # end def formfield-for_dbfield

  # form = FormUploadFile
  # add_form = FormUploadFile
  readonly_fields = ('date_time',)

  # fields to display on the 'select' list
  list_display = ('id','item','topic','content_type','size',)
  search_fields = [ 'topic', 'upload_name' ]

  list_filter = ['content_type',]
  ordering = ['-id']

  # fieldsets for edit-form display
  fieldsets = (
    (None, {
      'fields': (  'topic', 'up_name',  'item', 'location')
    }),

    ('Details', {
      'classes': ('collapse',),
      'fields': ('url','down_name','content_type','charset','size', 'sha512',
      'description',
      'department','public','date_time'
      )
    }),
    )
    # end fieldsets

  '''
    More django admin cookbook tips: to delete add and delete buttons (as all
    CubaLibro data should be imported?)
    Remove the _exp method name suffix to implement.
  '''
  def has_add_permission(self,request, obj=None):
        # With False, no 'add' button should appear per item
        return True

  # classes Meta, Media
  class Meta:
    ordering = ('-date_time', 'department',)

  class Media:
    js = ('jquery/jquery.js',
          # 'wymeditor/jquery.wymeditor.js',
          'admin_textarea.js')

  # end classes Media, Meta
# end class FileModelAdmin

admin.site.register(File, FileModelAdmin)
admin.site.register(Item, ItemModelAdmin)
admin.site.register(Yaml, admin.ModelAdmin)
admin.site.register(PrintScanYaml, admin.ModelAdmin)
admin.site.register(DigitalBornYaml, admin.ModelAdmin)


#admin.site.register(Upload, HathiModelAdmin)
