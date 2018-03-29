from django.contrib import admin
from .models import Item, File, Upload

class HathiModelAdmin(admin.ModelAdmin):
    # Using should be a settings.py DATABASES key, a 'connection' name,
    # actually, as called in misc Django messages
    using = 'hathitrust_connection'
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

class ItemAdmin(HathiModelAdmin):
    list_display = ['name', 'status', 'folder_path', 'modify_date',]
    search_fields = ['name','status',]

admin.site.register(Item, ItemAdmin)
admin.site.register(Upload, HathiModelAdmin)
admin.site.register(File, HathiModelAdmin)

# Register your models here.
