from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    # ─── REST API v1 ──────────────────────────────────────────────────────
    path("api/v1/auth/", include("users.urls", namespace="users")),
    path("api/v1/clients/", include("clients.urls", namespace="clients")),
    path("api/v1/projects/", include("projects.urls", namespace="projects")),
    path("api/v1/workspaces/", include("apps.workspaces.urls", namespace="workspaces")),
    path("api/v1/", include("core.api_urls", namespace="core")),
    # Jednoduchý frontend (Django templates)
    path("", RedirectView.as_view(url="/accounts/login/", permanent=False)),
    path("accounts/", include("users.template_urls")),
]
