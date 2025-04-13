from django.urls import path
from . import views

app_name = 'update_kuota'

urlpatterns = [
    path('dokter/', views.list_dokter, name='list_dokter'),
    path('dokter/<uuid:id_dokter>/update/', views.update_kuota, name='update_kuota'),
]
