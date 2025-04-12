import csv
from django.core.management.base import BaseCommand
from datetime import datetime
from book_konsultasi.models import RumahSakit, Dokter, JadwalKonsultasi


class Command(BaseCommand):
    help = 'Load hospital, doctor, and schedule data from CSV into the database'

    def handle(self, *args, **kwargs):
        # Paths to the CSV files
        dokter_file_path = 'dataset/dokter.csv'  # Doctor data
        rumah_sakit_file_path = 'dataset/rs.csv'  # Hospital data
        jadwal_konsultasi_file_path = 'dataset/jadwal.csv'  # Schedule data

        # Load RumahSakit data
        rumah_sakit_data = {}
        with open(rumah_sakit_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                nama_rumah_sakit, alamat_rumah_sakit, no_telp = row
                rumah_sakit, created = RumahSakit.objects.get_or_create(
                    nama_rumah_sakit=nama_rumah_sakit.strip(),
                    alamat_rumah_sakit=alamat_rumah_sakit.strip(),
                    no_telp=no_telp.strip()
                )
                rumah_sakit_data[nama_rumah_sakit.strip()] = rumah_sakit

        # Load Dokter data
        dokter_data = {}
        with open(dokter_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                rumah_sakit_name = row[0].strip()  # First column is 'nama_rumah_sakit'
                dokter_name = row[1].strip()  # Second column is 'nama_dokter'
                print(f"Looking for hospital: {rumah_sakit_name}")  # Debugging

                if rumah_sakit_name in rumah_sakit_data:
                    rumah_sakit = rumah_sakit_data[rumah_sakit_name]

                    # Create Dokter
                    dokter, created = Dokter.objects.get_or_create(
                        nama_dokter=dokter_name,
                        rumah_sakit=rumah_sakit
                    )
                    dokter_data[dokter_name] = dokter
                else:
                    self.stdout.write(self.style.ERROR(f"Rumah Sakit {rumah_sakit_name} not found"))

        # Load JadwalKonsultasi data
        with open(jadwal_konsultasi_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                dokter_name = row[0].strip()
                if dokter_name in dokter_data:
                    dokter = dokter_data[dokter_name]

                    # Parse the schedule data
                    try:
                        hari = row[1].strip()
                        waktu = row[2].strip()
                        kuota = int(row[3].strip())

                        # Split the schedule data into day and time
                        start_time, end_time = waktu.split('-')

                        # Replace '.' with ':' in the time strings
                        start_time = start_time.replace('.', ':').strip()
                        end_time = end_time.replace('.', ':').strip()

                        # Parse the time strings
                        start_time = datetime.strptime(start_time, "%H:%M").time()
                        end_time = datetime.strptime(end_time, "%H:%M").time()


                        # Create JadwalKonsultasi
                        jadwal, created = JadwalKonsultasi.objects.get_or_create(
                            dokter=dokter,
                            hari=hari,
                            jam_mulai=start_time,
                            jam_selesai=end_time,
                            kuota=kuota
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error in schedule format for {dokter_name}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Doctor {dokter_name} not found"))

        self.stdout.write(self.style.SUCCESS('Hospital, doctor, and schedule data loaded successfully'))