from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('api/', include('api.urls')),
    re_path("^.*$", views.index)
]