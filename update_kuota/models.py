from django.db import models
import uuid
from book_konsultasi.models import RumahSakit

class JadwalKonsultasi(models.Model):
    rumah_sakit = models.ForeignKey(RumahSakit, on_delete=models.CASCADE)
    id_dokter = models.UUIDField()
    nama_dokter = models.CharField(max_length=100)
    kuota = models.PositiveIntegerField()