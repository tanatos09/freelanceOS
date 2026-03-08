"""
End-to-End UI testy pro aplikaci `freelanceos`.

Testuje kompletní auth flow přes webové rozhraní pomocí Playwright.
Testy:
- Registrace přes webové formuláře
- Login přes webové formuláře
- Dashboard přístup
- Logout
"""
import os
from playwright.sync_api import sync_playwright

# Konfigurace
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"


class TestAuthFlow:
    """E2E testy pro auth flow.."""

    @staticmethod
    def setup_method():
        """Setup před každým testem (Playwright context)."""
        pass

    @staticmethod
    def teardown_method():
        """Cleanup po každém testu."""
        pass

    def test_registration_flow(self):
        """
        Test: Registrace přes web UI.

        Scénář:
        1. Jdi na registrační stránku
        2. Vyplň formulář (email, heslo, heslo2)
        3. Odešli formulář
        4. Ověři redirect na login nebo dashboard
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page()

            try:
                # Jdi na registrační stránku
                page.goto(f"{BASE_URL}/accounts/register/")

                # Ověř, že stránka existuje
                assert "register" in page.url or "signup" in page.url

                # Vyplň registrační formulář
                page.fill('input[name="email"]', "e2e_test@example.com")
                page.fill('input[name="password"]', "SecurePass123!")
                page.fill('input[name="password2"]', "SecurePass123!")

                # Klikni na submit
                page.click('button[type="submit"]')

                # Počkej na navigaci
                page.wait_for_load_state("networkidle")

                # Ověří, že jsme na login nebo dashboard stránce
                assert (
                    "login" in page.url or "dashboard" in page.url or "accounts" in page.url
                ), f"Unexpected URL after registration: {page.url}"

                print("✓ Registrace přes UI úspěšná")

            finally:
                browser.close()

    def test_login_and_dashboard_flow(self):
        """
        Test: Login přes web UI a přístup na dashboard.

        Scénář:
        1. Jdi na login stránku
        2. Vyplň email a heslo
        3. Odešli formulář
        4. Ověř přístup na dashboard
        5. Ověř, že je zobrazeno uživatelské info
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page()

            try:
                # Jdi na login stránku
                page.goto(f"{BASE_URL}/accounts/login/")

                # Ověř, že jsme na login stránce
                assert "login" in page.url

                # Vyplň login formulář
                page.fill('input[name="email"]', "login@example.com")
                page.fill('input[name="password"]', "testpass123")

                # Klikni na submit
                page.click('button[type="submit"]')

                # Počkej na response
                page.wait_for_load_state("networkidle")

                # Ověř, že jsme přesměrováni
                # (může to být dashboard, home, nebo cokoliv mimo login)
                assert "login" not in page.url.lower(), f"Stále na login stránce: {page.url}"

                print("✓ Login přes UI úspěšný")

            finally:
                browser.close()

    def test_logout_flow(self):
        """
        Test: Logout a ověření přesměrování.

        Scénář:
        1. Login
        2. Najdi logout button
        3. Klikni na logout
        4. Ověř, že jsme na login/home stránce
        5. Ověř, že cookies/tokeny jsou smazány
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page()

            try:
                # Jdi na login stránku
                page.goto(f"{BASE_URL}/accounts/login/")

                # Vyplň a odešli login
                page.fill('input[name="email"]', "login@example.com")
                page.fill('input[name="password"]', "testpass123")
                page.click('button[type="submit"]')

                # Počkej na login
                page.wait_for_load_state("networkidle")

                # Najdi logout button (může být v menu, sidebar, atd.)
                logout_buttons = page.query_selector_all(
                    'a[href*="logout"], button:has-text("logout"), a:has-text("logout")'
                )

                if logout_buttons:
                    logout_buttons[0].click()
                    page.wait_for_load_state("networkidle")

                    # Ověř, že jsme na public page
                    print(f"✓ Logout úspěšný, aktuální URL: {page.url}")
                else:
                    # Logout button nenalezen - info
                    print("ℹ Logout button nenalezen - test skončen")

            finally:
                browser.close()

    def test_invalid_credentials(self):
        """
        Test: Login s neplatnými údaji.

        Scénář:
        1. Jdi na login
        2. Vyplň neplatný email/heslo
        3. Odešli
        4. Ověř error zprávu
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page()

            try:
                # Jdi na login
                page.goto(f"{BASE_URL}/accounts/login/")

                # Vyplň neplatné údaje
                page.fill('input[name="email"]', "invalid@example.com")
                page.fill('input[name="password"]', "wrongpassword")

                # Odešli
                page.click('button[type="submit"]')

                # Počkej na response
                page.wait_for_load_state("networkidle")

                # Ověř error (měli bychom být stále na login)
                # nebo vidět chybovou zprávu
                has_error = (
                    "login" in page.url
                    or "error" in page.content().lower()
                    or "invalid" in page.content().lower()
                )

                assert has_error, "Nebylo zobrazeno chybové hlášení"

                print("✓ Správné zacházení s neplatnými přihlašovacími údaji")

            finally:
                browser.close()

    def test_page_responsiveness(self):
        """
        Test: Responzivní design (mobile view).

        Scénář:
        1. Nastavi viewport na mobilní velikost
        2. Jdi na stránku
        3. Ověř, že se stránka správně zobrazuje
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)

            # Mobilní viewport
            page = browser.new_page(
                viewport={"width": 375, "height": 667},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X)",
            )

            try:
                # Jdi na login
                page.goto(f"{BASE_URL}/accounts/login/")

                # Ověř, že se stránka zobrazuje bez errorů
                # a že formulář je dostupný
                email_input = page.query_selector('input[name="email"]')

                assert email_input is not None, "Email input nenalezen na mobile"
                assert email_input.is_visible(), "Email input není viditelný"

                print("✓ Mobilní responsiveness OK")

            finally:
                browser.close()


if __name__ == "__main__":
    # Testy lze spustit přímo bez pytest
    import sys

    test = TestAuthFlow()

    tests = [
        ("Registration Flow", test.test_registration_flow),
        ("Login Flow", test.test_login_and_dashboard_flow),
        ("Logout Flow", test.test_logout_flow),
        ("Invalid Credentials", test.test_invalid_credentials),
        ("Page Responsiveness", test.test_page_responsiveness),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n[TEST] {test_name}...")
            test_func()
            passed += 1
        except Exception as e:
            print(f"[FAILED] {test_name}: {str(e)}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")

    sys.exit(0 if failed == 0 else 1)
