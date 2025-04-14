from django.contrib import admin
from .models import RumahSakit, Dokter, JadwalKonsultasi, BookKonsultasi

def get_all_fields(model):
    return [field.name for field in model._meta.fields]

@admin.register(RumahSakit)
class RumahSakitAdmin(admin.ModelAdmin):
    list_display = get_all_fields(RumahSakit)

@admin.register(Dokter)
class DokterAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Dokter)

@admin.register(JadwalKonsultasi)
class JadwalKonsultasiAdmin(admin.ModelAdmin):
    list_display = get_all_fields(JadwalKonsultasi)

@admin.register(BookKonsultasi)
class BookKonsultasiAdmin(admin.ModelAdmin):
    list_display = get_all_fields(BookKonsultasi)
