from django.urls import path
from .views import list_rumah_sakit, view_dokter, list_dokter, BookKonsultasiView, KonsultasiSayaView, CheckAuthStatusView

app_name = 'book_konsultasi'

urlpatterns = [
    path('', list_rumah_sakit, name='list_rumah_sakit'),
    path('<uuid:id_dokter>/', view_dokter, name='view_dokter'),
    path('list-dokter/<uuid:id_rumah_sakit>/', list_dokter, name='list_dokter'),
    path('book-konsultasi/<uuid:id_jadwal>/', BookKonsultasiView.as_view(), name='book_konsultasi'),
    path('konsultasi-saya/', KonsultasiSayaView.as_view(), name='konsultasi_saya'),
    path('check-jwt/', CheckAuthStatusView.as_view(), name='check-auth-status'),
]