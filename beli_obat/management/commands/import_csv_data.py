# beli_obat/management/commands/import_data_obat.py
from django.core.management.base import BaseCommand
import csv
from beli_obat.models import Obat
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import data obat dari CSV'

    def handle(self, *args, **options):
        csv_path = 'dataset_obat.csv'  # Path di dalam container
        
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Obat.objects.create(
                    nama_obat=row['nama_obat'],
                    harga=Decimal(row['harga']),  # Konversi ke Decimal
                    deskripsi=row['deskripsi'],
                    aturan_pakai=row['aturan_pakai'],
                    stok=int(row['stok'])  # Konversi ke integer
                )