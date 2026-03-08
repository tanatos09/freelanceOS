from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from clients.models import Client
from projects.models import Project

User = get_user_model()


class Command(BaseCommand):
    help = "Vytvoří testovací data (user, client, project)"

    def handle(self, *args, **options):
        # Smaž všechna stará testovací data
        User.objects.filter(email="test@example.com").delete()

        # Vytvoř nového test user
        user = User.objects.create_user(
            email="test@example.com", password="test123", is_active=True
        )
        self.stdout.write(self.style.SUCCESS("✓ Uživatel vytvořen: test@example.com / test123"))

        # Vytvoř testovací klient
        client = Client.objects.create(
            user=user,
            name="Acme Corporation",
            email="acme@example.com",
            company="Acme Inc.",
            phone="+420 123 456 789",
            notes="Naš hlavní klient - VIP support",
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Klient vytvořen: {client.name}"))

        # Vytvoř testovací projekt
        project = Project.objects.create(
            user=user,
            client=client,
            name="Website Redesign",
            description="Nový design a frontend webu pro Acme Corp",
            status="active",
            budget=50000.00,
            estimated_hours=200.00,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=60)).date(),
        )
        self.stdout.write(self.style.SUCCESS(f"✓ Projekt vytvořen: {project.name}"))

        # Výstup info pro testování
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 TESTOVACÍ DATA PŘIPRAVENA!"))
        self.stdout.write("=" * 60)
        self.stdout.write("\n📝 Přihlašovací údaje:")
        self.stdout.write("   Email:    test@example.com")
        self.stdout.write("   Heslo:    test123")
        self.stdout.write("\n📋 Testovací data:")
        self.stdout.write(f"   Klient:   {client.name} ({client.email})")
        self.stdout.write(f"   Projekt:  {project.name}")
        self.stdout.write(f"   Rozpočet: {project.budget} CZK")
        self.stdout.write(f"   Hodiny:   {project.estimated_hours}h")
        self.stdout.write(f"   Deadline: {project.end_date}")
        self.stdout.write("\n🚀 Server pokyn:")
        self.stdout.write("   python manage.py runserver")
        self.stdout.write("\n🌐 API pro testování:")
        self.stdout.write("   Login:     POST /api/auth/login/")
        self.stdout.write("   Klienti:   GET /api/clients/")
        self.stdout.write("   Projekty:  GET /api/projects/")
        self.stdout.write("=" * 60 + "\n")
