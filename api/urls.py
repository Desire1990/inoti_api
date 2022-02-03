from django.urls import path, include, re_path
from rest_framework import routers
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView, UserDetailsView


router = routers.DefaultRouter()
router.register("user",UserViewset)
router.register("taux",TauxViewset)
router.register("compte",AccountViewset)
router.register("depot",TransferViewset)
router.register("depense",DepenseViewset)
router.register("approvision",ProvisioningViewset)

app_name='api'

urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
]