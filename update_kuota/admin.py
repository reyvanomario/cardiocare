from django.contrib import admin

# dokter/admin.py
from django.contrib import admin
from .models import Dokter

@admin.register(Dokter)
class DokterAdmin(admin.ModelAdmin):
    list_display = ['nama_dokter', 'kuota']
    search_fields = ['nama_dokter']
