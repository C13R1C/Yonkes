from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.accounts.models import UserProfile
from apps.auditoria.models import AuditLog

User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver"], LOGIN_RATE_LIMIT_ATTEMPTS=2, LOGIN_RATE_LIMIT_WINDOW=60)
class LoginRateLimitAndAuditTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="ratelimit", password="RatePass123!")
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROLE_BUSQUEDA, activo=True)

    def test_failed_attempts_block_temporarily_with_generic_message(self):
        for _ in range(2):
            response = self.client.post("/login/", {"username": "ratelimit", "password": "bad"})
            self.assertContains(response, "Credenciales inválidas.")
        response = self.client.post("/login/", {"username": "ratelimit", "password": "RatePass123!"})
        self.assertContains(response, "Credenciales inválidas.")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_successful_login_clears_counter_and_other_accounts_or_ips_are_independent(self):
        self.client.post("/login/", {"username": "ratelimit", "password": "bad"})
        response = self.client.post("/login/", {"username": "other", "password": "bad"})
        self.assertContains(response, "Credenciales inválidas.")
        response = self.client.post("/login/", {"username": "ratelimit", "password": "RatePass123!"})
        self.assertEqual(response.status_code, 302)
        self.client.post("/logout/")
        response = self.client.post("/login/", {"username": "ratelimit", "password": "bad"}, REMOTE_ADDR="203.0.113.10")
        self.assertContains(response, "Credenciales inválidas.")

    def test_login_logout_audit_events_do_not_store_passwords(self):
        self.client.post("/login/", {"username": "ratelimit", "password": "bad-secret"})
        failed = AuditLog.objects.filter(accion="login_fallido").latest("id")
        self.assertEqual(failed.cambios.get("username"), "ratelimit")
        self.assertNotIn("bad-secret", str(failed.cambios))
        self.client.post("/login/", {"username": "ratelimit", "password": "RatePass123!"})
        self.assertTrue(AuditLog.objects.filter(accion="login_exitoso", usuario=self.user).exists())
        self.client.post("/logout/")
        self.assertTrue(AuditLog.objects.filter(accion="logout", usuario=self.user).exists())
