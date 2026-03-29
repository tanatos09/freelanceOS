from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import WorkCommit
from .serializers import WorkCommitSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def workcommit_list(request):
    """
    GET /api/v1/workcommits/
    List work commits for the authenticated user.
    Query params: project (int), date (YYYY-MM-DD)
    """
    qs = WorkCommit.objects.filter(user=request.user).select_related("project")

    project_id = request.query_params.get("project")
    if project_id:
        qs = qs.filter(project_id=project_id)

    date_str = request.query_params.get("date")
    if date_str:
        qs = qs.filter(start_time__date=date_str)

    serializer = WorkCommitSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def workcommit_running(request):
    """
    GET /api/v1/workcommits/running/
    Returns the currently running commit or null.
    """
    commit = (
        WorkCommit.objects.filter(user=request.user, end_time__isnull=True)
        .select_related("project")
        .first()
    )
    if not commit:
        return Response(None)
    return Response(WorkCommitSerializer(commit).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workcommit_start(request):
    """
    POST /api/v1/workcommits/start/
    Body: {"project": <id>}
    Starts a new work timer. Fails if a timer is already running.
    """
    project_id = request.data.get("project")
    if not project_id:
        return Response(
            {"detail": "Pole project je povinné."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # One running timer per user at a time
    already_running = WorkCommit.objects.filter(user=request.user, end_time__isnull=True).exists()
    if already_running:
        return Response(
            {"detail": "Timer již běží. Nejprve ho zastav nebo commitni."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from projects.models import Project

    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Projekt nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    commit = WorkCommit.objects.create(
        user=request.user,
        project=project,
        start_time=timezone.now(),
    )
    return Response(WorkCommitSerializer(commit).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workcommit_commit(request, pk):
    """
    POST /api/v1/workcommits/{pk}/commit/
    Body: {"description": "...", "continue": true/false}
    Finish current segment + optionally start a new one.
    """
    try:
        commit = WorkCommit.objects.select_related("project").get(pk=pk, user=request.user)
    except WorkCommit.DoesNotExist:
        return Response(
            {"detail": "Commit nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not commit.is_running:
        return Response(
            {"detail": "Tento timer již byl dokončen."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    description = request.data.get("description", "")
    tag = request.data.get("tag") or None
    should_continue = bool(request.data.get("continue", False))

    commit.stop(description=description)
    if tag is not None:
        commit.tag = tag
        commit.save(update_fields=["tag"])

    next_commit = None
    if should_continue:
        next_commit = WorkCommit.objects.create(
            user=request.user,
            project=commit.project,
            start_time=timezone.now(),
        )

    next_commit_data = WorkCommitSerializer(next_commit).data if next_commit else None
    return Response(
        {
            "commit": WorkCommitSerializer(commit).data,
            "next_commit": next_commit_data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workcommit_stop(request, pk):
    """
    POST /api/v1/workcommits/{pk}/stop/
    Body: {"description": "..."} (optional)
    Stop timer without continuing.
    """
    try:
        commit = WorkCommit.objects.get(pk=pk, user=request.user)
    except WorkCommit.DoesNotExist:
        return Response(
            {"detail": "Commit nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not commit.is_running:
        return Response(
            {"detail": "Tento timer již byl dokončen."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    description = request.data.get("description", "")
    tag = request.data.get("tag") or None
    commit.stop(description=description)
    if tag is not None:
        commit.tag = tag
        commit.save(update_fields=["tag"])
    return Response(WorkCommitSerializer(commit).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workcommit_pause(request, pk):
    """
    POST /api/v1/workcommits/{pk}/pause/
    Pause the running timer without ending the session.
    """
    try:
        commit = WorkCommit.objects.get(pk=pk, user=request.user)
    except WorkCommit.DoesNotExist:
        return Response({"detail": "Commit nenalezen."}, status=status.HTTP_404_NOT_FOUND)

    if not commit.is_running:
        return Response({"detail": "Timer neběží."}, status=status.HTTP_400_BAD_REQUEST)
    if commit.is_paused:
        return Response({"detail": "Timer je již pozastaven."}, status=status.HTTP_400_BAD_REQUEST)

    commit.pause()
    return Response(WorkCommitSerializer(commit).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workcommit_resume(request, pk):
    """
    POST /api/v1/workcommits/{pk}/resume/
    Resume a previously paused timer.
    """
    try:
        commit = WorkCommit.objects.get(pk=pk, user=request.user)
    except WorkCommit.DoesNotExist:
        return Response({"detail": "Commit nenalezen."}, status=status.HTTP_404_NOT_FOUND)

    if not commit.is_paused:
        return Response({"detail": "Timer není pozastaven."}, status=status.HTTP_400_BAD_REQUEST)

    commit.resume()
    return Response(WorkCommitSerializer(commit).data)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def workcommit_detail(request, pk):
    """
    GET    /api/v1/workcommits/{pk}/ — detail
    PATCH  /api/v1/workcommits/{pk}/ — partial update (description, tag, start_time, end_time, project)
    DELETE /api/v1/workcommits/{pk}/ — delete
    """
    try:
        commit = WorkCommit.objects.select_related("project").get(pk=pk, user=request.user)
    except WorkCommit.DoesNotExist:
        return Response(
            {"detail": "Commit nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        return Response(WorkCommitSerializer(commit).data)

    if request.method == "PATCH":
        # Validate project ownership before serializer runs
        if "project" in request.data:
            from projects.models import Project

            try:
                Project.objects.get(id=request.data["project"], user=request.user)
            except Project.DoesNotExist:
                return Response(
                    {"detail": "Projekt nenalezen."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Disallow clearing end_time on an already-completed commit
        if "end_time" in request.data and not request.data["end_time"] and not commit.is_running:
            return Response(
                {"detail": "Nelze odstranit end_time dokončeného záznamu."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WorkCommitSerializer(commit, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_start = serializer.validated_data.get("start_time", commit.start_time)
        new_end = serializer.validated_data.get("end_time", commit.end_time)
        if new_end and new_start >= new_end:
            return Response(
                {"detail": "end_time musí být po start_time."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = serializer.save()

        # Recalculate duration when times change on a completed commit
        times_changed = (
            "start_time" in serializer.validated_data or "end_time" in serializer.validated_data
        )
        if not instance.is_running and times_changed:
            instance.duration_seconds = max(
                0, int((instance.end_time - instance.start_time).total_seconds())
            )
            instance.save(update_fields=["duration_seconds"])

        return Response(WorkCommitSerializer(instance).data)

    commit.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
