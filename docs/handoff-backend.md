# Handoff Backend - MVP Yonkes CANACO

## Estado actual

Backend inicial funcional para el MVP de inventario de yonkes afiliados a CANACO Juarez.

Incluye:

- Django funcionando.
- Django REST Framework funcionando.
- Admin de Django activo.
- Modelos principales creados.
- Migraciones aplicadas.
- Datos iniciales cargados.
- API REST basica funcionando.
- Busqueda de piezas funcionando.
- Catalogos base funcionando.
- Inventario visible desde admin y API.

## Stack

- Python
- Django
- Django REST Framework
- django-filter
- SQLite para desarrollo local
- PostgreSQL recomendado despues
- Pillow para imagenes
- openpyxl para futura importacion Excel

## Estructura principal

```txt
Propuesta Yonkes/
├── apps/
│   ├── accounts/
│   ├── auditoria/
│   ├── busqueda/
│   ├── catalogos/
│   ├── importaciones/
│   ├── inventario/
│   └── yonkes/
├── config/
├── docs/
├── media/
├── scripts/
├── static/
├── templates/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── venv/

## Endpoints disponibles

### Yonkes

GET, POST, PUT, PATCH y DELETE:

```txt
/api/yonkes/
/api/yonkes/{id}/
## Endpoints disponibles

Yonkes:
GET /api/yonkes/
POST /api/yonkes/
GET /api/yonkes/{id}/
PATCH /api/yonkes/{id}/
DELETE /api/yonkes/{id}/

Vehiculos:
GET /api/vehiculos/
POST /api/vehiculos/
GET /api/vehiculos/{id}/
PATCH /api/vehiculos/{id}/
DELETE /api/vehiculos/{id}/

Piezas:
GET /api/piezas/
POST /api/piezas/
GET /api/piezas/{id}/
PATCH /api/piezas/{id}/
DELETE /api/piezas/{id}/

Catalogos:
GET /api/catalogos/marcas/
GET /api/catalogos/modelos/
GET /api/catalogos/categorias/
GET /api/catalogos/nombres-piezas/
GET /api/catalogos/alias-piezas/

Busqueda:
GET /api/busqueda/piezas/

Parametros de busqueda:
pieza
marca
modelo
anio
categoria
yonke
condicion
estatus
solo_disponibles

Ejemplos:
http://127.0.0.1:8000/api/busqueda/piezas/?pieza=motor
http://127.0.0.1:8000/api/busqueda/piezas/?marca=Nissan&modelo=Sentra&anio=2016
http://127.0.0.1:8000/api/busqueda/piezas/?pieza=defensa&solo_disponibles=true
## Comandos utiles

Activar entorno virtual:
.\venv\Scripts\Activate.ps1

Instalar dependencias:
pip install -r requirements.txt

Aplicar migraciones:
python manage.py migrate

Crear superusuario:
python manage.py createsuperuser

Cargar datos iniciales:
python manage.py shell -c "exec(open('scripts/seed_demo_data.py', encoding='utf-8').read()); run()"

Correr servidor:
python manage.py runserver

Validar proyecto:
python manage.py check

Admin local:
http://127.0.0.1:8000/admin/
## Pendientes tecnicos

1. Implementar permisos reales por rol.
2. Implementar autenticacion para API.
3. Asegurar separacion estricta por yonke.
4. Implementar importacion Excel funcional.
5. Implementar logs automaticos.
6. Mejorar carga de imagenes por API.
7. Migrar de SQLite a PostgreSQL en etapa posterior.
8. Documentar contrato final de API.
9. Revisar seguridad antes de cualquier despliegue.
10. Evitar uso de datos reales sensibles en validacion local.

## Restricciones

No construir todavia:

- Fiscalia.
- Pagos.
- E-commerce.
- Facturacion.
- App movil nativa.
- Requisiciones completas entre yonkes.
- WhatsApp Business API.
- Despliegue productivo.
- Datos legales reales.
- Documentos sensibles reales.

## Estado de entrega

Backend base funcional para validacion local.

Incluye:

- Admin funcional.
- API REST basica.
- Datos iniciales.
- Inventario consultable.
- Busqueda de piezas.

No es backend productivo todavia.
