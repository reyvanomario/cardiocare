from django.http import HttpResponse
from django.shortcuts import render
import psycopg2
import os
import csv
from .models import Obat

def test_view(request):
    con = psycopg2.connect(
        host = os.getenv('DB_HOST'),
        database = os.getenv('DB_NAME'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD') 
    )

    cur = con.cursor()

    # cur.execute("SELECT current_database();")
    # current_db = cur.fetchone()[0]
    # print("Connected to database:", current_db)

    cur.execute("SELECT * FROM public.obat")

    rows = cur.fetchall()

    for r in rows:
        print("nama obat: " + r[1])


    con.close()

    return HttpResponse("Data obat berhasil diambil.")


def show_page_obat(request):
    list_obat = Obat.objects.all()
    context = {'list_obat': list_obat}

    return render(request, "tes-page-obat.html", context)



def import_csv_data():
    with open('dataset obat.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Obat.objects.create(
                nama_obat=row['nama_obat'],          
                harga=row['harga'],
                deskripsi=row['deskripsi'],
                aturan_pakai=row['aturan_pakai'],
                stok=row['stok']
            )

if __name__ == '__main__':
    import_csv_data()
