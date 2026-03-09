"""
Factory Boy factories pro generování testovacích dat.

Tyto factories se používají v testech pro snadné vytváření objektů
s realistickými daty.
"""

from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model

from clients.models import Client
from projects.models import Project

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory pro vytváření testovacích uživatelů."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Nastavi heslo."""
        if create:
            password = extracted or "testpass123"
            obj.set_password(password)
            obj.save()


class ClientFactory(factory.django.DjangoModelFactory):
    """Factory pro vytváření testovacích klientů."""

    class Meta:
        model = Client

    user = factory.SubFactory(UserFactory)
    workspace = None
    name = factory.Faker("company")
    email = factory.Faker("email")
    phone = factory.Faker("numerify", text="+##########")  # max 12 chars, fits max_length=20
    company = factory.Faker("company")
    notes = factory.Faker("text", max_nb_chars=200)


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory pro vytváření testovacích projektů."""

    class Meta:
        model = Project

    user = factory.SubFactory(UserFactory)
    workspace = None
    client = factory.SubFactory(ClientFactory, user=factory.SelfAttribute("..user"))
    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph", nb_sentences=3)
    status = "draft"
    budget = factory.Faker("pyint", min_value=100, max_value=50000)
    estimated_hours = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, min_value=1, max_value=500
    )
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
