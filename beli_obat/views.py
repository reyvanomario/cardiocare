from uuid import UUID
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
import psycopg2
import os
import csv
from .models import Obat, TransaksiPembelianObat

import jwt
import requests
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

import pyotp
from datetime import datetime, timedelta
from django.utils.html import strip_tags

from django.core.mail import send_mail
from django.template.loader import render_to_string



# views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Obat
from django.core.paginator import Paginator
from django.contrib import messages

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
        public_key_response = requests.get('http://cardiocare-auth-backend.kelompok-38-ns.svc.cluster.local/api/get-public-key/')
        public_key_response.raise_for_status()
        public_key = public_key_response.json()['public_key']

        
        
        if not public_key:
            return None, HttpResponseForbidden("Invalid auth service response")
        
        token_bytes = token.encode('utf-8')

        # 2. Decode & validasi JWT
        try:
            payload = jwt.decode(token_bytes, public_key, algorithms=['RS256'])
        except jwt.ExpiredSignatureError:
            return None, HttpResponseForbidden("Token telah kedaluwarsa. Silakan login kembali.")
        except jwt.InvalidTokenError:
            return None, HttpResponseForbidden("Token tidak valid. Silakan login.")

        # 3. Cek user 
        try:
            user_response = requests.get(
                f'http://cardiocare-auth-backend.kelompok-38-ns.svc.cluster.local/api/user/',
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


def katalog_obat(request):
    is_authenticated = False

    token = request.COOKIES.get('jwt')

    if token is None:
        user = None
    else:
        user, error = validate_jwt_and_get_user(token)
        is_authenticated = True

        if error:
            return error

    
    # Mulai dengan semua obat
    obat_query = Obat.objects.all()
    
    # Filter berdasarkan pencarian
    q = request.GET.get('q')
    if q:
        obat_query = obat_query.filter(
            Q(nama_obat__icontains=q) | 
            Q(deskripsi__icontains=q)
        )
    
    # Pengurutan
    sort = request.GET.get('sort', 'name-asc')
    if sort == 'name-asc':
        obat_query = obat_query.order_by('nama_obat')
    elif sort == 'name-desc':
        obat_query = obat_query.order_by('-nama_obat')
    elif sort == 'price-asc':
        obat_query = obat_query.order_by('harga')
    elif sort == 'price-desc':
        obat_query = obat_query.order_by('-harga')
    
    # Pagination
    paginator = Paginator(obat_query, 8)  # 8 obat per halaman
    page_number = request.GET.get('page')
    obat_list = paginator.get_page(page_number)
    
    context = {
        'obat_list': obat_list,
        'current_query': q,
        'current_sort': sort,
        'is_authenticated': is_authenticated,
        'user': user
    }
    
    return render(request, 'katalog.html', context)

def detail_obat(request, obat_id):
    is_authenticated = False

    token = request.COOKIES.get('jwt')

    if token is None:
        user = None
    else:
        user, error = validate_jwt_and_get_user(token)
        is_authenticated = True

        if error:
            return error
        
    obat = get_object_or_404(Obat, id=obat_id)


    context = {'obat': obat, 'is_authenticated': is_authenticated, 'user': user}

    return render(request, 'detail_obat.html', context)


def show_checkout_page(request, obat_id):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        next_url = request.build_absolute_uri()  # Contoh: http://localhost:8000/checkout-page/...
        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/?next={next_url}"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    
    obat = get_object_or_404(Obat, id=obat_id)

    context = {'obat': obat, 'user':user, 'is_authenticated': True}

    return render(request, 'checkout_page.html', context)


def checkout_obat(request, obat_id, quantity):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        next_url = request.build_absolute_uri()  # Contoh: http://localhost:8000/checkout-page/...
        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/?next={next_url}"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    
    obat_dipilih = get_object_or_404(Obat, id=obat_id)
    total_biaya = obat_dipilih.harga * quantity
    
    
    request.session['pending_transaction'] = {
        'obat_id': str(obat_id),
        'quantity': quantity,
        'total_biaya': total_biaya,
    }

    return HttpResponseRedirect(reverse('beli_obat:otp_view'))




def otp_view(request):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")

        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    
    # Cek apakah ada transaksi pending
    pending_transaction = request.session.get('pending_transaction')
    if not pending_transaction:
        return HttpResponseRedirect(reverse('beli_obat:katalog_obat'))
    

    obat_id = UUID(pending_transaction['obat_id'])

    obat_dipilih = get_object_or_404(Obat, id=obat_id)

    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_time = datetime.now() + timedelta(minutes=5)
    request.session['otp_valid_time'] = str(valid_time)


    subject = 'Kode OTP Anda'
    html_message = render_to_string('otp_email.html', {
        'otp': otp,
        'username': user['username'],
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        'settings.EMAIL_HOST_USER',  # Email pengirim
        [user['email']],  # Email penerima
        html_message=html_message,
    )

    context = {'obat': obat_dipilih, 'user_email': user['email'], 'is_authenticated': True, 'user': user} 

    return render(request, 'otp.html', context)



def verify_otp(request):
    if request.method == 'POST':
        token = request.COOKIES.get('jwt')

        if token is None:
            # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")

            login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/"
            return HttpResponseRedirect(login_url)

        user, error = validate_jwt_and_get_user(token)

        if error:
            return error
        

        user_otp = ''.join([
            request.POST.get('otp1', ''),
            request.POST.get('otp2', ''),
            request.POST.get('otp3', ''),
            request.POST.get('otp4', ''),
            request.POST.get('otp5', ''),
            request.POST.get('otp6', '')
        ])

        if len(user_otp) != 6:
            messages.error(request, 'OTP harus 6 digit. Kode terbaru sudah dikirim.')
            return redirect('beli_obat:otp_view')


        pending_transaction = request.session.get('pending_transaction')
        otp_secret = request.session.get('otp_secret_key')
        otp_valid_time = datetime.fromisoformat(request.session.get('otp_valid_time'))

        if datetime.now() > otp_valid_time:
            messages.error(request, 'OTP telah kedaluwarsa.')
            return HttpResponseRedirect(reverse('beli_obat:otp_view'))

        totp = pyotp.TOTP(otp_secret, interval=60)
        if totp.verify(user_otp, valid_window=1):
            # Simpan transaksi ke database
            obat_id = UUID(pending_transaction['obat_id'])
            obat_dipilih = get_object_or_404(Obat, id=obat_id)
            TransaksiPembelianObat.objects.create(
                user_id=user['id'],
                obat=obat_dipilih,
                quantity=pending_transaction['quantity'],
                total_biaya=pending_transaction['total_biaya']
            )

            obat_dipilih.stok -= pending_transaction['quantity']
            obat_dipilih.save()

            # Hapus data session
            del request.session['pending_transaction']
            del request.session['otp_secret_key']
            del request.session['otp_valid_time']
            messages.success(request, 'Pembelian berhasil!')
            return HttpResponseRedirect(reverse('main:home'))
        else:
            messages.error(request, 'OTP tidak valid. Kode terbaru sudah dikirim.')
            return HttpResponseRedirect(reverse('beli_obat:otp_view'))
    return HttpResponseRedirect(reverse('beli_obat:otp_view'))


def view_riwayat_pembelian_obat(request):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        next_url = request.build_absolute_uri()  # Contoh: http://localhost:8000/checkout-page/...
        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/?next={next_url}"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    


    list_transaksi = TransaksiPembelianObat.objects.filter(user_id=UUID(user['id'])).order_by('-waktu_transaksi')
    
    context = {
        'list_transaksi': list_transaksi,
        'is_authenticated': True,
        'user': user
    }

    return render(request, 'riwayat_pembelian_obat.html', context)



