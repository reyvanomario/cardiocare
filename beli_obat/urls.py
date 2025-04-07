from django.urls import path
from beli_obat.views import test_view, show_page_obat, logout_view

from . import views

app_name = 'beli_obat'

urlpatterns = [
    path('test-view/', test_view, name='test-view'),
    path('show-page-obat/', show_page_obat, name='show-page-obat'),
    path('logout/', logout_view, name='logout'),
    path('katalog/', views.katalog_obat, name='katalog_obat'),
    path('obat/<uuid:obat_id>/', views.detail_obat, name='detail_obat'),
]