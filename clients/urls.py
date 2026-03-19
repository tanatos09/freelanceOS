from django.urls import path

from projects.views import client_projects

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.clients_list, name="list-create"),
    path("<int:pk>/", views.client_detail, name="detail"),
    path("<int:pk>/stats/", views.client_stats, name="stats"),
    path("<int:client_id>/projects/", client_projects, name="client-projects"),
]
