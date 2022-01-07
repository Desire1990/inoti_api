from django.contrib import admin
from django.urls import path, include, re_path


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/', swagger_schema_view),
    # path('password-reset/', PasswordResetView.as_view()),
    # path('password-reset-confirm/<slug:uidb64>/<slug:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/',include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
