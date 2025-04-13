from django.shortcuts import render, redirect, get_object_or_404
from .models import Dokter
from .forms import DokterForm

def list_dokter(request):
    dokter_list = Dokter.objects.all()
    return render(request, 'list_dokter.html', {'dokter_list': dokter_list})

def update_kuota(request, id_dokter):
    dokter = get_object_or_404(Dokter, id_dokter=id_dokter)
    
    if request.method == 'POST':
        form = DokterForm(request.POST, instance=dokter)
        if form.is_valid():
            form.save()
            return redirect('update_kuota:list_dokter')
    else:
        form = DokterForm(instance=dokter)
    
    return render(request, 'update_kuota.html', {'form': form, 'dokter': dokter})