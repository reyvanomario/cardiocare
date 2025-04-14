from django.db import models

# Create your models here.
from django.db import models
import uuid

class RumahSakit(models.Model):
    id_rumah_sakit = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False, blank=False, db_index=True)
    nama_rumah_sakit = models.CharField(max_length=100, unique=True)
    alamat_rumah_sakit = models.TextField()
    no_telp = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nama_rumah_sakit

class Dokter(models.Model):
    id_dokter = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False, blank=False, db_index=True)
    nama_dokter = models.CharField(max_length=100)
    rumah_sakit = models.ForeignKey(RumahSakit, on_delete=models.CASCADE, related_name='dokter')

    def __str__(self):
        return f"{self.nama_dokter} - {self.rumah_sakit.nama_rumah_sakit}"

class JadwalKonsultasi(models.Model):
    id_jdwl_konsultasi = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False, blank=False, db_index=True)
    dokter = models.OneToOneField(Dokter, on_delete=models.CASCADE, related_name='jadwal_konsultasi')
    hari = models.CharField(max_length=10)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    kuota = models.PositiveIntegerField()

    class Meta:
        unique_together = ('dokter', 'hari', 'jam_mulai')

    def __str__(self):
        return f"{self.hari} | {self.jam_mulai.strftime('%H:%M')} - {self.jam_selesai.strftime('%H:%M')}"

class BookKonsultasi(models.Model):
    id_book_konsultasi = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False, blank=False)
    jadwal = models.ForeignKey(JadwalKonsultasi, on_delete=models.RESTRICT)
    id_pasien = models.UUIDField()
    tanggal_pemesanan = models.DateField(auto_now_add=True)
