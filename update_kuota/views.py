from collections import defaultdict
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from book_konsultasi.models import JadwalKonsultasi, Dokter, RumahSakit
from django.contrib import messages
from django.urls import reverse
from beli_obat.views import validate_jwt_and_get_user

def list_dokter(request):
    is_superuser = False

    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        next_url = request.build_absolute_uri()  # Contoh: http://localhost:8000/checkout-page/...
        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/?next={next_url}"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    
    if user['is_admin'] == True:
        is_superuser = True
    

    
    jadwals = JadwalKonsultasi.objects.select_related('dokter__rumah_sakit').order_by('dokter__rumah_sakit__nama_rumah_sakit')

    dokter_by_rs = defaultdict(list)

    for jadwal in jadwals:
        rumah_sakit = jadwal.dokter.rumah_sakit
        dokter_by_rs[rumah_sakit].append(jadwal)

    context = {
        'dokter_by_rs': dict(dokter_by_rs),
        'user': user,
        'is_superuser': is_superuser
    }
    return render(request, 'list_dokter.html', context)

def update_kuota(request, id_dokter):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        next_url = request.build_absolute_uri()  # Contoh: http://localhost:8000/checkout-page/...
        login_url = f"https://kelompok-38-cardiocare-auth.pkpl.cs.ui.ac.id/login/?next={next_url}"
        return HttpResponseRedirect(login_url)

    user, error = validate_jwt_and_get_user(token)

    if error:
        return error
    
    if user['is_admin'] == False:
        return HttpResponseForbidden("Anda bukan admin.")
        
    jadwal = get_object_or_404(JadwalKonsultasi, dokter__id_dokter=id_dokter)

    if request.method == 'POST':
        new_kuota = request.POST.get('kuota')
        if new_kuota and new_kuota.isdigit():
            kuota_int = int(new_kuota)
            if kuota_int >= 0 and kuota_int < 200:
                jadwal.kuota = kuota_int
                jadwal.save()
                messages.success(request, f"Kuota untuk Dr. {jadwal.dokter.nama_dokter} berhasil diperbarui.")
        return redirect(reverse('update_kuota:list_dokter'))

    return redirect(reverse('update_kuota:list_dokter'))



