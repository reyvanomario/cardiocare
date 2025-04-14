from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from . import views


from django.shortcuts import redirect

def home(request):
    return redirect('beli_obat:katalog_obat')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('beli-obat/', include('beli_obat.urls')),
    path('cari-konsultasi/', include('book_konsultasi.urls', namespace='book_konsultasi')),
    path('kuota/', include('update_kuota.urls')),

]