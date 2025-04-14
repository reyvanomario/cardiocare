from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from book_konsultasi.models import JadwalKonsultasi, Dokter, RumahSakit
from django.contrib import messages
from django.urls import reverse

def list_dokter(request):
    jadwals = JadwalKonsultasi.objects.select_related('dokter__rumah_sakit').order_by('dokter__rumah_sakit__nama_rumah_sakit')

    dokter_by_rs = defaultdict(list)

    for jadwal in jadwals:
        rumah_sakit = jadwal.dokter.rumah_sakit
        dokter_by_rs[rumah_sakit].append(jadwal)

    context = {
        'dokter_by_rs': dict(dokter_by_rs)  
    }
    return render(request, 'list_dokter.html', context)

def update_kuota(request, id_dokter):
    jadwal = get_object_or_404(JadwalKonsultasi, dokter__id_dokter=id_dokter)

    if request.method == 'POST':
        new_kuota = request.POST.get('kuota')
        if new_kuota and new_kuota.isdigit():
            kuota_int = int(new_kuota)
            if kuota_int >= 0:
                jadwal.kuota = kuota_int
                jadwal.save()
                messages.success(request, f"Kuota untuk Dr. {jadwal.dokter.nama_dokter} berhasil diperbarui.")
        return redirect(reverse('update_kuota:list_dokter'))

    return redirect(reverse('update_kuota:list_dokter'))