from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.accounts.models import UserProfile
from apps.auditoria.models import AuditLog
from apps.inventario.models import Pieza, Vehiculo
from apps.yonkes.models import Yonke

User = get_user_model()


def make_user(username, role, yonke=None):
    user = User.objects.create_user(username=username, password="AuditPass123!")
    UserProfile.objects.create(user=user, rol=role, yonke=yonke, activo=True)
    return user


@override_settings(ALLOWED_HOSTS=["testserver"])
class AuditEventTests(TestCase):
    def setUp(self):
        self.yonke = Yonke.objects.create(nombre="Yonke Audit", estatus="activo")
        self.admin = make_user("auditadmin", UserProfile.ROLE_ADMIN_GENERAL)
        self.owner = make_user("auditowner", UserProfile.ROLE_DUENO_YONKE, self.yonke)
        self.employee = make_user("auditemployee", UserProfile.ROLE_EMPLEADO, self.yonke)
        self.search = make_user("auditsearch", UserProfile.ROLE_BUSQUEDA)
        self.vehicle = Vehiculo.objects.create(yonke=self.yonke, marca_texto="Nissan", modelo_texto="Tsuru", visibilidad="privado")
        self.piece = Pieza.objects.create(yonke=self.yonke, vehiculo=self.vehicle, nombre="Puerta", precio=100, precio_visible=False, visibilidad="privado")

    def test_admin_can_access_audit_and_non_admin_cannot(self):
        self.client.force_login(self.search)
        self.assertEqual(self.client.get("/auditoria/").status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get("/auditoria/").status_code, 200)

    def test_create_user_and_change_role_generate_audit_logs(self):
        self.client.force_login(self.admin)
        response = self.client.post("/usuarios/nuevo/", {"username": "newemployee", "first_name": "New", "last_name": "Employee", "email": "new@example.test", "rol": UserProfile.ROLE_EMPLEADO, "yonke": self.yonke.pk, "telefono": "", "activo": "on", "password": "Secur3-Delta-789!"})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newemployee")
        self.assertTrue(AuditLog.objects.filter(accion="crear_usuario", entidad_id=str(user.pk)).exists())
        response = self.client.post(f"/usuarios/{user.pk}/editar/", {"username": "newemployee", "first_name": "New", "last_name": "Employee", "email": "new@example.test", "rol": UserProfile.ROLE_BUSQUEDA, "yonke": "", "telefono": "", "activo": "on", "password": ""})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AuditLog.objects.filter(accion="cambiar_rol_usuario", entidad_id=str(user.pk)).exists())

    def test_create_vehicle_and_edit_piece_generate_audit_logs_with_changes(self):
        self.client.force_login(self.owner)
        response = self.client.post("/vehiculos/nuevo/", {"marca_texto": "Honda", "modelo_texto": "Civic", "estatus": "disponible", "visibilidad": "privado"})
        self.assertEqual(response.status_code, 302)
        vehicle = Vehiculo.objects.latest("id")
        self.assertTrue(AuditLog.objects.filter(accion="crear_vehiculo", entidad_id=str(vehicle.pk)).exists())
        response = self.client.post(f"/piezas/{self.piece.pk}/editar/", {"yonke": self.yonke.pk, "vehiculo": self.vehicle.pk, "nombre": "Puerta", "condicion": "usada", "estatus": "disponible", "visibilidad": "privado", "precio": "150.00", "precio_visible": "on", "cantidad": 1, "ubicacion": "A1", "observaciones": "Cambio"})
        self.assertEqual(response.status_code, 302)
        log = AuditLog.objects.filter(accion="editar_pieza", entidad_id=str(self.piece.pk)).latest("id")
        self.assertIn("precio", log.cambios)
        self.assertIn("precio_visible", log.cambios)
