from django.urls import path
from . import views
from update_kuota.views import update_kuota_dokter


app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    # URL lain yang mungkin ada
    path('update-kuota/', update_kuota_dokter, name='update_kuota_dokter')

]