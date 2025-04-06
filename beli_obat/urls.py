from django.urls import path
from beli_obat.views import test_view, show_page_obat, logout_view


app_name = 'beli_obat'

urlpatterns = [
    path('test-view/', test_view, name='test-view'),
    path('show-page-obat/', show_page_obat, name='show-page-obat'),
    path('logout/', logout_view, name='logout')
]