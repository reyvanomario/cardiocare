from django.db import models

class Obat(models.Model):
    nama_obat = models.CharField(max_length=100)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    aturan_pakai = models.CharField(max_length=100, null=True, blank=True)
    stok = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Obat'
        verbose_name_plural = 'Obat'
    
    def __str__(self):
        return self.nama_obat