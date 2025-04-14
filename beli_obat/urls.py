from django.urls import path
from . import views

app_name = 'beli_obat'

urlpatterns = [
    path('katalog/', views.katalog_obat, name='katalog_obat'),
    path('obat/<int:obat_id>/', views.detail_obat, name='detail_obat'),
]