from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'users'

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
    path('change-password/', views.change_password, name='change-password'),
    # JWT refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
