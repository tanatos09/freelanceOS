from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.common.permissions import IsWorkspaceAdmin
from .serializers import (
    WorkspaceSerializer,
    WorkspaceCreateSerializer,
    WorkspaceMembershipSerializer,
)
from .services import WorkspaceService


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def workspace_list(request):
    """
    GET  /api/v1/workspaces/    — List user's workspaces
    POST /api/v1/workspaces/    — Create a new workspace
    """
    if request.method == "GET":
        workspaces = WorkspaceService.get_user_workspaces(request.user)
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    serializer = WorkspaceCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    workspace = WorkspaceService.create_workspace(
        owner=request.user,
        **serializer.validated_data,
    )
    return Response(
        WorkspaceSerializer(workspace).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def workspace_detail(request, pk):
    """
    GET /api/v1/workspaces/{id}/   — Workspace detail
    PUT /api/v1/workspaces/{id}/   — Update workspace
    """
    workspace = WorkspaceService.get_workspace(pk)

    if request.method == "GET":
        return Response(WorkspaceSerializer(workspace).data)

    # Only admin/owner can update
    if not IsWorkspaceAdmin().has_permission(request, None):
        return Response(
            {"detail": "Nemáte oprávnění."},
            status=status.HTTP_403_FORBIDDEN,
        )
    serializer = WorkspaceCreateSerializer(workspace, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(WorkspaceSerializer(workspace).data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def workspace_members(request, pk):
    """
    GET  /api/v1/workspaces/{id}/members/    — List members
    POST /api/v1/workspaces/{id}/members/    — Add member
    """
    workspace = WorkspaceService.get_workspace(pk)

    if request.method == "GET":
        memberships = workspace.memberships.filter(is_active=True).select_related("user")
        serializer = WorkspaceMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    serializer = WorkspaceMembershipSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    membership = WorkspaceService.add_member(
        workspace=workspace,
        user=serializer.validated_data["user"],
        role=serializer.validated_data.get("role", "member"),
    )
    return Response(
        WorkspaceMembershipSerializer(membership).data,
        status=status.HTTP_201_CREATED,
    )
