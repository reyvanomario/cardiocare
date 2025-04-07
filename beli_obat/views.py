from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import psycopg2
import os
import csv
from .models import Obat

import jwt
import requests
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

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

def validate_jwt_and_get_user(token):
    try:
        public_key_response = requests.get('http://django-auth:8000/api/get-public-key/')
        public_key_response.raise_for_status()
        public_key = public_key_response.json()['public_key']

        
        
        if not public_key:
            return None, HttpResponseForbidden("Invalid auth service response")
        
        token_bytes = token.encode('utf-8')

        # 2. Decode & validasi JWT
        try:
            payload = jwt.decode(token_bytes, public_key, algorithms=['RS256'])
        except jwt.ExpiredSignatureError:
            return HttpResponseForbidden("Token telah kedaluwarsa. Silakan login kembali.")
        except jwt.InvalidTokenError:
            return HttpResponseForbidden("Token tidak valid. Silakan login.")

        # 3. Cek user 
        try:
            user_response = requests.get(
                f'http://django-auth:8000/api/user/',
                cookies={'jwt': token}
            )
            user_data = user_response.json()
            return user_data, None
        except Exception as e:
            return None, HttpResponseForbidden("User tidak terdaftar di sistem")

    except requests.exceptions.RequestException as e:
        return None, HttpResponseForbidden(f"Gagal terhubung ke auth service: {str(e)}")
    
    except ExpiredSignatureError:
        return None, HttpResponseForbidden("Sesi telah berakhir. Silakan login kembali.")
    
    except InvalidTokenError as e:
        return None, HttpResponseForbidden(f"Token tidak valid: {str(e)}")

def show_page_obat(request):
    token = request.COOKIES.get('jwt')

    if token is None:
        return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")

    user, error = validate_jwt_and_get_user(token)
    if error:
        return error
    
    list_obat = Obat.objects.all()
    context = {'list_obat': list_obat, 'user_data': user}

    return render(request, "tes-page-obat.html", context)
    
   
def logout_view(request):
    response = HttpResponseRedirect(reverse('login'))
    response.delete_cookie('jwt')  # Hapus cookie JWT
    return response
    
    



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
