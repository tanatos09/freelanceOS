from django.urls import path

from . import views

app_name = "workcommits"

urlpatterns = [
    path("", views.workcommit_list, name="list"),
    path("running/", views.workcommit_running, name="running"),
    path("start/", views.workcommit_start, name="start"),
    path("<int:pk>/", views.workcommit_detail, name="detail"),
    path("<int:pk>/commit/", views.workcommit_commit, name="commit"),
    path("<int:pk>/stop/", views.workcommit_stop, name="stop"),
]
