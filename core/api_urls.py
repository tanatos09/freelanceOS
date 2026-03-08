from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]

