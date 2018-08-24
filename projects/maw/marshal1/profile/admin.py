from django.contrib import admin
from .models import CubaLibro

class CubaLibroAdmin(admin.ModelAdmin):
    pass

admin.site.register(CubaLibro, CubaLibroAdmin)
