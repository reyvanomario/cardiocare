import os
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cardio_care.settings')
django.setup()

from beli_obat.models import Obat

def import_data():
    # Hapus data lama (opsional)
    Obat.objects.all().delete()
    print("Data lama dihapus")
    
    # Path ke file data
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'obat.txt')
    
    # Baca file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    
    # Split data berdasarkan VALUES
    rows = data.split('),')
    count = 0
    
    for row in rows:
        try:
            # Ekstrak data
            match = re.search(r"'([^']*)',\s*([0-9.]*),\s*'([^']*)',\s*'([^']*)',\s*([0-9.]*)", row)
            if match:
                nama_obat = match.group(1).strip()
                harga = float(match.group(2).strip())
                deskripsi = match.group(3).strip()
                aturan_pakai = match.group(4).strip()
                stok = float(match.group(5).strip())
                
                # Buat obat baru
                Obat.objects.create(
                    nama_obat=nama_obat,
                    harga=harga,
                    deskripsi=deskripsi,
                    aturan_pakai=aturan_pakai,
                    stok=stok
                )
                count += 1
                print(f"Berhasil mengimpor: {nama_obat}")
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"Berhasil mengimpor {count} data obat")
    print(f"Total obat dalam database: {Obat.objects.count()}")

if __name__ == "__main__":
    import_data()
