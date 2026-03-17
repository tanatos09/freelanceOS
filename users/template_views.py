"""
Jednoduché Django template views pro frontend (login, register, dashboard, clients, projects).
Všechna business logika jde přes REST API (/api/auth/*, /api/clients/*, /api/projects/*).
Tyto views pouze servírují HTML stránky.
"""

from django.shortcuts import render


def login_page(request):
    return render(request, "auth/login.html")


def register_page(request):
    return render(request, "auth/register.html")


def dashboard_page(request):
    return render(request, "auth/dashboard.html")


def clients_page(request):
    return render(request, "dashboard/clients.html")


def projects_page(request):
    return render(request, "dashboard/projects.html")


def timer_page(request):
    return render(request, "dashboard/timer.html")
