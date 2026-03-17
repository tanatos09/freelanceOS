from django.urls import path

from . import template_views

urlpatterns = [
    path("login/", template_views.login_page, name="login"),
    path("register/", template_views.register_page, name="register"),
    path("dashboard/", template_views.dashboard_page, name="dashboard"),
    path("clients/", template_views.clients_page, name="clients"),
    path("projects/", template_views.projects_page, name="projects"),
    path("timer/", template_views.timer_page, name="timer"),
]
