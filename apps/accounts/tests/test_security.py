from django.contrib.auth import authenticate, get_user_model
from django.test import Client, TestCase, override_settings
from apps.accounts.forms import RegisterForm
from apps.accounts.models import UserProfile
from apps.yonkes.models import Yonke

User = get_user_model()


@override_settings(ALLOWED_HOSTS=["testserver"])
class PublicRegistrationSecurityTests(TestCase):
    def setUp(self):
        self.yonke = Yonke.objects.create(nombre="Yonke Seguro", estatus="activo")

    def test_public_register_form_does_not_expose_role_or_yonke(self):
        form = RegisterForm()
        self.assertNotIn("rol", form.fields)
        self.assertNotIn("yonke", form.fields)

        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="rol"')
        self.assertNotContains(response, 'name="yonke"')

    def test_posted_role_and_yonke_are_ignored_and_password_is_hashed(self):
        response = self.client.post(
            "/register/",
            {
                "username": "public-user",
                "first_name": "Public",
                "last_name": "User",
                "email": "public@example.test",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "telefono": "5551234567",
                "rol": UserProfile.ROLE_ADMIN_GENERAL,
                "yonke": str(self.yonke.pk),
            },
        )
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="public-user")
        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.profile.rol, UserProfile.ROLE_BUSQUEDA)
        self.assertIsNone(user.profile.yonke)
        self.assertTrue(user.profile.activo)
        self.assertIsNotNone(authenticate(username="public-user", password="StrongPass123!"))


@override_settings(ALLOWED_HOSTS=["testserver"])
class LoginRedirectSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="login-user", password="StrongPass123!")
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROLE_BUSQUEDA, activo=True)

    def test_internal_next_is_preserved(self):
        response = self.client.post("/login/?next=/vehiculos/", {"username": "login-user", "password": "StrongPass123!"})
        self.assertRedirects(response, "/vehiculos/", fetch_redirect_response=False)

    def test_external_https_next_is_rejected(self):
        response = self.client.post("/login/?next=https://evil.example", {"username": "login-user", "password": "StrongPass123!"})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_protocol_relative_next_is_rejected(self):
        response = self.client.post("/login/?next=//evil.example", {"username": "login-user", "password": "StrongPass123!"})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_missing_next_goes_to_dashboard(self):
        response = self.client.post("/login/", {"username": "login-user", "password": "StrongPass123!"})
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_private_route_returns_to_original_path_after_login(self):
        response = self.client.get("/perfil/")
        self.assertRedirects(response, "/login/?next=/perfil/", fetch_redirect_response=False)
        response = self.client.post("/login/?next=/perfil/", {"username": "login-user", "password": "StrongPass123!"})
        self.assertRedirects(response, "/perfil/", fetch_redirect_response=False)


@override_settings(ALLOWED_HOSTS=["testserver"])
class LogoutSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="logout-user", password="StrongPass123!")
        UserProfile.objects.create(user=self.user, rol=UserProfile.ROLE_BUSQUEDA, activo=True)

    def test_logout_get_is_not_allowed(self):
        self.client.force_login(self.user)
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 405)

    def test_logout_post_with_session_logs_out(self):
        self.client.force_login(self.user)
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_post_without_csrf_fails_when_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post("/logout/")
        self.assertEqual(response.status_code, 403)

    def test_logout_post_with_valid_csrf_logs_out(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        get_response = client.get("/perfil/")
        self.assertEqual(get_response.status_code, 200)
        token = client.cookies["csrftoken"].value
        response = client.post("/logout/", HTTP_X_CSRFTOKEN=token)
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        self.assertNotIn("_auth_user_id", client.session)
