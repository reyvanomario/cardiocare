from django.urls import path
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('article1', views.article1, name='article1'),
    path('article2', views.article2, name='article2'),
    path('article3', views.article3, name='article3'),
    path('article4', views.article4, name='article4'),
    path('article5', views.article5, name='article5'),

]