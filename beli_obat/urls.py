from django.urls import path
from beli_obat.views import test_view, show_page_obat, show_checkout_page, checkout_obat, otp_view, verify_otp

from . import views

app_name = 'beli_obat'

urlpatterns = [
    path('test-view/', test_view, name='test-view'),
    path('show-page-obat/', show_page_obat, name='show-page-obat'),
    path('katalog/', views.katalog_obat, name='katalog_obat'),
    path('obat/<uuid:obat_id>/', views.detail_obat, name='detail_obat'),
    path('checkout-page/<uuid:obat_id>/', show_checkout_page, name='checkout-page'),
    path('checkout-obat/<uuid:obat_id>/<int:quantity>/', checkout_obat, name='checkout-obat'),
    path('otp/', otp_view, name='otp_view'),
    path('verify-otp/', verify_otp, name='verify_otp'),
]