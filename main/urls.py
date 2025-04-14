from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('artikel/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article1.html', views.article1, name='article1'),
    path('article2.html', views.article2, name='article2'),
    path('article3.html', views.article3, name='article3'),
    path('article4.html', views.article4, name='article4'),
    path('article5.html', views.article5, name='article5'),
]