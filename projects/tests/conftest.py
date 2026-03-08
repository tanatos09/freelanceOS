"""
Lokální fixtures pro aplikaci projects.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from tests.factories import ProjectFactory


@pytest.fixture
def project_data(client_obj):
    """Validní data pro vytvoření projektu."""
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)

    return {
        "name": "Website Redesign",
        "description": "Complete redesign of company website",
        "client": client_obj.id,
        "status": "draft",
        "budget": 5000.00,
        "estimated_hours": 100.00,
        "start_date": start_date,
        "end_date": end_date,
    }


@pytest.fixture
def multiple_projects(user, client_obj):
    """Vytvoří více projektů v různých stavech."""
    return [
        ProjectFactory(user=user, client=client_obj, status="draft"),
        ProjectFactory(user=user, client=client_obj, status="active"),
        ProjectFactory(user=user, client=client_obj, status="active"),
        ProjectFactory(user=user, client=client_obj, status="completed"),
        ProjectFactory(user=user, client=client_obj, status="archived"),
    ]
