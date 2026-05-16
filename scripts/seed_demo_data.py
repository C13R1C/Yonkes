from django.contrib.auth.models import User

from apps.yonkes.models import Yonke
from apps.catalogos.models import Marca, ModeloVehiculo, CategoriaPieza, NombrePieza, AliasPieza
from apps.inventario.models import Vehiculo, Pieza


def get_admin_user():
    user = User.objects.filter(is_superuser=True).first()
    return user


def run():
    admin_user = get_admin_user()

    yonkes_data = [
        {
            "nombre": "Yonke Norte",
            "telefono": "656-100-0001",
            "whatsapp": "6561000001",
            "email": "contacto@yonkenorte.demo",
            "direccion": "Av. Tecnologico, Ciudad Juarez",
            "contacto_principal": "Encargado Norte",
            "estatus": "activo",
        },
        {
            "nombre": "Yonke Rio Bravo",
            "telefono": "656-100-0002",
            "whatsapp": "6561000002",
            "email": "contacto@yonkeriobravo.demo",
            "direccion": "Zona Rio Bravo, Ciudad Juarez",
            "contacto_principal": "Encargado Rio Bravo",
            "estatus": "activo",
        },
        {
            "nombre": "Yonke Central",
            "telefono": "656-100-0003",
            "whatsapp": "6561000003",
            "email": "contacto@yonkecentral.demo",
            "direccion": "Centro, Ciudad Juarez",
            "contacto_principal": "Encargado Central",
            "estatus": "activo",
        },
        {
            "nombre": "Yonke Frontera",
            "telefono": "656-100-0004",
            "whatsapp": "6561000004",
            "email": "contacto@yonkefrontera.demo",
            "direccion": "Zona Frontera, Ciudad Juarez",
            "contacto_principal": "Encargado Frontera",
            "estatus": "activo",
        },
    ]

    yonkes = {}
    for data in yonkes_data:
        yonke, _ = Yonke.objects.get_or_create(nombre=data["nombre"], defaults=data)
        yonkes[data["nombre"]] = yonke

    marcas_nombres = ["Nissan", "Chevrolet", "Ford", "Honda", "Toyota"]
    marcas = {}
    for nombre in marcas_nombres:
        marca, _ = Marca.objects.get_or_create(nombre=nombre)
        marcas[nombre] = marca

    modelos_data = [
        ("Nissan", "Sentra"),
        ("Chevrolet", "Silverado"),
        ("Ford", "Focus"),
        ("Honda", "Civic"),
        ("Toyota", "Corolla"),
    ]

    modelos = {}
    for marca_nombre, modelo_nombre in modelos_data:
        modelo, _ = ModeloVehiculo.objects.get_or_create(
            marca=marcas[marca_nombre],
            nombre=modelo_nombre,
        )
        modelos[f"{marca_nombre} {modelo_nombre}"] = modelo

    categorias_nombres = [
        "Motor",
        "Transmision",
        "Carroceria",
        "Electrico",
        "Enfriamiento",
        "Interior",
        "Exterior",
    ]

    categorias = {}
    for nombre in categorias_nombres:
        categoria, _ = CategoriaPieza.objects.get_or_create(nombre=nombre)
        categorias[nombre] = categoria

    piezas_catalogo = [
        ("motor", "Motor"),
        ("transmision", "Transmision"),
        ("alternador", "Electrico"),
        ("defensa delantera", "Carroceria"),
        ("faro izquierdo", "Exterior"),
        ("puerta derecha", "Carroceria"),
        ("cofre", "Carroceria"),
        ("radiador", "Enfriamiento"),
        ("computadora", "Electrico"),
        ("retrovisor", "Exterior"),
    ]

    nombres_piezas = {}
    for pieza_nombre, categoria_nombre in piezas_catalogo:
        nombre_pieza, _ = NombrePieza.objects.get_or_create(
            nombre_normalizado=pieza_nombre,
            defaults={"categoria": categorias[categoria_nombre]},
        )
        nombres_piezas[pieza_nombre] = nombre_pieza

    alias_data = [
        ("defensa delantera", "bumper"),
        ("defensa delantera", "fascia"),
        ("defensa delantera", "parachoques"),
        ("transmision", "caja"),
        ("computadora", "ecu"),
    ]

    for pieza_nombre, alias in alias_data:
        AliasPieza.objects.get_or_create(
            nombre_pieza=nombres_piezas[pieza_nombre],
            alias=alias,
        )

    vehiculos_data = [
        ("Yonke Norte", "Nissan", "Sentra", 2016, "patio B posicion 15"),
        ("Yonke Rio Bravo", "Chevrolet", "Silverado", 2014, "fila 3"),
        ("Yonke Central", "Ford", "Focus", 2013, "rack 2"),
        ("Yonke Frontera", "Honda", "Civic", 2012, "bodega"),
        ("Yonke Norte", "Toyota", "Corolla", 2015, "seccion motores"),
    ]

    vehiculos = []
    for yonke_nombre, marca_nombre, modelo_nombre, anio, ubicacion in vehiculos_data:
        vehiculo, _ = Vehiculo.objects.get_or_create(
            yonke=yonkes[yonke_nombre],
            marca_texto=marca_nombre,
            modelo_texto=modelo_nombre,
            anio=anio,
            defaults={
                "marca": marcas[marca_nombre],
                "modelo": modelos[f"{marca_nombre} {modelo_nombre}"],
                "ubicacion_fisica": ubicacion,
                "estatus": "en_desarme",
                "visibilidad": "visible",
                "observaciones": "Vehiculo demo sin datos sensibles reales.",
                "creado_por": admin_user,
            },
        )
        vehiculos.append(vehiculo)

    piezas_demo = [
        ("motor", "Yonke Norte", "Nissan", "Sentra", 2016, 1, 12500, True, "usada", "disponible", vehiculos[0]),
        ("alternador", "Yonke Norte", "Nissan", "Sentra", 2016, 2, 1200, True, "usada", "disponible", vehiculos[0]),
        ("transmision", "Yonke Rio Bravo", "Chevrolet", "Silverado", 2014, 1, 18500, False, "usada", "disponible", vehiculos[1]),
        ("defensa delantera", "Yonke Central", "Ford", "Focus", 2013, 1, 2300, True, "usada", "disponible", vehiculos[2]),
        ("faro izquierdo", "Yonke Frontera", "Honda", "Civic", 2012, 1, 900, True, "usada", "disponible", vehiculos[3]),
        ("puerta derecha", "Yonke Norte", "Toyota", "Corolla", 2015, 1, 3500, False, "usada", "disponible", vehiculos[4]),
        ("cofre", "Yonke Rio Bravo", "Chevrolet", "Silverado", 2014, 1, 4200, True, "usada", "apartada", vehiculos[1]),
        ("radiador", "Yonke Central", "Ford", "Focus", 2013, 3, 1100, True, "usada", "disponible", None),
        ("computadora", "Yonke Frontera", "Honda", "Civic", 2012, 1, 2800, False, "usada", "pendiente_revision", None),
        ("retrovisor", "Yonke Norte", "Nissan", "Sentra", 2016, 4, 450, True, "usada", "disponible", None),
    ]

    for pieza_nombre, yonke_nombre, marca_nombre, modelo_nombre, anio, cantidad, precio, precio_visible, condicion, estatus, vehiculo in piezas_demo:
        Pieza.objects.get_or_create(
            yonke=yonkes[yonke_nombre],
            nombre=pieza_nombre,
            marca_texto=marca_nombre,
            modelo_texto=modelo_nombre,
            anio_inicio=anio,
            anio_fin=anio,
            defaults={
                "vehiculo": vehiculo,
                "nombre_normalizado": nombres_piezas[pieza_nombre],
                "categoria": nombres_piezas[pieza_nombre].categoria,
                "marca_compatible": marcas[marca_nombre],
                "modelo_compatible": modelos[f"{marca_nombre} {modelo_nombre}"],
                "cantidad": cantidad,
                "precio": precio,
                "precio_visible": precio_visible,
                "condicion": condicion,
                "estatus": estatus,
                "visibilidad": "visible",
                "ubicacion": "ubicacion demo",
                "observaciones": "Pieza demo para presentacion del MVP.",
                "creado_por": admin_user,
            },
        )

    print("Datos demo cargados correctamente.")
    print("Yonkes creados:", Yonke.objects.count())
    print("Marcas creadas:", Marca.objects.count())
    print("Vehiculos creados:", Vehiculo.objects.count())
    print("Piezas creadas:", Pieza.objects.count())


if __name__ == "__main__":
    run()
