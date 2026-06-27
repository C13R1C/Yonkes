import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.catalogos.models import AliasPieza, Marca, ModeloVehiculo, NombrePieza
from apps.inventario.models import Pieza, Vehiculo
from apps.yonkes.models import Yonke


User = get_user_model()
TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class InventoryRolePermissionTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.yonke_a = Yonke.objects.create(nombre="Yonke A", estatus="activo", mostrar_contacto=True, telefono="111")
        self.yonke_b = Yonke.objects.create(nombre="Yonke B", estatus="activo", mostrar_contacto=True, telefono="222")

        self.admin = User.objects.create_superuser(username="admin", password="pass12345")
        self.owner = self._user("owner", UserProfile.ROLE_DUENO_YONKE, self.yonke_a)
        self.employee = self._user("employee", UserProfile.ROLE_EMPLEADO, self.yonke_a)
        self.search_user = self._user("search", UserProfile.ROLE_BUSQUEDA, None)

        self.own_vehicle = Vehiculo.objects.create(yonke=self.yonke_a, marca_texto="Nissan", modelo_texto="Versa", visibilidad="visible")
        self.other_vehicle = Vehiculo.objects.create(yonke=self.yonke_b, marca_texto="Ford", modelo_texto="Focus", visibilidad="visible")

        self.own_piece = Pieza.objects.create(
            yonke=self.yonke_a,
            vehiculo=self.own_vehicle,
            nombre="Alternador propio",
            visibilidad="oculto",
            precio="100.00",
            precio_visible=False,
            ubicacion="Rack A",
        )
        self.other_visible_piece = Pieza.objects.create(
            yonke=self.yonke_b,
            nombre="Alternador externo visible",
            visibilidad="visible",
            precio="999.00",
            precio_visible=False,
            ubicacion="Rack B",
        )
        self.other_hidden_piece = Pieza.objects.create(
            yonke=self.yonke_b,
            nombre="Alternador oculto",
            visibilidad="oculto",
            precio="888.00",
            precio_visible=False,
        )

    def _user(self, username, role, yonke):
        user = User.objects.create_user(username=username, password="pass12345")
        UserProfile.objects.create(user=user, rol=role, yonke=yonke, activo=True)
        return user

    def _image(self, name="inventario.gif"):
        return SimpleUploadedFile(
            name,
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )

    def test_owner_can_edit_piece_from_own_yonke(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:piezas-edit", args=[self.own_piece.pk]),
            {
                "yonke": self.yonke_a.pk,
                "nombre": "Alternador editado",
                "condicion": "usada",
                "estatus": "disponible",
                "visibilidad": "oculto",
                "precio": "101.00",
                "cantidad": 1,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.own_piece.refresh_from_db()
        self.assertEqual(self.own_piece.nombre, "Alternador editado")

    def test_owner_cannot_edit_piece_from_other_yonke(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:piezas-edit", args=[self.other_visible_piece.pk]))
        self.assertEqual(response.status_code, 403)

    def test_employee_can_view_visible_inventory_from_other_yonke(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("inventario_html:piezas-detail", args=[self.other_visible_piece.pk]))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_edit_inventory_from_other_yonke(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("inventario_html:piezas-edit", args=[self.other_visible_piece.pk]))
        self.assertEqual(response.status_code, 403)

    def test_search_user_cannot_create_piece(self):
        self.client.force_login(self.search_user)
        response = self.client.get(reverse("inventario_html:piezas-create"))
        self.assertEqual(response.status_code, 403)

    def test_search_user_only_sees_visible_pieces(self):
        self.client.force_login(self.search_user)
        response = self.client.get(reverse("inventario_html:piezas-list"))
        content = response.content.decode()
        self.assertContains(response, self.other_visible_piece.nombre)
        self.assertNotIn(self.other_hidden_piece.nombre, content)
        self.assertNotIn(self.own_piece.nombre, content)

    def test_hidden_price_is_not_rendered_for_external_search(self):
        self.client.force_login(self.search_user)
        response = self.client.get("/busqueda/", {"pieza": "Alternador externo visible"})
        content = response.content.decode()
        self.assertContains(response, "Precio no visible")
        self.assertNotIn("999.00", content)

    def test_admin_can_view_global_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_owner_can_view_all_active_yonkes_as_directory(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("yonkes_html:yonkes-list"))
        self.assertContains(response, self.yonke_a.nombre)
        self.assertContains(response, self.yonke_b.nombre)

    def test_employee_can_view_all_active_yonkes_as_directory(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse("yonkes_html:yonkes-list"))
        self.assertContains(response, self.yonke_a.nombre)
        self.assertContains(response, self.yonke_b.nombre)

    def test_owner_cannot_edit_other_yonke_from_directory(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("yonkes_html:yonkes-edit", args=[self.yonke_b.pk]))
        self.assertEqual(response.status_code, 403)

    def test_private_yonke_contact_and_notes_hidden_for_external_owner(self):
        self.yonke_b.mostrar_contacto = False
        self.yonke_b.telefono = "222-privado"
        self.yonke_b.whatsapp = "whatsapp-privado"
        self.yonke_b.email = "privado@example.com"
        self.yonke_b.contacto_principal = "Contacto privado"
        self.yonke_b.notas_internas = "Nota interna privada"
        self.yonke_b.save()
        self.client.force_login(self.owner)
        response = self.client.get(reverse("yonkes_html:yonkes-detail", args=[self.yonke_b.pk]))
        content = response.content.decode()
        self.assertContains(response, self.yonke_b.nombre)
        self.assertContains(response, "Contacto no publico")
        self.assertNotIn("222-privado", content)
        self.assertNotIn("whatsapp-privado", content)
        self.assertNotIn("privado@example.com", content)
        self.assertNotIn("Contacto privado", content)
        self.assertNotIn("Nota interna privada", content)

    def test_admin_views_inventory_as_read_only(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventario_html:piezas-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.own_piece.nombre)
        self.assertNotContains(response, reverse("inventario_html:piezas-edit", args=[self.own_piece.pk]))

    def test_admin_cannot_create_vehicle(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventario_html:vehiculos-create"))
        self.assertEqual(response.status_code, 403)

    def test_owner_vehicle_form_only_lists_own_yonke_brands(self):
        own_brand = Marca.objects.create(nombre="Marca Yonke A", yonke=self.yonke_a, activo=True)
        other_brand = Marca.objects.create(nombre="Marca Yonke B", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:vehiculos-create"))
        content = response.content.decode()
        self.assertContains(response, own_brand.nombre)
        self.assertNotIn(other_brand.nombre, content)

    def test_employee_vehicle_form_only_lists_own_yonke_brands(self):
        own_brand = Marca.objects.create(nombre="Marca empleado A", yonke=self.yonke_a, activo=True)
        other_brand = Marca.objects.create(nombre="Marca empleado B", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.employee)
        response = self.client.get(reverse("inventario_html:vehiculos-create"))
        content = response.content.decode()
        self.assertContains(response, own_brand.nombre)
        self.assertNotIn(other_brand.nombre, content)

    def test_owner_cannot_create_vehicle_with_other_yonke_brand(self):
        other_brand = Marca.objects.create(nombre="Marca externa", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:vehiculos-create"),
            {
                "yonke": self.yonke_a.pk,
                "marca": other_brand.pk,
                "anio": 2005,
                "estatus": "disponible",
                "visibilidad": "visible",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vehiculo.objects.filter(marca=other_brand).exists())

    def test_owner_cannot_create_vehicle_with_other_yonke_model(self):
        own_brand = Marca.objects.create(nombre="Marca propia modelo", yonke=self.yonke_a, activo=True)
        other_model = ModeloVehiculo.objects.create(marca=own_brand, nombre="Modelo externo", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:vehiculos-create"),
            {
                "yonke": self.yonke_a.pk,
                "marca": own_brand.pk,
                "modelo": other_model.pk,
                "anio": 2006,
                "estatus": "disponible",
                "visibilidad": "visible",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Vehiculo.objects.filter(modelo=other_model).exists())

    def test_admin_cannot_create_piece(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("inventario_html:piezas-create"))
        self.assertEqual(response.status_code, 403)

    def test_vehicle_create_redirects_to_html_detail_not_api(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:vehiculos-create"),
            {
                "yonke": self.yonke_a.pk,
                "anio": 2001,
                "estatus": "disponible",
                "visibilidad": "visible",
            },
        )
        self.assertEqual(response.status_code, 302)
        vehiculo = Vehiculo.objects.latest("pk")
        self.assertEqual(response["Location"], reverse("inventario_html:vehiculos-detail", args=[vehiculo.pk]))
        self.assertTrue(response["Location"].startswith("/vehiculos/"))

    def test_can_create_multiple_pieces_for_same_vehicle(self):
        self.client.force_login(self.owner)
        for name in ["Puerta derecha", "Faro izquierdo", "Motor"]:
            response = self.client.post(
                f"{reverse('inventario_html:piezas-create')}?vehiculo={self.own_vehicle.pk}",
                {
                    "vehiculo_context": self.own_vehicle.pk,
                    "yonke": self.yonke_a.pk,
                    "vehiculo": self.own_vehicle.pk,
                    "nombre": name,
                    "condicion": "usada",
                    "estatus": "disponible",
                    "visibilidad": "visible",
                    "cantidad": 1,
                },
            )
            self.assertEqual(response.status_code, 302)
        self.assertEqual(Pieza.objects.filter(vehiculo=self.own_vehicle).count(), 4)

    def test_owner_can_add_piece_to_own_vehicle_and_redirects_to_vehicle(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            f"{reverse('inventario_html:piezas-create')}?vehiculo={self.own_vehicle.pk}",
            {
                "vehiculo_context": self.own_vehicle.pk,
                "yonke": self.yonke_a.pk,
                "vehiculo": self.own_vehicle.pk,
                "nombre": "Radiador",
                "condicion": "usada",
                "estatus": "disponible",
                "visibilidad": "visible",
                "cantidad": 1,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("inventario_html:vehiculos-detail", args=[self.own_vehicle.pk]))
        self.assertTrue(Pieza.objects.filter(vehiculo=self.own_vehicle, nombre="Radiador").exists())

    def test_employee_can_add_piece_to_own_vehicle(self):
        self.client.force_login(self.employee)
        response = self.client.post(
            f"{reverse('inventario_html:piezas-create')}?vehiculo={self.own_vehicle.pk}",
            {
                "vehiculo_context": self.own_vehicle.pk,
                "yonke": self.yonke_a.pk,
                "vehiculo": self.own_vehicle.pk,
                "nombre": "Cofre",
                "condicion": "usada",
                "estatus": "disponible",
                "visibilidad": "visible",
                "cantidad": 1,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pieza.objects.filter(vehiculo=self.own_vehicle, nombre="Cofre").exists())

    def test_search_user_cannot_add_piece_to_vehicle(self):
        self.client.force_login(self.search_user)
        response = self.client.get(f"{reverse('inventario_html:piezas-create')}?vehiculo={self.own_vehicle.pk}")
        self.assertEqual(response.status_code, 403)

    def test_owner_cannot_add_piece_to_other_yonke_vehicle(self):
        self.client.force_login(self.owner)
        response = self.client.get(f"{reverse('inventario_html:piezas-create')}?vehiculo={self.other_vehicle.pk}")
        self.assertEqual(response.status_code, 403)

    def test_employee_cannot_add_piece_to_other_yonke_vehicle(self):
        self.client.force_login(self.employee)
        response = self.client.get(f"{reverse('inventario_html:piezas-create')}?vehiculo={self.other_vehicle.pk}")
        self.assertEqual(response.status_code, 403)

    def test_loose_piece_create_keeps_current_redirect(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:piezas-create"),
            {
                "yonke": self.yonke_a.pk,
                "nombre": "Pieza suelta",
                "condicion": "usada",
                "estatus": "disponible",
                "visibilidad": "visible",
                "cantidad": 1,
            },
        )
        self.assertEqual(response.status_code, 302)
        pieza = Pieza.objects.get(nombre="Pieza suelta")
        self.assertIsNone(pieza.vehiculo)
        self.assertEqual(response["Location"], reverse("inventario_html:piezas-detail", args=[pieza.pk]))

    def test_vehicle_can_be_created_with_main_image(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:vehiculos-create"),
            {
                "yonke": self.yonke_a.pk,
                "anio": 2002,
                "estatus": "disponible",
                "visibilidad": "visible",
                "imagen_principal": self._image("vehiculo.gif"),
            },
        )
        self.assertEqual(response.status_code, 302)
        vehiculo = Vehiculo.objects.latest("pk")
        self.assertTrue(vehiculo.imagen_principal.name.startswith("vehiculos/principales/"))

    def test_piece_can_be_created_with_main_image(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:piezas-create"),
            {
                "yonke": self.yonke_a.pk,
                "nombre": "Manija exterior",
                "condicion": "usada",
                "estatus": "disponible",
                "visibilidad": "visible",
                "cantidad": 1,
                "imagen_principal": self._image("pieza.gif"),
            },
        )
        self.assertEqual(response.status_code, 302)
        pieza = Pieza.objects.get(nombre="Manija exterior")
        self.assertTrue(pieza.imagen_principal.name.startswith("piezas/principales/"))

    def test_search_result_renders_image_or_placeholder(self):
        self.client.force_login(self.search_user)
        response = self.client.get("/busqueda/", {"pieza": "Alternador externo visible"})
        content = response.content.decode()
        self.assertTrue("media-placeholder" in content or "media-main" in content)

    def test_search_user_does_not_see_hidden_piece_image(self):
        self.own_piece.imagen_principal = self._image("oculta.gif")
        self.own_piece.save()
        self.client.force_login(self.search_user)
        response = self.client.get(reverse("inventario_html:piezas-list"))
        content = response.content.decode()
        self.assertNotIn("oculta", content)
        self.assertNotIn(self.own_piece.nombre, content)

    def test_owner_sees_hidden_own_piece_image(self):
        self.own_piece.imagen_principal = self._image("propia-oculta.gif")
        self.own_piece.save()
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:piezas-detail", args=[self.own_piece.pk]))
        self.assertContains(response, "propia-oculta")

    def test_brand_catalog_renders_logo_or_placeholder(self):
        marca_con_logo = Marca.objects.create(nombre="Marca con logo")
        marca_con_logo.logo = self._image("marca.gif")
        marca_con_logo.save()
        Marca.objects.create(nombre="Marca sin logo")
        self.client.force_login(self.admin)
        response = self.client.get("/catalogos/marcas/")
        self.assertContains(response, "marca.gif")
        self.assertContains(response, "Sin logo")

    def test_search_user_cannot_create_catalogs(self):
        self.client.force_login(self.search_user)
        response = self.client.get("/catalogos/nombres-piezas/nuevo/")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_create_own_piece_name_catalog(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            "/catalogos/nombres-piezas/nuevo/",
            {
                "nombre_normalizado": "Facia delantera",
                "activo": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        nombre = NombrePieza.objects.get(nombre_normalizado="Facia delantera")
        self.assertEqual(nombre.yonke, self.yonke_a)

    def test_employee_can_create_own_piece_alias_catalog(self):
        nombre = NombrePieza.objects.create(nombre_normalizado="Calavera", yonke=self.yonke_a, activo=True)
        self.client.force_login(self.employee)
        response = self.client.post(
            "/catalogos/alias-piezas/nuevo/",
            {
                "nombre_pieza": nombre.pk,
                "alias": "Stop trasero",
            },
        )
        self.assertEqual(response.status_code, 302)
        alias = AliasPieza.objects.get(alias="Stop trasero")
        self.assertEqual(alias.yonke, self.yonke_a)

    def test_admin_cannot_create_operational_catalog(self):
        self.client.force_login(self.admin)
        response = self.client.get("/catalogos/nombres-piezas/nuevo/")
        self.assertEqual(response.status_code, 403)

    def test_private_catalog_does_not_appear_for_other_yonke(self):
        private_name = NombrePieza.objects.create(nombre_normalizado="Moldura privada", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:piezas-create"))
        content = response.content.decode()
        self.assertNotIn(private_name.nombre_normalizado, content)

    def test_owner_inventory_admin_lists_own_inventory_first(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:piezas-list"))
        content = response.content.decode()
        self.assertLess(content.index(self.own_piece.nombre), content.index(self.other_visible_piece.nombre))

    def test_vehicle_table_shows_yonke_before_image(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:vehiculos-list"))
        content = response.content.decode()
        expected_headers = [
            "<th>Yonke</th>",
            "<th>Imagen</th>",
            "<th>Marca</th>",
            "<th>Modelo</th>",
            "<th>Anio</th>",
            "<th>Estatus</th>",
            "<th>Visibilidad</th>",
            "<th>Fecha de creacion</th>",
            "<th>Acciones</th>",
        ]
        positions = [content.index(header) for header in expected_headers]
        self.assertEqual(positions, sorted(positions))

    def test_search_orders_own_yonke_before_external_visible(self):
        own_visible = Pieza.objects.create(
            yonke=self.yonke_a,
            nombre="Alternador visible propio",
            visibilidad="visible",
            estatus="disponible",
            cantidad=1,
        )
        self.client.force_login(self.owner)
        response = self.client.get("/busqueda/", {"pieza": "Alternador"})
        content = response.content.decode()
        self.assertLess(content.index(own_visible.nombre), content.index(self.other_visible_piece.nombre))

    def test_suspended_yonke_user_cannot_operate_inventory(self):
        self.yonke_a.estatus = "suspendido"
        self.yonke_a.save()
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:vehiculos-create"))
        self.assertEqual(response.status_code, 403)

    def test_suspended_yonke_user_cannot_create_operational_catalog(self):
        self.yonke_a.estatus = "suspendido"
        self.yonke_a.save()
        self.client.force_login(self.employee)
        response = self.client.get("/catalogos/nombres-piezas/nuevo/")
        self.assertEqual(response.status_code, 403)

    def test_admin_can_suspend_and_reactivate_yonke(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("yonkes_html:yonkes-edit", args=[self.yonke_a.pk]),
            {
                "nombre": self.yonke_a.nombre,
                "estatus": "suspendido",
                "mostrar_contacto": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.yonke_a.refresh_from_db()
        self.assertEqual(self.yonke_a.estatus, "suspendido")

        response = self.client.post(
            reverse("yonkes_html:yonkes-edit", args=[self.yonke_a.pk]),
            {
                "nombre": self.yonke_a.nombre,
                "estatus": "activo",
                "mostrar_contacto": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.yonke_a.refresh_from_db()
        self.assertEqual(self.yonke_a.estatus, "activo")

    def test_images_use_uniform_classes(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("inventario_html:piezas-list"))
        self.assertContains(response, "media-thumb")
        response = self.client.get(reverse("inventario_html:piezas-detail", args=[self.own_piece.pk]))
        self.assertContains(response, "media-detail")

    def test_models_api_filters_by_brand(self):
        nissan = Marca.objects.create(nombre="Nissan", yonke=self.yonke_a)
        ford = Marca.objects.create(nombre="Ford", yonke=self.yonke_a)
        versa = ModeloVehiculo.objects.create(marca=nissan, nombre="Versa", yonke=self.yonke_a, activo=True)
        ModeloVehiculo.objects.create(marca=ford, nombre="Focus", yonke=self.yonke_a, activo=True)
        self.client.force_login(self.owner)
        response = self.client.get("/api/catalogos/modelos/", {"marca": nissan.pk, "activo": "true"})
        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn(versa.nombre, content)
        self.assertNotIn("Focus", content)

    def test_models_api_filters_by_brand_and_user_yonke(self):
        nissan = Marca.objects.create(nombre="Nissan catalogo A", yonke=self.yonke_a)
        own_model = ModeloVehiculo.objects.create(marca=nissan, nombre="Versa propio", yonke=self.yonke_a, activo=True)
        external_model = ModeloVehiculo.objects.create(marca=nissan, nombre="Versa externo", yonke=self.yonke_b, activo=True)
        self.client.force_login(self.owner)
        response = self.client.get("/api/catalogos/modelos/", {"marca": nissan.pk, "activo": "true"})
        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn(own_model.nombre, content)
        self.assertNotIn(external_model.nombre, content)

    def test_vehicle_does_not_allow_model_from_other_brand(self):
        nissan = Marca.objects.create(nombre="Nissan")
        ford = Marca.objects.create(nombre="Ford")
        focus = ModeloVehiculo.objects.create(marca=ford, nombre="Focus", activo=True)
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("inventario_html:vehiculos-create"),
            {
                "yonke": self.yonke_a.pk,
                "marca": nissan.pk,
                "modelo": focus.pk,
                "anio": 2019,
                "estatus": "disponible",
                "visibilidad": "visible",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "El modelo seleccionado no pertenece a la marca indicada.")
