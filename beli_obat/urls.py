from django.urls import path
from beli_obat.views import test_view, show_page_obat


app_name = 'beli_obat'

urlpatterns = [
    path('test-view/', test_view, name='test-view'),
    path('show-page-obat/', show_page_obat, name='show-page-obat')
]