import uuid
from django.db import models


class Obat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_obat = models.CharField(max_length=100)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    aturan_pakai = models.TextField(null=True, blank=True)
    stok = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Obat'
        verbose_name_plural = 'Obat'
    
    def __str__(self):
        return self.nama_obat


class TransaksiPembelianObat(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    user_id = models.UUIDField(null=True)
    waktu_transaksi = models.DateTimeField(auto_now_add=True)
    obat = models.ForeignKey(Obat, on_delete=models.CASCADE, related_name='transaksi', verbose_name='Obat yang dibeli')
    quantity = models.IntegerField(default=0)
    total_biaya = models.IntegerField()