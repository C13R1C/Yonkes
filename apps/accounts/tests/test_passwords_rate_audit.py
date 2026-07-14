from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.accounts.forms import RegisterForm, UsuarioCreateForm, UsuarioEditForm
from apps.accounts.models import UserProfile
from apps.yonkes.models import Yonke

User = get_user_model()


def base_register(password="ValidPass123!", password_confirm=None, username="secureuser"):
    return {
        "username": username,
        "first_name": "Secure",
        "last_name": "User",
        "email": "secure@example.test",
        "password": password,
        "password_confirm": password if password_confirm is None else password_confirm,
        "telefono": "",
    }


@override_settings(ALLOWED_HOSTS=["testserver"])
class PasswordValidationTests(TestCase):
    def setUp(self):
        self.yonke = Yonke.objects.create(nombre="Yonke Uno", estatus="activo")

    def test_register_rejects_short_common_numeric_and_similar_passwords(self):
        for password, username in [("short", "shortuser"), ("password", "commonuser"), ("123456789", "numericuser"), ("similaruser2026", "similaruser")]:
            form = RegisterForm(data=base_register(password=password, username=username))
            self.assertFalse(form.is_valid(), password)
            self.assertIn("password", form.errors)

    def test_register_accepts_valid_password_and_rejects_mismatch(self):
        form = RegisterForm(data=base_register())
        self.assertTrue(form.is_valid(), form.errors)
        mismatch = RegisterForm(data=base_register(password_confirm="AnotherValid123!"))
        self.assertFalse(mismatch.is_valid())
        self.assertIn("password_confirm", mismatch.errors)

    def test_usuario_create_and_edit_validate_password_when_required(self):
        data = {
            "username": "createduser",
            "first_name": "Created",
            "last_name": "User",
            "email": "created@example.test",
            "rol": UserProfile.ROLE_EMPLEADO,
            "yonke": self.yonke.pk,
            "telefono": "",
            "activo": "on",
            "password": "123456789",
        }
        form = UsuarioCreateForm(data=data, actor=self._admin())
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        data["password"] = "CreatedPass123!"
        form = UsuarioCreateForm(data=data, actor=self._admin())
        self.assertTrue(form.is_valid(), form.errors)

        edit_data = data.copy()
        edit_data["password"] = ""
        edit_form = UsuarioEditForm(data=edit_data, actor=self._admin())
        self.assertTrue(edit_form.is_valid(), edit_form.errors)
        edit_data["password"] = "password"
        edit_form = UsuarioEditForm(data=edit_data, actor=self._admin())
        self.assertFalse(edit_form.is_valid())
        self.assertIn("password", edit_form.errors)

    def test_created_user_password_is_hashed(self):
        response = self.client.post("/register/", base_register(username="hashuser"))
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="hashuser")
        self.assertNotEqual(user.password, "ValidPass123!")
        self.assertTrue(user.check_password("ValidPass123!"))

    def _admin(self):
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.test"})
        if not admin.has_usable_password():
            admin.set_password("AdminPass123!")
            admin.save()
        UserProfile.objects.get_or_create(user=admin, defaults={"rol": UserProfile.ROLE_ADMIN_GENERAL, "activo": True})
        return admin

