from django.db.models import Q
from .models import Client


class ClientService:
    """Business layer - všechna obchodní logika pro klienty."""

    @staticmethod
    def get_user_clients(user, search_query=None, workspace=None):
        """Vrátí všechny klienty uživatele (s vyhledáváním).

        If workspace is provided, filters by workspace (multi-tenant).
        Otherwise, falls back to user-based filtering (backward compat).
        """
        if workspace:
            clients = Client.objects.filter(workspace=workspace)
        else:
            clients = Client.objects.filter(user=user)

        if search_query:
            clients = clients.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(company__icontains=search_query)
            )

        return clients

    @staticmethod
    def create_client(user, workspace=None, **kwargs):
        """Vytvoří a vrátí nového klienta."""
        return Client.objects.create(user=user, workspace=workspace, **kwargs)

    @staticmethod
    def update_client(client, **kwargs):
        """Edituje klienta bez změny user a workspace pole."""
        for key, value in kwargs.items():
            if key not in ("user", "workspace"):
                setattr(client, key, value)
        client.save()
        return client

    @staticmethod
    def delete_client(client):
        """Smaže klienta."""
        client.delete()

    @staticmethod
    def get_client_detail(user, client_id, workspace=None):
        """Vrátí detail klienta (ověří ownership)."""
        try:
            filters = {"id": client_id}
            if workspace:
                filters["workspace"] = workspace
            else:
                filters["user"] = user
            return Client.objects.get(**filters)
        except Client.DoesNotExist:
            return None

    @staticmethod
    def get_client_stats(client):
        """Vrátí statistiky klienta."""
        return {
            "total_earnings": client.total_earnings(),
            "project_count": client.project_count(),
        }
