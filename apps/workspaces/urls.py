from django.urls import path

from . import views

app_name = "workspaces"

urlpatterns = [
    path("", views.workspace_list, name="workspace-list"),
    path("<uuid:pk>/", views.workspace_detail, name="workspace-detail"),
    path("<uuid:pk>/members/", views.workspace_members, name="workspace-members"),
]
