from django.urls import path

from . import template_views

urlpatterns = [
    path("login/", template_views.login_page, name="login"),
    path("register/", template_views.register_page, name="register"),
    path("dashboard/", template_views.dashboard_page, name="dashboard"),
    path("clients/", template_views.clients_page, name="clients"),
    path("clients/<int:pk>/", template_views.client_detail_page, name="client_detail"),
    path("projects/", template_views.projects_page, name="projects"),
    path("projects/<int:pk>/", template_views.project_detail_page, name="project_detail"),
    path("timer/", template_views.timer_page, name="timer"),
]
