from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "user", "status", "budget", "end_date", "created_at")
    list_filter = ("user", "status", "created_at", "end_date")
    search_fields = ("name", "client__name", "description")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Základní info",
            {
                "fields": ("user", "client", "name", "status"),
            },
        ),
        (
            "Popis",
            {
                "fields": ("description",),
            },
        ),
        (
            "Rozpočet a čas",
            {
                "fields": ("budget", "estimated_hours", "start_date", "end_date"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
