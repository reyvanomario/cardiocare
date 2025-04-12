from rest_framework.serializers import ModelSerializer
from .models import BookKonsultasi
    
class BookKonsultasiSerializer(ModelSerializer):
    class Meta:
        model = BookKonsultasi
        fields = ["id_book_konsultasi", "jadwal", "id_pasien", "tanggal_pemesanan"]
        extra_kwargs = {
            "id_pasien": {"read_only": True},
            "tanggal_pemesanan": {"read_only": True}
        }