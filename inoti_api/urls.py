from django.contrib import admin
from django.urls import path, include, re_path
from . import views



urlpatterns = [
    path("", views.index),
    path('admin/', admin.site.urls),
    path('api/',include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

