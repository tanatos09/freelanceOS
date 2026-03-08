from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.projects_list, name="list-create"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("stats/", views.projects_stats, name="stats"),
]
