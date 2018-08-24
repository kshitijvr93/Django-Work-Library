from django.contrib import admin
from .models import CubaLibro

class CubaLibroAdmin(admin.ModelAdmin):
    list_display = [ 'id','user','agent']
    pass

admin.site.register(CubaLibro, CubaLibroAdmin)
