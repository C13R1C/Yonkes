from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.catalogos.models import Marca
from apps.inventario.models import Vehiculo
from apps.yonkes.models import Yonke


class CatalogDeletePermissionTests(TestCase):
    def setUp(self):
        self.yonke = Yonke.objects.create(nombre="Yonke Uno", estatus="activo")
        self.otro_yonke = Yonke.objects.create(nombre="Yonke Dos", estatus="activo")
        self.admin = self._user("admin", UserProfile.ROLE_ADMIN_GENERAL)
        self.dueno = self._user("dueno", UserProfile.ROLE_DUENO_YONKE, self.yonke)
        self.busqueda = self._user("busqueda", UserProfile.ROLE_BUSQUEDA)

    def _user(self, username, role, yonke=None):
        user = User.objects.create_user(username=username, password="pass")
        UserProfile.objects.create(user=user, rol=role, yonke=yonke, activo=True)
        return user

    def _delete_url(self, obj):
        return reverse("catalogos-marcas-delete", args=[obj.pk])

    def test_canaco_elimina_global_permitido(self):
        marca = Marca.objects.create(nombre="Global CANACO")
        self.client.force_login(self.admin)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Marca.objects.filter(pk=marca.pk).exists())

    def test_dueno_elimina_registro_propio(self):
        marca = Marca.objects.create(nombre="Local propio", yonke=self.yonke)
        self.client.force_login(self.dueno)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Marca.objects.filter(pk=marca.pk).exists())

    def test_dueno_no_elimina_global(self):
        marca = Marca.objects.create(nombre="Global protegida")
        self.client.force_login(self.dueno)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())

    def test_dueno_no_elimina_registro_de_otro_yonke(self):
        marca = Marca.objects.create(nombre="Local ajeno", yonke=self.otro_yonke)
        self.client.force_login(self.dueno)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())

    def test_usuario_busqueda_no_elimina(self):
        marca = Marca.objects.create(nombre="Global usuario busqueda")
        self.client.force_login(self.busqueda)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())

    def test_registro_usado_no_se_borra_fisicamente(self):
        marca = Marca.objects.create(nombre="Usada")
        Vehiculo.objects.create(yonke=self.yonke, marca=marca, anio=2001)
        self.client.force_login(self.admin)

        response = self.client.post(self._delete_url(marca))

        self.assertEqual(response.status_code, 302)
        marca.refresh_from_db()
        self.assertFalse(marca.activo)

    def test_eliminacion_requiere_post(self):
        marca = Marca.objects.create(nombre="Requiere POST")
        self.client.force_login(self.admin)

        response = self.client.get(self._delete_url(marca))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())

    def test_get_a_eliminar_no_debe_eliminar(self):
        marca = Marca.objects.create(nombre="GET no borra")
        self.client.force_login(self.admin)

        self.client.get(self._delete_url(marca))

        self.assertTrue(Marca.objects.filter(pk=marca.pk).exists())
