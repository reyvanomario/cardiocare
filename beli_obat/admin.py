from django.contrib import admin
from .models import Obat

@admin.register(Obat)
class ObatAdmin(admin.ModelAdmin):
    list_display = ('nama_obat', 'harga', 'stok')
    search_fields = ('nama_obat', 'deskripsi', 'aturan_pakai')
    list_filter = ('stok',)
    fieldsets = (
        ('Informasi Obat', {
            'fields': ('nama_obat', 'deskripsi')
        }),
        ('Aturan Pakai', {
            'fields': ('aturan_pakai',)
        }),
        ('Detail Harga & Stok', {
            'fields': ('harga', 'stok')
        }),
    )