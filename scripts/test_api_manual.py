#!/usr/bin/env python
"""
Test script pro API testing - vytvoří projekt a zaloguje uživatele
Spuštění: python test_api.py
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _print_response(self, title: str, status: int, data: dict, success: bool = True):
        """Pretty print API response."""
        color = "\033[92m" if success else "\033[91m"  # Green or Red
        reset = "\033[0m"
        
        print(f"\n{color}{'='*60}")
        print(f"✓ {title}" if success else f"✗ {title}")
        print(f"Status: {status}{reset}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"{color}{'='*60}{reset}\n")
    
    def login(self, email: str, password: str) -> bool:
        """Login a získej JWT token."""
        print(f"\n🔐 Přihlášení: {email}")
        
        url = f"{self.base_url}/api/v1/auth/login/"
        payload = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access")
                self.headers["Authorization"] = f"Bearer {self.token}"
                
                self._print_response(
                    "Login úspěšný",
                    response.status_code,
                    {"email": email, "token": self.token[:20] + "..."},
                    success=True
                )
                return True
            else:
                self._print_response(
                    "Login selhal",
                    response.status_code,
                    response.json(),
                    success=False
                )
                return False
        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            return False
    
    def get_clients(self) -> Optional[list]:
        """Vrátí seznam klientů."""
        print(f"\n📋 Načítám klienty...")
        
        if not self.token:
            print("❌ Nejdřív se musíš přihlásit!")
            return None
        
        url = f"{self.base_url}/api/v1/clients/"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data if isinstance(data, list) else data.get("results", [])
                
                self._print_response(
                    f"Klienti načteni ({len(clients)})",
                    response.status_code,
                    {"count": len(clients), "clients": clients},
                    success=True
                )
                return clients
            else:
                self._print_response(
                    "Načtení klientů selhalo",
                    response.status_code,
                    response.json(),
                    success=False
                )
                return None
        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            return None
    
    def get_projects(self) -> Optional[list]:
        """Vrátí seznam projektů."""
        print(f"\n📁 Načítám projekty...")
        
        if not self.token:
            print("❌ Nejdřív se musíš přihlásit!")
            return None
        
        url = f"{self.base_url}/api/v1/projects/"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                projects = data if isinstance(data, list) else data.get("results", [])
                
                self._print_response(
                    f"Projekty načteny ({len(projects)})",
                    response.status_code,
                    {"count": len(projects), "projects": projects},
                    success=True
                )
                return projects
            else:
                self._print_response(
                    "Načtení projektů selhalo",
                    response.status_code,
                    response.json(),
                    success=False
                )
                return None
        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            return None
    
    def create_project(self, client_id: int, name: str, budget: float, hours: float) -> Optional[dict]:
        """Vytvoří nový projekt."""
        print(f"\n✏️  Vytvářím projekt: {name}")
        
        if not self.token:
            print("❌ Nejdřív se musíš přihlásit!")
            return None
        
        url = f"{self.base_url}/api/v1/projects/"
        payload = {
            "name": name,
            "description": f"Test projekt {name}",
            "client": client_id,
            "status": "active",
            "budget": budget,
            "estimated_hours": hours,
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code == 201:
                data = response.json()
                self._print_response(
                    f"Projekt vytvořen: {name}",
                    response.status_code,
                    data,
                    success=True
                )
                return data
            else:
                self._print_response(
                    "Vytvoření projektu selhalo",
                    response.status_code,
                    response.json(),
                    success=False
                )
                return None
        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            return None
    
    def get_project_detail(self, project_id: int) -> Optional[dict]:
        """Vrátí detail projektu s calculovanými poli."""
        print(f"\n🔍 Načítám detail projektu #{project_id}...")
        
        if not self.token:
            print("❌ Nejdřív se musíš přihlásit!")
            return None
        
        url = f"{self.base_url}/api/v1/projects/{project_id}/"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self._print_response(
                    f"Detail projektu {data.get('name')}",
                    response.status_code,
                    data,
                    success=True
                )
                return data
            else:
                self._print_response(
                    "Načtení detailu selhalo",
                    response.status_code,
                    response.json(),
                    success=False
                )
                return None
        except Exception as e:
            print(f"❌ Chyba: {str(e)}")
            return None


def main():
    """Main test flow."""
    print("\n" + "="*60)
    print("🚀 FreelanceOS API Test")
    print("="*60)
    
    tester = APITester()
    
    # 1. Login
    if not tester.login("test@example.com", "test123"):
        print("❌ Login fail - nemůžu pokračovat")
        return
    
    # 2. List clients
    clients = tester.get_clients()
    if not clients or len(clients) == 0:
        print("❌ Žádní klienti - nemůžu pokračovat")
        return
    
    client_id = clients[0]["id"]
    print(f"\n✓ Vybrán klient: {clients[0]['name']} (ID: {client_id})")
    
    # 3. List projects
    tester.get_projects()
    
    # 4. Create new project
    new_project = tester.create_project(
        client_id=client_id,
        name="Mobile App Development",
        budget=75000.00,
        hours=300.00
    )
    
    if new_project:
        project_id = new_project["id"]
        
        # 5. Get project detail
        tester.get_project_detail(project_id)
        
        # 6. List projects (updated)
        projects = tester.get_projects()
        print(f"\n✅ Celkem projektů: {len(projects) if projects else 0}")
    
    print("\n" + "="*60)
    print("✅ Test skončil úspěšně!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test přerušen")
    except Exception as e:
        print(f"\n\n❌ Chyba: {str(e)}")
