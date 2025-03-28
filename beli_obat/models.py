import uuid
from django.db import models


class Obat(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    nama_obat = models.CharField(max_length=255)
    harga = models.IntegerField()
    deskripsi = models.TextField(max_length=1000)
    aturan_pakai = models.TextField(max_length=1000)
    stok = models.IntegerField()
