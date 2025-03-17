from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('login', views.login),
    re_path('register', views.register),
    re_path('test-token', views.test_token),
    path('', include('main.urls')),
]
