from django.db import models


class Obat(models.Model):
    nama_obat = models.CharField(max_length=255)
    harga = models.IntegerField()
    deskripsi = models.TextField(max_length=1000)
    aturan_pakai = models.TextField(max_length=1000)
    stok = models.IntegerField()
