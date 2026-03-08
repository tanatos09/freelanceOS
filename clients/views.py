from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    ClientListSerializer,
    ClientDetailSerializer,
    ClientCreateUpdateSerializer,
)
from .services import ClientService

# ─── List / Create clients ────────────────────────────────────────────────────


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def clients_list(request):
    """
    GET  /api/clients/ - List všech klientů uživatele
    POST /api/clients/ - Vytvoří nového klienta

    Query:
      - search: hledání v name, email, company
    """
    if request.method == "GET":
        search_query = request.query_params.get("search", None)
        workspace = getattr(request, "workspace", None)
        clients = ClientService.get_user_clients(request.user, search_query, workspace=workspace)
        serializer = ClientListSerializer(clients, many=True)
        return Response(serializer.data)

    # POST - Create new client
    serializer = ClientCreateUpdateSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    workspace = getattr(request, "workspace", None)
    client = ClientService.create_client(
        request.user, workspace=workspace, **serializer.validated_data
    )
    return Response(
        ClientDetailSerializer(client).data,
        status=status.HTTP_201_CREATED,
    )


# ─── Retrieve / Update / Delete client ─────────────────────────────────────────


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def client_detail(request, pk):
    """
    GET    /api/clients/{id}/ - Detail klienta
    PUT    /api/clients/{id}/ - Editace klienta
    DELETE /api/clients/{id}/ - Smazání klienta
    """
    client = ClientService.get_client_detail(
        request.user, pk, workspace=getattr(request, "workspace", None)
    )
    if not client:
        return Response(
            {"detail": "Klient nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = ClientDetailSerializer(client)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = ClientCreateUpdateSerializer(
            client,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_client = ClientService.update_client(client, **serializer.validated_data)
        return Response(ClientDetailSerializer(updated_client).data)

    elif request.method == "DELETE":
        ClientService.delete_client(client)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Client stats ─────────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def client_stats(request, pk):
    """
    GET /api/clients/{id}/stats/ - Statistiky klienta
    """
    client = ClientService.get_client_detail(
        request.user, pk, workspace=getattr(request, "workspace", None)
    )
    if not client:
        return Response(
            {"detail": "Klient nenalezen."},
            status=status.HTTP_404_NOT_FOUND,
        )

    stats = ClientService.get_client_stats(client)
    return Response(stats)
