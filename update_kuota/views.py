from django.shortcuts import render, get_object_or_404, redirect
from .models import Dokter  
from .forms import UpdateKuotaDokterForm

def update_kuota(request):
    daftar_dokter = Dokter.objects.all()  # Ambil semua dokter

    if request.method == 'POST':
        selected_dokters = request.POST.getlist('dokter')  # Ambil dokter yang dipilih
        for dokter_id in selected_dokters:
            dokter = Dokter.objects.get(id=dokter_id)
            dokter.kuota += 1  # Contoh logika update (misalnya nambah kuota)
            dokter.save()

        return render(request, 'update_kuota/update_kuota_success.html')

    return render(request, 'update_kuota/update_kuota.html', {'daftar_dokter': daftar_dokter})

def update_kuota_dokter(request, id_dokter):
    dokter = get_object_or_404(Dokter, id_dokter=id_dokter)

    if request.method == 'POST':
        form = UpdateKuotaDokterForm(request.POST, instance=dokter)
        if form.is_valid():
            form.save()
            return redirect('update_kuota_success') 
    else:
        form = UpdateKuotaDokterForm(instance=dokter)

    return render(request, 'update_kuota/update.html', {'form': form, 'dokter': dokter})
