# views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Obat
from django.core.paginator import Paginator

def katalog_obat(request):
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
    }
    
    return render(request, 'katalog.html', context)

def detail_obat(request, obat_id):
    obat = get_object_or_404(Obat, id=obat_id)
    # Tambahkan print untuk debugging
    print(f"Obat: {obat.nama_obat}")
    print(f"Aturan Pakai: {obat.aturan_pakai}")
    return render(request, 'detail_obat.html', {'obat': obat})