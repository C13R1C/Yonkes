import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.accounts.models import UserProfile
from apps.importaciones.models import ImportacionExcel
from apps.inventario.models import Pieza, Vehiculo
from apps.yonkes.models import Yonke

User = get_user_model()


def make_user(username, role, yonke=None):
    user = User.objects.create_user(username=username, password="AccessPass123!")
    UserProfile.objects.create(user=user, rol=role, yonke=yonke, activo=True)
    return user


@override_settings(ALLOWED_HOSTS=["testserver"])
class TenantAccessTests(TestCase):
    def setUp(self):
        self.y1 = Yonke.objects.create(nombre="Yonke Uno", estatus="activo")
        self.y2 = Yonke.objects.create(nombre="Yonke Dos", estatus="activo")
        self.owner = make_user("owner", UserProfile.ROLE_DUENO_YONKE, self.y1)
        self.employee = make_user("employee", UserProfile.ROLE_EMPLEADO, self.y1)
        self.search = make_user("search", UserProfile.ROLE_BUSQUEDA, None)
        self.other_user = make_user("otheremployee", UserProfile.ROLE_EMPLEADO, self.y2)
        self.other_vehicle = Vehiculo.objects.create(yonke=self.y2, marca_texto="Ford", modelo_texto="F150", visibilidad="privado")
        self.own_vehicle = Vehiculo.objects.create(yonke=self.y1, marca_texto="Nissan", modelo_texto="Tsuru", visibilidad="privado")
        self.other_piece = Pieza.objects.create(yonke=self.y2, vehiculo=self.other_vehicle, nombre="Motor", visibilidad="privado")
        self.own_piece = Pieza.objects.create(yonke=self.y1, vehiculo=self.own_vehicle, nombre="Puerta", visibilidad="privado")

    def test_owner_cannot_view_or_edit_private_vehicle_from_other_yonke(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(f"/vehiculos/{self.other_vehicle.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/vehiculos/{self.other_vehicle.pk}/editar/").status_code, 404)

    def test_employee_cannot_edit_piece_from_other_yonke(self):
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(f"/piezas/{self.other_piece.pk}/editar/").status_code, 404)

    def test_owner_cannot_edit_user_from_other_yonke(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(f"/usuarios/{self.other_user.pk}/editar/").status_code, 404)

    def test_search_user_cannot_create_or_edit_inventory(self):
        self.client.force_login(self.search)
        self.assertEqual(self.client.get("/vehiculos/nuevo/").status_code, 403)
        self.assertEqual(self.client.get(f"/piezas/{self.own_piece.pk}/editar/").status_code, 404)

    def test_unauthenticated_private_route_redirects_to_login(self):
        response = self.client.get("/vehiculos/nuevo/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/?next=/vehiculos/nuevo/", response.url)

    def test_posted_yonke_is_ignored_for_vehicle_create(self):
        self.client.force_login(self.owner)
        response = self.client.post("/vehiculos/nuevo/", {"yonke": self.y2.pk, "marca_texto": "Honda", "modelo_texto": "Civic", "estatus": "disponible", "visibilidad": "privado"})
        self.assertEqual(response.status_code, 302)
        vehiculo = Vehiculo.objects.latest("id")
        self.assertEqual(vehiculo.yonke_id, self.y1.pk)

    def test_posted_vehicle_from_other_yonke_is_rejected_for_piece_create(self):
        self.client.force_login(self.owner)
        response = self.client.post("/piezas/nueva/", {"yonke": self.y1.pk, "vehiculo": self.other_vehicle.pk, "nombre": "Caja", "condicion": "usada", "estatus": "disponible", "visibilidad": "privado", "cantidad": 1})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Pieza.objects.filter(nombre="Caja").exists())

    def test_url_id_manipulation_returns_not_found(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/vehiculos/999999/editar/").status_code, 404)


@override_settings(ALLOWED_HOSTS=["testserver"])
class ApiAccessTests(TestCase):
    def setUp(self):
        self.y1 = Yonke.objects.create(nombre="Yonke Uno", estatus="activo")
        self.y2 = Yonke.objects.create(nombre="Yonke Dos", estatus="activo")
        self.owner = make_user("apiowner", UserProfile.ROLE_DUENO_YONKE, self.y1)
        self.vehicle = Vehiculo.objects.create(yonke=self.y1, marca_texto="Nissan", modelo_texto="Tsuru", visibilidad="privado")
        self.other_vehicle = Vehiculo.objects.create(yonke=self.y2, marca_texto="Ford", modelo_texto="F150", visibilidad="privado")

    def test_anonymous_api_requests_are_not_public(self):
        for url in ["/api/vehiculos/", "/api/piezas/", "/api/busqueda/piezas/", "/api/yonkes/"]:
            self.assertIn(self.client.get(url).status_code, [401, 403], url)

    def test_authenticated_user_accesses_own_api_objects_only(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/api/vehiculos/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/vehiculos/{self.vehicle.pk}/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/vehiculos/{self.other_vehicle.pk}/").status_code, 404)


@override_settings(ALLOWED_HOSTS=["testserver"])
class PrivateImportDownloadTests(TestCase):
    def setUp(self):
        self.y1 = Yonke.objects.create(nombre="Yonke Uno", estatus="activo")
        self.y2 = Yonke.objects.create(nombre="Yonke Dos", estatus="activo")
        self.owner = make_user("downowner", UserProfile.ROLE_DUENO_YONKE, self.y1)
        self.other = make_user("downother", UserProfile.ROLE_DUENO_YONKE, self.y2)
        self.admin = make_user("downadmin", UserProfile.ROLE_ADMIN_GENERAL, None)
        path = settings.MEDIA_ROOT / "importaciones" if hasattr(settings.MEDIA_ROOT, "__truediv__") else os.path.join(settings.MEDIA_ROOT, "importaciones")
        os.makedirs(path, exist_ok=True)
        self.file_path = os.path.join(str(path), "test.xlsx")
        with open(self.file_path, "wb") as fh:
            fh.write(b"private excel placeholder")
        self.importacion = ImportacionExcel.objects.create(yonke=self.y1, usuario=self.owner, tipo_importacion="vehiculos", archivo="importaciones/test.xlsx")

    def tearDown(self):
        if hasattr(self, "file_path") and os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_download_requires_auth_and_tenant_or_admin(self):
        self.assertEqual(self.client.get(f"/importaciones/{self.importacion.pk}/descargar/").status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f"/importaciones/{self.importacion.pk}/descargar/").status_code, 404)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(f"/importaciones/{self.importacion.pk}/descargar/").status_code, 200)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(f"/importaciones/{self.importacion.pk}/descargar/").status_code, 200)

    def test_arbitrary_file_or_directory_traversal_url_does_not_exist(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/importaciones/../../settings.py/descargar/").status_code, 404)
