import uuid
from django.db import models


class Obat(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    nama_obat = models.CharField(max_length=255)
    harga = models.IntegerField()
    deskripsi = models.TextField(max_length=1000)
    aturan_pakai = models.TextField(max_length=1000)
    stok = models.IntegerField()


class TransaksiPembelianObat(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    waktu_transaksi = models.DateTimeField(auto_now_add=True)
    obat = models.ForeignKey(Obat, on_delete=models.CASCADE, related_name='transaksi', verbose_name='Obat yang dibeli')
    total_biaya = models.IntegerField()
