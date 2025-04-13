from django.urls import path
from .views import update_kuota_dokter, update_kuota

urlpatterns = [
    path('update-kuota/', update_kuota, name='update_kuota'),
    path('<uuid:id_dokter>/', update_kuota_dokter, name='update_kuota_dokter'),
]
