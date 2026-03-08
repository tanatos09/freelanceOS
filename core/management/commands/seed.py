from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Client, Project, WorkCommit

User = get_user_model()


class Command(BaseCommand):
    help = "Vytvoří testovací data (klienti, projekty, commits)"

    def handle(self, *args, **options):
        # Vytvoř test uživatele
        user, created = User.objects.get_or_create(
            email="frank@test.cz", defaults={"is_staff": True, "is_active": True}
        )
        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS("✓ User frank@test.cz created"))
        else:
            self.stdout.write("○ User frank@test.cz already exists")

        # Vytvoř klienty
        clients_data = [
            {"name": "Web Novák", "email": "novak@example.com", "phone": "+420 777 123 456"},
            {
                "name": "Fotogalerie Svoboda",
                "email": "svoboda@example.com",
                "phone": "+420 777 234 567",
            },
            {"name": "E-shop Kolář", "email": "kolar@example.com", "phone": "+420 777 345 678"},
        ]

        clients = {}
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                user=user,
                name=client_data["name"],
                defaults={"email": client_data["email"], "phone": client_data["phone"]},
            )
            clients[client.name] = client
            status = "✓" if created else "○"
            self.stdout.write(f"{status} Client: {client.name}")

        # Vytvoř projekty
        projects_data = [
            {
                "name": "Redesign webu",
                "client": "Web Novák",
                "rate": 500,
                "status": "in_progress",
                "deadline": timezone.now().date() + timedelta(days=10),
            },
            {
                "name": "Galerie fotek",
                "client": "Fotogalerie Svoboda",
                "rate": 400,
                "status": "new",
                "deadline": timezone.now().date() + timedelta(days=7),
            },
            {
                "name": "Nový e-shop",
                "client": "E-shop Kolář",
                "rate": 600,
                "status": "in_progress",
                "deadline": timezone.now().date() - timedelta(days=2),
            },  # Overdue!
            {
                "name": "Opravy CSS",
                "client": "Web Novák",
                "rate": 300,
                "status": "done",
                "deadline": timezone.now().date() - timedelta(days=5),
            },
        ]

        projects = {}
        for proj_data in projects_data:
            project, created = Project.objects.get_or_create(
                user=user,
                name=proj_data["name"],
                defaults={
                    "client": clients[proj_data["client"]],
                    "rate": proj_data["rate"],
                    "status": proj_data["status"],
                    "deadline": proj_data["deadline"],
                },
            )
            projects[project.name] = project
            status = "✓" if created else "○"
            self.stdout.write(f"{status} Project: {project.name}")

        # Vytvoř pracovní commity
        commits_data = [
            {"project": "Redesign webu", "description": "Oprava CSS navů", "hours": 1.5},
            {"project": "Redesign webu", "description": "Mobilní layout", "hours": 2},
            {"project": "Redesign webu", "description": "Review a feedback", "hours": 0.5},
            {"project": "Galerie fotek", "description": "Setup galerie komponenty", "hours": 3},
            {"project": "Nový e-shop", "description": "Databáze a modely", "hours": 4},
            {"project": "Nový e-shop", "description": "API endpointy", "hours": 3},
            {"project": "Opravy CSS", "description": "Responsive design fixes", "hours": 2},
            {"project": "Opravy CSS", "description": "Testování", "hours": 1},
        ]

        commit_count = 0
        now = timezone.now()
        for commit_data in commits_data:
            project = projects[commit_data["project"]]
            # Rozprostři commity v čase (včera, dneska)
            start = now - timedelta(hours=24 - commit_count)
            end = start + timedelta(hours=commit_data["hours"])

            commit, created = WorkCommit.objects.get_or_create(
                user=user,
                project=project,
                start_time=start,
                defaults={
                    "end_time": end,
                    "description": commit_data["description"],
                },
            )
            if created:
                commit_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✓ Seed data created! {commit_count} commits"))
        self.stdout.write(self.style.SUCCESS("\n🔐 Test login: frank@test.cz / testpass123"))
        self.stdout.write(self.style.SUCCESS("🔗 Admin: http://localhost:8000/admin/"))
