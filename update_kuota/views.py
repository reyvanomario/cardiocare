from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from book_konsultasi.models import JadwalKonsultasi, Dokter, RumahSakit
from django.contrib import messages
from django.urls import reverse
from beli_obat.views import validate_jwt_and_get_user

def list_dokter(request):
    token = request.COOKIES.get('jwt')
    user = None
    is_superuser = False

    if token:
        user, error = validate_jwt_and_get_user(token)
        if user and not error:
            is_superuser = user.is_superuser
    
    jadwals = JadwalKonsultasi.objects.select_related('dokter__rumah_sakit').order_by('dokter__rumah_sakit__nama_rumah_sakit')

    dokter_by_rs = defaultdict(list)

    for jadwal in jadwals:
        rumah_sakit = jadwal.dokter.rumah_sakit
        dokter_by_rs[rumah_sakit].append(jadwal)

    context = {
        'dokter_by_rs': dict(dokter_by_rs),
        'user': user
    }
    return render(request, 'list_dokter.html', context)

def update_kuota(request, id_dokter):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        is_authenticated = False
        context = {'is_authenticated': is_authenticated}
        return render(request, 'home.html', context)
    else:
        is_authenticated = True
        user, error = validate_jwt_and_get_user(token)

        if error:
            return error
        
        # Cek apakah user adalah superuser
        if not user.is_superuser:
            messages.error(request, "Anda tidak memiliki izin untuk mengupdate kuota dokter.")
            return redirect(reverse('update_kuota:list_dokter'))
        
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