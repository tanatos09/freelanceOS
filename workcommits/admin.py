from django.contrib import admin

from .models import WorkCommit


@admin.register(WorkCommit)
class WorkCommitAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "description", "start_time", "end_time", "duration_seconds", "is_running"]
    list_filter = ["project", "user"]
    search_fields = ["description", "project__name", "user__email"]
    raw_id_fields = ["user", "project"]
    readonly_fields = ["duration_seconds", "created_at"]

    @admin.display(boolean=True)
    def is_running(self, obj):
        return obj.is_running
