from django.db import models
import uuid

class Dokter(models.Model):
    id_dokter = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, null=False, blank=False, db_index=True)
    nama_dokter = models.CharField(max_length=100)
    kuota = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.nama_dokter} (Kuota: {self.kuota})"