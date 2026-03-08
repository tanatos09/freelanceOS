from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
)
from .services import ProjectService

# ─── List / Create projects ───────────────────────────────────────────────────


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def projects_list(request):
    """
    GET  /api/projects/ - List všech projektů uživatele
    POST /api/projects/ - Vytvoří nový projekt

    Query params:
      - status: draft|active|completed|archived|cancelled
      - client_id: int
      - search: string (hledá v name)
      - overdue: bool (true/false)
    """
    if request.method == "GET":
        filters = {
            "status": request.query_params.get("status"),
            "client_id": request.query_params.get("client_id"),
            "search": request.query_params.get("search"),
            "overdue": request.query_params.get("overdue") == "true",
        }
        # Odeber None values
        filters = {k: v for k, v in filters.items() if v}

        workspace = getattr(request, "workspace", None)
        projects = ProjectService.get_user_projects(request.user, filters, workspace=workspace)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    # POST - Create new project
    serializer = ProjectCreateUpdateSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    try:
        workspace = getattr(request, "workspace", None)
        project = ProjectService.create_project(
            request.user, workspace=workspace, **serializer.validated_data
        )
        return Response(
            ProjectDetailSerializer(project).data,
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─── Retrieve / Update / Delete project ───────────────────────────────────────


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def project_detail(request, pk):
    """
    GET    /api/projects/{id}/ - Detail projektu
    PUT    /api/projects/{id}/ - Editace projektu
    DELETE /api/projects/{id}/ - Smazání projektu
    """
    project = ProjectService.get_project_detail(
        request.user, pk, workspace=getattr(request, "workspace", None)
    )
    if not project:
        return Response(
            {"detail": "Projekt nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = ProjectCreateUpdateSerializer(
            project,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_project = ProjectService.update_project(
                project, request.user, **serializer.validated_data
            )
            return Response(ProjectDetailSerializer(updated_project).data)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif request.method == "DELETE":
        try:
            ProjectService.delete_project(project, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ─── Project stats ────────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def projects_stats(request):
    """
    GET /api/projects/stats/ - Celkové statistiky projektů
    """
    stats = ProjectService.get_project_stats(
        request.user, workspace=getattr(request, "workspace", None)
    )
    return Response(stats)


# ─── Client projects ──────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def client_projects(request, client_id):
    """
    GET /api/clients/{client_id}/projects/ - Všechny projekty klienta
    """
    try:
        from clients.models import Client

        client = Client.objects.get(id=client_id, user=request.user)
    except Exception:
        return Response(
            {"detail": "Klient nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    projects = client.projects.all()
    serializer = ProjectListSerializer(projects, many=True)
    return Response(serializer.data)
