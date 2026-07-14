# Informe técnico de desarrollo frontend — Red de Yonkes

## 1. Resumen ejecutivo del frontend

Este documento analiza exclusivamente el frontend localizado en el repositorio. La aplicación es un sistema web renderizado en servidor con Django Templates, HTML5, CSS3 personalizado y JavaScript nativo. No se encontró un pipeline de compilación frontend, `package.json`, bundler, Tailwind, React, Vue ni dependencias npm. La UI se sirve mediante templates en `templates/`, estilos globales en `static/css/base.css` y comportamiento global en `static/js/base.js`; los recursos estáticos se enlazan con `{% static %}` desde `templates/layout/base.html` y las páginas de acceso.

Confirmado en código:
- El sistema usa Django 6.0.5, Django Templates, `django.contrib.staticfiles`, `STATICFILES_DIRS = [BASE_DIR / 'static']`, `MEDIA_URL` y `MEDIA_ROOT` para recursos estáticos y archivos subidos.
- El layout principal reutiliza navbar, buscador global, menú de usuario, sidebar, breadcrumbs, área de mensajes, contenedor principal y footer.
- Las pantallas implementadas corresponden a dashboard, yonkes, vehículos, piezas, búsqueda, catálogos, importaciones, auditoría, usuarios, login, registro, perfil y configuración.
- La mayor parte de las pantallas hereda de `layout/base.html`; login y registro usan documentos HTML independientes para una experiencia de acceso separada.
- Las tablas y listados se renderizan principalmente en servidor con ciclos `{% for %}`; la interactividad JavaScript comprobada es global: drawer lateral, menú de usuario, validación mínima de búsqueda global, colapso de filtros avanzados de búsqueda y cierre de mensajes.

Inferible razonablemente:
- La metodología visual es de sistema de diseño propio sobre CSS variables y clases reutilizables, con inspiración documentada en README hacia Material Design, Tabler UI, Flowbite, Tailwind UI y Shadcn UI; sin embargo, esas librerías no se cargan como dependencias reales.
- El enfoque responsive es mobile-first porque la hoja de estilos define componentes base para pantallas pequeñas y media queries progresivas para 640, 768, 900, 1024 y 1180 px.

No determinable desde el repositorio:
- Herramienta de diseño usada, cronología histórica real, pruebas manuales ejecutadas, navegadores comprobados, dispositivos físicos usados, retroalimentación de usuarios y decisiones humanas de diseño.

## 2. Tecnologías identificadas

| Tecnología o recurso | Función dentro del frontend | Archivos donde se utiliza | Evidencia encontrada |
|---|---|---|---|
| HTML5 | Estructura de todas las pantallas | `templates/**/*.html` | Declaraciones `<!DOCTYPE html>` en login/registro y plantillas con secciones, formularios, tablas, tarjetas y enlaces. |
| Django Templates | Renderizado de UI en servidor | `templates/layout/base.html`, todos los templates de módulos | Uso de `{% extends %}`, `{% block %}`, `{% static %}`, `{% url %}`, `{% for %}`, `{% if %}` y variables `{{ }}`. |
| CSS3 personalizado | Sistema visual completo | `static/css/base.css` | Variables `:root`, clases `.btn`, `.card`, `.table`, `.sidebar-link`, `.form-control`, media queries. |
| JavaScript nativo | Interactividad global | `static/js/base.js`, enlazado en `layout/base.html` | IIFE con `querySelector`, `addEventListener`, `classList`, `matchMedia` y manipulación ARIA. |
| Django staticfiles | Carga de CSS/JS | `config/settings.py`, `templates/layout/base.html`, login, registro | `STATIC_URL`, `STATICFILES_DIRS` y `{% static 'css/base.css' %}` / `{% static 'js/base.js' %}`. |
| Media files | Visualización/carga de imágenes y archivos | `config/settings.py`, templates de vehículos/piezas/catálogos/importaciones | `MEDIA_URL`, `MEDIA_ROOT`, `{{ imagen.url }}`, formularios `enctype="multipart/form-data"`. |
| SVG inline | Iconografía del layout y acciones | `templates/layout/base.html`, `templates/dashboard/index.html`, `templates/busqueda/piezas.html` | Íconos `<svg>` definidos directamente; no hay paquete de iconos instalado. |
| Bootstrap Icons | Recurso declarado documentalmente | `README.md` | README lo enumera, pero no se encontró carga de CDN, CSS ni clases `bi`. |
| Bootstrap/Tailwind | No comprobado como dependencia | N/A | No hay `package.json`, CDN Bootstrap/Tailwind ni clases utilitarias típicas. |
| Tablas HTML responsive | Listados administrativos | `templates/*/list.html` | `div.table-responsive` con `<table class="table">`; no se encontró DataTables. |
| Formularios Django + HTML manual | Captura y filtros | `apps/*/forms.py`, `templates/*/form.html`, `templates/*/list.html` | Forms de Django agregan clases; filtros son inputs/selects escritos manualmente. |
| Mensajes Django | Alertas visuales | `templates/layout/base.html`, vistas HTML | Bloque `{% if messages %}` y botones `data-dismiss-message`. |
| OpenPyXL/Pillow | Soporte indirecto para importación e imágenes | `requirements.txt`, forms/importaciones/inventario/catalogos | Dependencias backend que habilitan archivos Excel/imágenes visibles, no librerías UI. |

## 3. Estructura de archivos

```text
Yonkes/
├── config/
│   ├── settings.py                  # Configuración de templates, static y media
│   └── urls.py                      # Inclusión de rutas HTML y media en debug
├── static/
│   ├── css/base.css                 # Única hoja de estilos global
│   └── js/base.js                   # Único script global
├── templates/
│   ├── layout/base.html             # Plantilla base reutilizable
│   ├── accounts/
│   │   ├── login.html               # Acceso, no extiende base
│   │   ├── register.html            # Registro, no extiende base
│   │   ├── profile.html             # Perfil
│   │   └── settings.html            # Configuración
│   ├── dashboard/
│   │   ├── index.html               # Dashboard
│   │   └── module_placeholder.html  # Placeholder genérico heredado
│   ├── yonkes/{list,form,detail}.html
│   ├── vehiculos/{list,form,detail}.html
│   ├── piezas/{list,form,detail}.html
│   ├── busqueda/piezas.html
│   ├── catalogos/{index,list,form}.html
│   ├── importaciones/{list,form,detail}.html
│   ├── usuarios/{list,form,detail}.html
│   └── auditoria/{list,detail}.html
├── apps/
│   ├── */html_urls.py               # Rutas HTML por módulo
│   ├── */html_views.py              # Contexto y selección de template
│   └── */forms.py                   # Formularios que inyectan clases CSS
└── README.md                        # Descripción declarada del frontend
```

Responsabilidades:
- `templates/layout/base.html` es global: define estructura de aplicación autenticada, navegación, mensajes, bloques `title`, `breadcrumbs`, `page_title` y `content`.
- `static/css/base.css` es global y concentra estilos generales y específicos; no hay CSS por módulo.
- `static/js/base.js` es global y se carga al final de `base.html`; login y registro no cargan este script.
- `templates/<modulo>/` contiene vistas específicas. Los CRUD usan patrones repetidos: listado con filtros, formulario de alta/edición y detalle.
- `apps/*/forms.py` afecta directamente la presentación porque asigna clases `form-control`, `form-select`, `form-checkbox` y `form-textarea` a widgets.
- `apps/*/html_urls.py` conecta URLs visibles con templates; `apps/*/html_views.py` determina variables de contexto, filtros, paginación inexistente o datos mostrados.

Herencia y reutilización:
- Heredan de `layout/base.html`: dashboard, yonkes, vehículos, piezas, búsqueda, catálogos, importaciones, auditoría, usuarios, perfil y configuración.
- No heredan de `layout/base.html`: login y registro; ambos incluyen `base.css` directamente y renderizan una pantalla centrada de acceso.
- Se evita duplicar estructura global mediante bloques. La duplicación todavía existe en patrones de formulario/listado porque no hay includes parciales para campos, tablas, paginación o cards.

## 4. Inventario de pantallas

| Nº | Pantalla | Ruta o URL | Template | CSS | JS | Función principal | Estado |
|---:|---|---|---|---|---|---|---|
| 1 | Login | `/login/`, `/accounts/login/` | `templates/accounts/login.html` | `static/css/base.css` | No carga `base.js` | Acceso con usuario/contraseña | Implementada y funcional |
| 2 | Registro | `/register/` | `templates/accounts/register.html` | `static/css/base.css` | No carga `base.js` | Alta de cuenta con formulario Django | Implementada y funcional |
| 3 | Dashboard | `/`, `/dashboard/` | `templates/dashboard/index.html` | `base.css` | `base.js` | Métricas, búsqueda rápida, accesos y últimas piezas | Implementada y funcional |
| 4 | Placeholder genérico | Rutas antiguas en `apps/dashboard/urls.py` cuando no quedan sobreescritas | `templates/dashboard/module_placeholder.html` | `base.css` | `base.js` | Mensaje de módulo en construcción | Placeholder / parcialmente eclipsado por rutas reales |
| 5 | Listado de yonkes | `/yonkes/` | `templates/yonkes/list.html` | `base.css` | `base.js` | Directorio filtrable de yonkes | Implementada y funcional |
| 6 | Nuevo yonke | `/yonkes/nuevo/` | `templates/yonkes/form.html` | `base.css` | `base.js` | Captura de datos del yonke | Implementada y funcional |
| 7 | Editar yonke | `/yonkes/<id>/editar/` | `templates/yonkes/form.html` | `base.css` | `base.js` | Edición de datos | Implementada y funcional |
| 8 | Detalle de yonke | `/yonkes/<id>/` | `templates/yonkes/detail.html` | `base.css` | `base.js` | Consulta detallada | Implementada y funcional |
| 9 | Listado de vehículos | `/vehiculos/` | `templates/vehiculos/list.html` | `base.css` | `base.js` | Inventario de unidades filtrable | Implementada y funcional |
| 10 | Nuevo vehículo | `/vehiculos/nuevo/` | `templates/vehiculos/form.html` | `base.css` | `base.js` | Captura con imagen | Implementada y funcional |
| 11 | Editar vehículo | `/vehiculos/<id>/editar/` | `templates/vehiculos/form.html` | `base.css` | `base.js` | Edición con imagen | Implementada y funcional |
| 12 | Detalle de vehículo | `/vehiculos/<id>/` | `templates/vehiculos/detail.html` | `base.css` | `base.js` | Consulta y piezas asociadas | Implementada y funcional |
| 13 | Listado de piezas | `/piezas/` | `templates/piezas/list.html` | `base.css` | `base.js` | Inventario de autopartes filtrable | Implementada y funcional |
| 14 | Nueva pieza | `/piezas/nueva/` | `templates/piezas/form.html` | `base.css` | `base.js` | Captura de pieza con imagen | Implementada y funcional |
| 15 | Editar pieza | `/piezas/<id>/editar/` | `templates/piezas/form.html` | `base.css` | `base.js` | Edición de pieza | Implementada y funcional |
| 16 | Detalle de pieza | `/piezas/<id>/` | `templates/piezas/detail.html` | `base.css` | `base.js` | Consulta de pieza, precio visible y datos técnicos | Implementada y funcional |
| 17 | Búsqueda de piezas | `/busqueda/` | `templates/busqueda/piezas.html` | `base.css` | `base.js` | Búsqueda avanzada con filtros colapsables | Implementada y funcional |
| 18 | Índice de catálogos | `/catalogos/` | `templates/catalogos/index.html` | `base.css` | `base.js` | Tarjetas de catálogos disponibles | Implementada y funcional |
| 19 | Listado de marcas | `/catalogos/marcas/` | `templates/catalogos/list.html` | `base.css` | `base.js` | CRUD visual de marcas | Implementada y funcional |
| 20 | Alta/edición marca | `/catalogos/marcas/nuevo/`, `/catalogos/marcas/<id>/editar/` | `templates/catalogos/form.html` | `base.css` | `base.js` | Formulario con posible logo | Implementada y funcional |
| 21 | Eliminación marca | `/catalogos/marcas/<id>/eliminar/` | Sin template propio; usa vista con redirect | N/A | N/A | Elimina y redirige | Implementada sin pantalla de confirmación |
| 22 | Listado/modelos + alta/edición/eliminación | `/catalogos/modelos/...` | `catalogos/list.html`, `catalogos/form.html` | `base.css` | `base.js` | CRUD modelos | Implementada y funcional |
| 23 | Listado/categorías + alta/edición/eliminación | `/catalogos/categorias/...` | `catalogos/list.html`, `catalogos/form.html` | `base.css` | `base.js` | CRUD categorías | Implementada y funcional |
| 24 | Listado/nombres piezas + alta/edición/eliminación | `/catalogos/nombres-piezas/...` | `catalogos/list.html`, `catalogos/form.html` | `base.css` | `base.js` | CRUD nombres normalizados | Implementada y funcional |
| 25 | Listado/alias piezas + alta/edición/eliminación | `/catalogos/alias-piezas/...` | `catalogos/list.html`, `catalogos/form.html` | `base.css` | `base.js` | CRUD alias | Implementada y funcional |
| 26 | Importaciones | `/importaciones/` | `templates/importaciones/list.html` | `base.css` | `base.js` | Historial de cargas Excel | Implementada y funcional |
| 27 | Nueva importación | `/importaciones/nueva/` | `templates/importaciones/form.html` | `base.css` | `base.js` | Carga de archivo Excel | Implementada y funcional |
| 28 | Detalle importación | `/importaciones/<id>/` | `templates/importaciones/detail.html` | `base.css` | `base.js` | Estado, errores y resumen | Implementada y funcional |
| 29 | Auditoría | `/auditoria/` | `templates/auditoria/list.html` | `base.css` | `base.js` | Filtros y timeline/tabla de eventos | Implementada y funcional |
| 30 | Detalle auditoría | `/auditoria/<id>/` | `templates/auditoria/detail.html` | `base.css` | `base.js` | Datos y JSON de cambios | Implementada y funcional |
| 31 | Usuarios | `/usuarios/` | `templates/usuarios/list.html` | `base.css` | `base.js` | Listado filtrable de usuarios | Implementada y funcional |
| 32 | Nuevo usuario | `/usuarios/nuevo/` | `templates/usuarios/form.html` | `base.css` | `base.js` | Alta de usuario | Implementada y funcional |
| 33 | Editar usuario | `/usuarios/<id>/editar/` | `templates/usuarios/form.html` | `base.css` | `base.js` | Edición de usuario | Implementada y funcional |
| 34 | Detalle usuario | `/usuarios/<id>/` | `templates/usuarios/detail.html` | `base.css` | `base.js` | Consulta de usuario | Implementada y funcional |
| 35 | Perfil | `/perfil/` | `templates/accounts/profile.html` | `base.css` | `base.js` | Consulta del propio perfil | Implementada y funcional |
| 36 | Configuración | `/configuracion/` | `templates/accounts/settings.html` | `base.css` | `base.js` | Edición de datos propios | Implementada y funcional |

## 5. Orden recomendado de documentación

La memoria ya contiene inicio de sesión, plantilla base/barra lateral y dashboard. El orden sugerido para continuar es:

- **3.2.4 Sistema de listados, filtros y estados vacíos.** Debe ir antes de módulos individuales porque `yonkes`, `vehiculos`, `piezas`, `usuarios`, `auditoria` e `importaciones` repiten el patrón de filtros GET, tabla responsive, cards móviles y empty states.
- **3.2.5 Administración de yonkes.** Es un catálogo operativo base: otros módulos muestran `yonke` como asociación o filtro.
- **3.2.6 Administración de catálogos.** Marcas, modelos, categorías, nombres y alias alimentan selects de vehículos, piezas y búsqueda.
- **3.2.7 Gestión de vehículos.** Depende de yonkes y catálogos de marca/modelo; además introduce imagen principal y relación con piezas.
- **3.2.8 Gestión de piezas.** Es el módulo central de inventario; depende de vehículos y catálogos, y alimenta búsqueda/dashboard.
- **3.2.9 Búsqueda avanzada de piezas.** Debe documentarse después de piezas porque consulta registros existentes y usa filtros por vehículo, categoría, estado y yonke.
- **3.2.10 Importación de información.** Complementa alta manual mediante archivo; conviene describirlo tras CRUD de inventario.
- **3.2.11 Usuarios, perfil y configuración.** Puede describirse de manera frontend sin abordar seguridad profunda: listados, formularios y vistas personales.
- **3.2.12 Auditoría.** Visualiza actividad y cambios; se relaciona con módulos anteriores como consulta administrativa.
- **3.2.13 Responsive, accesibilidad e interactividad.** Cierra la sección al explicar ajustes transversales y `base.js`.

## 6. Análisis detallado por módulo

### 6.1 Módulo de yonkes

**Objetivo.** Administrar el directorio de yonkes: listar, filtrar, crear, editar y consultar detalles. Muestra nombre, razón social, contacto, estatus, dirección, contacto principal y notas internas condicionadas.

**Pantallas.**
- Listado `/yonkes/`: `templates/yonkes/list.html` extiende `layout/base.html`. Usa bloques `title`, `breadcrumbs`, `page_title`, `content`. Recibe `yonkes`, `filters`, `estatus_choices` y banderas de acciones. Contiene filtros GET por nombre/razón social, estatus, mostrar contacto y contacto; presenta cards y tabla responsive; muestra empty state si no hay registros.
- Formulario `/yonkes/nuevo/` y `/yonkes/<id>/editar/`: `templates/yonkes/form.html`. Usa `YonkeForm`; divide campos en información principal, contacto, operación y notas. Botones cancelar/guardar. La acción cambia según `is_edit`.
- Detalle `/yonkes/<id>/`: `templates/yonkes/detail.html`. Hero con estado mediante badge, resumen, acciones regresar/editar, panel de información general y condicionales de contacto/datos internos.

**Procedimiento técnico reconstruido.** 1) Crear ruta HTML y vista de listado. 2) Extender `layout/base.html`. 3) Definir filtros GET manuales. 4) Renderizar cards para móvil y tabla para escritorio. 5) Crear `YonkeForm` con clases CSS. 6) Reutilizar template para alta/edición con `is_edit`. 7) Crear detalle con hero, badges y grid. 8) Integrar mensajes de Django desde base.

**Flujo.** El usuario entra al listado, filtra o limpia. Desde “Nuevo yonke” abre formulario; al guardar la vista redirige al listado/detalle según implementación de vista. Desde listado puede ver detalle y, si aplica, editar. En edición, cancelar regresa al detalle.

| Elemento descrito | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Filtros de listado | `templates/yonkes/list.html` | `form method="get"` | Envia criterios por URL. |
| Cards + tabla | `templates/yonkes/list.html` | `.list-card`, `.table-responsive` | Dos representaciones para responsive. |
| Formulario estilizado | `apps/yonkes/forms.py` | `YonkeForm.__init__` | Inyecta clases de controles. |
| Campos manuales | `templates/yonkes/form.html` | `{% with field=form.nombre %}` | Controla agrupación visual. |
| Detalle | `templates/yonkes/detail.html` | `.detail-hero`, `.detail-grid` | Patrón de consulta. |

### 6.2 Módulo de catálogos

**Objetivo.** Administrar datos base: marcas, modelos de vehículo, categorías de pieza, nombres normalizados y alias de piezas. Las acciones visibles son consultar listados, filtrar, crear, editar y eliminar sin confirmación HTML propia.

**Pantallas.**
- Índice `/catalogos/`: `catalogos/index.html` muestra cards generadas desde `cards` y enlaces a cada catálogo.
- Listados `/catalogos/<slug>/`: `catalogos/list.html` usa `items`, `columns`, `filters`, `catalog_title`, `create_url`; renderiza formulario de búsqueda, tabla dinámica y acciones editar/eliminar.
- Formulario `/catalogos/<slug>/nuevo/` y edición: `catalogos/form.html`; recorre `form` y muestra errores/ayudas; si hay archivos (marca/logo), usa `multipart/form-data` desde la vista/template.
- Eliminación: rutas `/eliminar/`; las vistas hacen operación y redirect, no se encontró template de confirmación.

**Procedimiento técnico reconstruido.** 1) Definir catálogo por configuración de vista. 2) Crear índice de cards. 3) Crear listado genérico basado en columnas. 4) Crear formulario genérico que itera campos. 5) Estilizar forms desde `BaseStyledModelForm`. 6) Agregar acciones por registro.

**Flujo.** Desde sidebar/dashboard se accede al índice; se elige catálogo; se filtra por búsqueda/activo/visibilidad según contexto; se crea o edita registro; eliminar se acciona desde el listado y redirige.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Rutas de todos los catálogos | `apps/catalogos/html_urls.py` | `catalogos/...` | Define URLs reales. |
| Forms genéricos | `apps/catalogos/forms.py` | `BaseStyledModelForm` | Homologa clases CSS. |
| Índice | `templates/catalogos/index.html` | `cards` | Navegación por tarjetas. |
| Listado dinámico | `templates/catalogos/list.html` | `columns`, `items` | Reutiliza un template para varios catálogos. |
| Formulario dinámico | `templates/catalogos/form.html` | `{% for field in form %}` | Evita duplicar templates por catálogo. |

### 6.3 Módulo de vehículos

**Objetivo.** Gestionar unidades/vehículos asociados a yonkes, con marca, modelo, año, versión, motor, transmisión, VIN, número de serie, ubicación, observaciones, estado, visibilidad e imagen principal.

**Pantallas.**
- Listado `/vehiculos/`: filtros por búsqueda, yonke, marca, modelo, estatus, visibilidad y año; cards con imagen y tabla.
- Formulario `/vehiculos/nuevo/` y edición: `vehiculos/form.html`; `enctype="multipart/form-data"` para imagen; campos agrupados en identificación, datos técnicos, ubicación/estado y notas.
- Detalle `/vehiculos/<id>/`: hero con imagen o emblema, badges de estatus/visibilidad, grid de datos y listado/acciones de piezas asociadas.

**Procedimiento técnico reconstruido.** 1) Crear `VehiculoForm` y asignar clases. 2) Configurar select dependiente conceptual de marca/modelo en servidor (el queryset de modelo cambia según marca enviada). 3) Construir formulario con carga de archivo. 4) Crear listado con filtros GET. 5) Crear detalle con imagen y relación a piezas.

**Flujo.** El usuario filtra vehículos; crea uno con imagen opcional; consulta detalle; desde detalle puede editar o crear pieza contextual asociada al vehículo.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Rutas | `apps/inventario/html_urls.py` | `vehiculos/...` | CRUD visible. |
| Formulario | `apps/inventario/forms.py` | `VehiculoForm` | Campos y clases. |
| Carga de imagen | `templates/vehiculos/form.html` | `multipart/form-data` | Permite subir imagen principal. |
| Visualización imagen | `templates/vehiculos/list.html`, `detail.html` | `imagen_principal.url` | Renderiza miniatura/hero. |
| Detalle con piezas | `templates/vehiculos/detail.html` | lista de piezas | Enlaza inventario relacionado. |

### 6.4 Módulo de piezas

**Objetivo.** Administrar autopartes del inventario. Permite listar, filtrar, crear, editar y ver detalle. Muestra compatibilidad vehicular, categoría, condición, estatus, visibilidad, cantidad, precio, ubicación, imagen y observaciones.

**Pantallas.**
- Listado `/piezas/`: filtros por q, yonke, vehículo, categoría, condición, estatus, visibilidad, precio mínimo/máximo y año. Cards y tabla; acciones ver/editar.
- Formulario `/piezas/nueva/` y edición: `piezas/form.html`; `multipart/form-data`; campos de identificación/compatibilidad, inventario/precio/ubicación y observaciones. Puede recibir `vehiculo_context`.
- Detalle `/piezas/<id>/`: hero con imagen de pieza o vehículo, badges, stats, precio visible condicionalmente, información general, compatibilidad e inventario.

**Procedimiento técnico reconstruido.** 1) Definir `PiezaForm` con campos de inventario y CSS. 2) Incorporar catálogos en selects. 3) Agregar carga de imagen. 4) Implementar listado filtrable. 5) Crear detalle con fallback de imagen y badges. 6) Relacionar con búsqueda y dashboard.

**Flujo.** El usuario consulta piezas; filtra; crea pieza manualmente o desde detalle de vehículo; guarda; visualiza detalle; edita desde listado/detalle.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Filtros | `templates/piezas/list.html` | inputs/selects GET | Segmenta inventario. |
| Formulario | `apps/inventario/forms.py` | `PiezaForm` | Define campos visibles. |
| Contexto vehículo | `templates/piezas/form.html` | `vehiculo_context` | Permite alta relacionada. |
| Precio condicional | `templates/piezas/detail.html` | `precio_visible` | Comportamiento visible condicional. |
| Cards/tabla | `templates/piezas/list.html` | `.list-card`, `.table` | Responsive. |

### 6.5 Módulo de búsqueda

**Objetivo.** Buscar piezas disponibles o filtradas por atributos de pieza, vehículo y yonke. Es una pantalla de consulta tipo marketplace.

**Pantallas.**
- `/busqueda/`: `templates/busqueda/piezas.html`; formulario GET con búsqueda principal `pieza`, filtros por marca, modelo, año, categoría, condición, estatus, yonke y checkbox `solo_disponibles`. Tiene botón para colapsar filtros avanzados mediante `base.js`. Resultados en cards con imagen, badges, detalle, compatibilidad, precio y contacto visible.

**Procedimiento técnico reconstruido.** 1) Crear formulario GET. 2) Separar búsqueda principal de filtros avanzados. 3) Renderizar resultados con cards. 4) Agregar empty states según existan filtros o no. 5) Programar colapso visual en JS.

**Flujo.** El usuario escribe pieza desde navbar, dashboard o pantalla de búsqueda; la petición GET llega a `/busqueda/`; se muestran filtros activos y resultados; puede abrir detalle de pieza.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Buscador global | `templates/layout/base.html` | `data-global-search` | Redirige a búsqueda. |
| Validación de búsqueda | `static/js/base.js` | submit de `searchForm` | Evita envío vacío global. |
| Filtros avanzados | `templates/busqueda/piezas.html` | `advanced-search-filters` | Panel colapsable. |
| Toggle filtros | `static/js/base.js` | `data-toggle-search-filters` | Alterna `.is-collapsed`. |
| Resultados | `templates/busqueda/piezas.html` | `resultados` | Cards de piezas. |

### 6.6 Módulo de importaciones

**Objetivo.** Registrar cargas de archivo Excel y visualizar su estado, errores y resultados. Acciones: listar importaciones, crear nueva carga y consultar detalle.

**Pantallas.**
- Listado `/importaciones/`: historial con filtros/tabla o cards según template, estado y fechas.
- Formulario `/importaciones/nueva/`: carga de `archivo`, selección de `yonke` y `tipo_importacion`, `multipart/form-data`.
- Detalle `/importaciones/<id>/`: estado, archivo, totales, errores y mensajes.

**Procedimiento técnico reconstruido.** 1) Crear `ImportacionExcelForm`. 2) Estilizar widgets. 3) Crear formulario de carga. 4) Crear listado de historial. 5) Crear detalle para resultados/errores.

**Flujo.** El usuario abre historial, entra a nueva importación, selecciona archivo y tipo, envía, y después consulta detalle del procesamiento.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Rutas | `apps/importaciones/html_urls.py` | `importaciones/...` | Tres pantallas visibles. |
| Form | `apps/importaciones/forms.py` | `ImportacionExcelForm` | Campos de carga. |
| Template carga | `templates/importaciones/form.html` | `multipart/form-data` | Permite archivo. |
| Historial | `templates/importaciones/list.html` | tabla/cards | Consulta de cargas. |
| Detalle | `templates/importaciones/detail.html` | estado/errores | Resultado de operación. |

### 6.7 Módulo de usuarios, perfil y configuración

**Objetivo.** Gestionar usuarios y datos propios desde UI. Para respetar el alcance, solo se documenta estructura visual y comportamiento condicional, no controles de seguridad.

**Pantallas.**
- Usuarios `/usuarios/`: filtros por búsqueda, rol, yonke y activo; cards y tabla; acciones ver/editar.
- Nuevo/editar usuario: `usuarios/form.html`; campos de cuenta, acceso y estado; password requerido en alta y opcional en edición según forms.
- Detalle: `usuarios/detail.html`; hero con inicial, rol, estado y grid de datos.
- Perfil `/perfil/`: datos del usuario actual.
- Configuración `/configuracion/`: formulario de nombre, apellido, email y teléfono.

**Procedimiento técnico reconstruido.** 1) Crear forms `UsuarioCreateForm`, `UsuarioEditForm`, `ProfileSettingsForm`. 2) Crear listado con filtros. 3) Crear formulario segmentado. 4) Crear detalle y perfil con `detail-grid`. 5) Reutilizar mensajes globales para resultados.

**Flujo.** Desde sidebar se consulta usuarios; se filtra; se abre nuevo/editar; se guarda; el usuario también accede a perfil desde menú superior y puede editar configuración.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Rutas usuario | `apps/accounts/html_urls.py` | `usuarios/...` | CRUD de usuarios. |
| Rutas perfil | `apps/accounts/auth_urls.py` | `perfil`, `configuracion` | Pantallas personales. |
| Forms | `apps/accounts/forms.py` | `UsuarioBaseForm`, etc. | Campos y clases. |
| Listado | `templates/usuarios/list.html` | filtros/cards/tabla | Consulta administrativa. |
| Perfil | `templates/accounts/profile.html` | `request.user`, `profile` | Datos propios. |

### 6.8 Módulo de auditoría

**Objetivo.** Consultar eventos registrados del sistema mediante filtros y detalle. Se documenta como frontend de consulta, no como mecanismo de seguridad.

**Pantallas.**
- Listado `/auditoria/`: filtros por búsqueda general, usuario, yonke, acción, entidad y rango de fechas. Muestra timeline cards y tabla con detalle.
- Detalle `/auditoria/<id>/`: hero con acción/entidad, grid de resumen y bloque `<pre>` para JSON de cambios.

**Procedimiento técnico reconstruido.** 1) Crear filtros GET. 2) Crear representación timeline para lectura rápida. 3) Agregar tabla responsive para datos tabulares. 4) Crear detalle con JSON sin transformar.

**Flujo.** El usuario filtra eventos, selecciona “Ver detalle”, revisa resumen y vuelve al listado.

| Elemento | Archivo | Relacionado | Explicación |
|---|---|---|---|
| Filtros | `templates/auditoria/list.html` | `audit-filter-form` | Consulta por criterios. |
| Timeline | `templates/auditoria/list.html` | `.audit-timeline-card` | Visual alterna. |
| Tabla | `templates/auditoria/list.html` | `.admin-ops-table-wrap` | Vista tabular. |
| JSON | `templates/auditoria/detail.html` | `.json-block` | Presenta cambios. |

## 7. Formularios

Formularios confirmados:
- **Login** (`accounts/login.html`): HTML manual, POST, campos `username` texto y `password` password, hidden `next`, requeridos, botones iniciar sesión/crear cuenta, error global `error`.
- **Registro** (`accounts/register.html` + `RegisterForm`): Django form iterado, campos usuario, nombre, apellido, email, contraseña, confirmación, teléfono, rol y yonke; muestra help text y errores por campo.
- **Yonke** (`yonkes/form.html` + `YonkeForm`): nombre, razón social, teléfono, WhatsApp, email, dirección textarea, contacto principal, estatus select, mostrar contacto checkbox, notas internas textarea. Alta y edición comparten template; acción y textos dependen de `is_edit`.
- **Vehículo** (`vehiculos/form.html` + `VehiculoForm`): yonke, marca, modelo, imagen principal file, año, versión, motor, transmisión, VIN, número de serie, ubicación física, observaciones textarea, datos legales internos textarea, estatus, visibilidad.
- **Pieza** (`piezas/form.html` + `PiezaForm`): yonke, vehículo, nombre, nombre normalizado, alias local, categoría, marca compatible, modelo compatible, imagen principal file, año inicial/final, condición, estatus, visibilidad, precio, precio visible checkbox, cantidad, ubicación, observaciones.
- **Búsqueda** (`busqueda/piezas.html`): GET manual, pieza, marca, modelo, año, categoría, condición, estatus, yonke y solo disponibles.
- **Catálogos** (`catalogos/form.html` + forms de catálogo): marca incluye logo file; modelo incluye marca/nombre; categoría nombre; nombre de pieza categoría/nombre normalizado; alias nombre_pieza/alias/activo. Template genérico itera campos.
- **Importación** (`importaciones/form.html` + `ImportacionExcelForm`): yonke, tipo_importacion, archivo file; usa `multipart/form-data`.
- **Usuarios** (`usuarios/form.html` + forms): username, first_name, last_name, email, telefono, rol, yonke, activo y password; diferencia alta/edición por `UsuarioCreateForm` y `UsuarioEditForm`.
- **Configuración** (`accounts/settings.html` + `ProfileSettingsForm`): first_name, last_name, email, telefono.
- **Filtros de listados**: HTML manual con método GET en yonkes, vehículos, piezas, usuarios, auditoría y posiblemente importaciones/catálogos.

No se encontró previsualización JavaScript de imágenes. La validación visible se basa en errores de Django (`field.errors`, `form.non_field_errors`), atributos HTML (`required`, tipos `date`, `number`, `password`) y clases `has-error`, `field-error`, `form-errors`.

## 8. Tablas y listados

Patrón común:
- Filtros se envían por GET y conservan valores con `filters.<campo>`.
- Se usa tabla HTML dentro de `.table-responsive` para escritorio/tablet y cards `.list-card` o variantes para móvil.
- No se encontró paginación visual ni librería de tabla; ordenamiento es de servidor en vistas cuando existe `order_by`.
- Acciones por registro: ver, editar y eliminar según módulo; eliminación de catálogos no tiene pantalla de confirmación.
- Empty states: mensajes en listados cuando no hay registros.

Listados principales:
- Yonkes: nombre, razón social, teléfono, WhatsApp, email, contacto principal, estatus, mostrar contacto y acciones.
- Vehículos: imagen, yonke, marca/modelo/año, versión, motor/transmisión, estatus, visibilidad, acciones.
- Piezas: imagen, nombre, yonke, vehículo, categoría, condición, estatus, visibilidad, cantidad, precio, ubicación, acciones.
- Búsqueda: resultados tipo card con imagen, badges, detalle, compatibilidad, precio y contacto.
- Usuarios: usuario, nombre, email, rol, yonke, teléfono, activo, fecha de registro y acciones.
- Auditoría: fecha, usuario, yonke, acción, entidad, ID entidad, IP y acciones; además timeline.
- Importaciones: historial con estado, tipo, archivo, fechas/totales/errores según template.
- Catálogos: columnas dinámicas según catálogo.

## 9. Componentes reutilizables

- **Navbar global**: `layout/base.html`; reutilizada por todas las pantallas autenticadas; contiene marca, toggle, búsqueda, menú de usuario.
- **Sidebar**: `layout/base.html`; enlaces por módulo y clase activa por `active_module`.
- **Breadcrumbs**: bloque `breadcrumbs` en cada template heredado; permite ruta contextual.
- **Page title**: bloque `page_title`.
- **Mensajes/alertas**: `layout/base.html` renderiza `messages` con botón de cierre manejado por JS.
- **Cards**: clases `.card`, `.list-card`, `.dashboard-action-card`, `.detail-stat-card` en CSS; reutilizadas en módulos.
- **Badges**: `.badge-*` para estados, roles, visibilidad, condición y filtros.
- **Tablas responsive**: `.table-responsive .table` en listados.
- **Form controls**: `.form-control`, `.form-select`, `.form-checkbox`, `.form-textarea` aplicadas desde forms y templates.
- **Empty state**: `.empty-state` en listados, dashboard y búsqueda.
- **Detail hero/grid**: `.detail-hero`, `.detail-grid`, `.detail-field` en detalles.
- **Drawer móvil**: sidebar + backdrop + `body.sidebar-open`, controlado por `base.js`.

Ventaja técnica: centralizar layout, estilos y comportamiento reduce cambios repetidos; la desventaja es que `base.css` concentra muchas reglas globales y específicas.

## 10. CSS y diseño visual

Confirmado:
- Paleta basada en variables: fondo `#f3f6f4`, superficie blanca, primario verde petróleo `#0f766e`, éxito `#067647`, advertencia `#b54708`, peligro `#b42318`, info `#175cd3`.
- Tipografía: variable `--font-sans` con Inter como primera opción y fallback system UI; no se carga fuente externa.
- Espaciado: variables `--space-1` a `--space-10`.
- Bordes: radios `--radius-xs` a `--radius-xl` y pill.
- Sombras: `--shadow-xs`, `--shadow-sm`, `--shadow-md`.
- Estados activos: `.sidebar-link.is-active`, badges, focus visible global.
- Formularios: clases `form-group`, `form-label`, `form-control`, `form-select`, `form-checkbox`, `form-textarea`, `has-error`, `field-error`.
- Tablas: `.table`, `.table-responsive`.
- Diseño de acciones: `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`.
- Convención de nombres: mezcla de componentes globales (`card`, `btn`, `badge`) y nombres por módulo (`dashboard-*`, `search-*`, `user-*`, `admin-ops-*`, `capture-*`).

Problemas de mantenibilidad observables:
- Único archivo CSS muy extenso para todo el sistema; facilita carga única, pero dificulta modularidad.
- Hay estilos específicos de módulo en el mismo archivo global.
- No hay componentes parciales ni CSS por pantalla.

## 11. JavaScript e interactividad

**Interactividad global (`static/js/base.js`):**
- IIFE para evitar variables globales.
- `setSidebar(open, options)`: abre/cierra sidebar móvil, actualiza `body.sidebar-open`, `aria-expanded`, `aria-label`, backdrop y restaura foco.
- `closeUserMenu()`: cierra dropdown del usuario.
- `showSearchFeedback(message)`: existe pero no se invoca en el script actual; posible código preparado o muerto.
- Click en `.sidebar-toggle`: alterna sidebar.
- Click en `[data-sidebar-backdrop]`: cierra sidebar.
- Click en `.user-menu-trigger`: abre/cierra menú de usuario.
- Click en `.sidebar-link`: cierra sidebar en pantallas <=1024 px.
- Click en `[data-toggle-search-filters]`: colapsa filtros avanzados de búsqueda.
- Submit en `[data-global-search]`: evita búsqueda vacía y recorta espacios.
- Click en `[data-dismiss-message]`: elimina mensaje del DOM.
- Click fuera del menú: cierra menú de usuario.
- Escape: cierra sidebar y menú.

**Interactividad específica de módulo:**
- Búsqueda: colapso de filtros avanzados por atributos `data-toggle-search-filters` e id `advanced-search-filters`.
- No se encontró JS específico para previsualización de imágenes, llamadas fetch/AJAX, modales, ordenamiento de tablas, filtros dinámicos de select ni estados de carga.

## 12. Diseño responsivo

Confirmado en CSS:
- Breakpoints: `@media (min-width: 640px)`, `768px`, `900px`, `1024px`, `1180px` y `@media (max-width: 1024px)`, `767px`, `520px`.
- Sidebar móvil: en <=1024 px se comporta como drawer con backdrop y clase `sidebar-open`; en >=1024 px se muestra como columna fija de layout.
- Navbar: buscador global ocupa ancho completo en móvil y se reacomoda en escritorio.
- Grids: formularios y tarjetas pasan de una columna a dos o más columnas según breakpoint.
- Tablas: `.table-responsive` permite desplazamiento horizontal.
- Cards móviles: listados incluyen representación de cards además de tabla, lo que mejora lectura en pantallas estrechas.
- Ajustes móviles en botones/formularios: clases de acciones se apilan y usan ancho disponible.

Riesgos potenciales:
- Tablas grandes siguen dependiendo de scroll horizontal; puede ser incómodo en móviles.
- El archivo CSS único dificulta identificar qué pantallas tienen cobertura completa.
- No hay evidencia de pruebas reales en dispositivos.

## 13. Integración con Django Templates

- `{% extends "layout/base.html" %}`: usado por pantallas internas para heredar layout.
- `{% block title %}`, `{% block breadcrumbs %}`, `{% block page_title %}`, `{% block content %}`: bloques principales.
- `{% static %}`: carga CSS/JS.
- `{% url %}`: navegación nombrada en yonkes, inventario y otros templates; también hay href absolutos.
- `{% for %}`: listados, cards, campos de formularios y mensajes.
- `{% if %}`: estados vacíos, badges, permisos visibles, imágenes fallback y errores.
- Variables de contexto: `filters`, `yonkes`, `vehiculos`, `piezas`, `resultados`, `form`, `profile`, `metrics`, `messages`, `active_module`.
- Formularios de Django: templates de forms renderizan campos con `{{ field }}` y errores.
- GET/POST: filtros usan GET; formularios de alta/edición y login usan POST; formularios con archivos usan `multipart/form-data`.
- Imágenes: `{{ objeto.imagen_principal.url }}` y fallback al vehículo.
- Registros vacíos: `{% else %}<div class="empty-state">...`.

## 14. Navegación entre pantallas

```mermaid
flowchart TD
  Login[/login/] --> Dashboard[/]
  Registro[/register/] --> Dashboard
  Dashboard --> Yonkes[/yonkes/]
  Dashboard --> Vehiculos[/vehiculos/]
  Dashboard --> Piezas[/piezas/]
  Dashboard --> Busqueda[/busqueda/]
  Dashboard --> Catalogos[/catalogos/]
  Dashboard --> Usuarios[/usuarios/]
  BaseNavbar[Buscador global] --> Busqueda
  Yonkes --> NuevoYonke[/yonkes/nuevo/]
  Yonkes --> DetalleYonke[/yonkes/:id/]
  DetalleYonke --> EditarYonke[/yonkes/:id/editar/]
  Catalogos --> CatalogoLista[/catalogos/:tipo/]
  CatalogoLista --> CatalogoForm[/catalogos/:tipo/nuevo o editar/]
  Vehiculos --> NuevoVehiculo[/vehiculos/nuevo/]
  Vehiculos --> DetalleVehiculo[/vehiculos/:id/]
  DetalleVehiculo --> EditarVehiculo[/vehiculos/:id/editar/]
  DetalleVehiculo --> NuevaPiezaContextual[/piezas/nueva/?vehiculo=id]
  Piezas --> NuevaPieza[/piezas/nueva/]
  Piezas --> DetallePieza[/piezas/:id/]
  DetallePieza --> EditarPieza[/piezas/:id/editar/]
  Busqueda --> DetallePieza
  Importaciones[/importaciones/] --> NuevaImportacion[/importaciones/nueva/]
  Importaciones --> DetalleImportacion[/importaciones/:id/]
  Usuarios --> NuevoUsuario[/usuarios/nuevo/]
  Usuarios --> DetalleUsuario[/usuarios/:id/]
  DetalleUsuario --> EditarUsuario[/usuarios/:id/editar/]
  UserMenu[Menú usuario] --> Perfil[/perfil/]
  Perfil --> Config[/configuracion/]
  Auditoria[/auditoria/] --> DetalleAuditoria[/auditoria/:id/]
```

## 15. Figuras recomendadas

| Figura sugerida | Pantalla | Qué debe mostrarse | Procedimiento que respalda | Pie sugerido |
|---|---|---|---|---|
| Listado de yonkes | `/yonkes/` | Filtros, tabla/cards y botón nuevo | Implementación de directorio operativo | “Listado filtrable de yonkes con acciones de consulta y edición.” |
| Formulario de yonke | `/yonkes/nuevo/` | Secciones de captura | Construcción de formularios segmentados | “Formulario de registro de yonke organizado por información principal y contacto.” |
| Índice de catálogos | `/catalogos/` | Tarjetas de catálogos | Reutilización de navegación por módulo | “Pantalla de selección de catálogos base del inventario.” |
| Formulario de vehículo | `/vehiculos/nuevo/` | Campo imagen y datos técnicos | Alta de unidades con archivo | “Formulario de vehículo con carga de imagen principal.” |
| Detalle de vehículo | `/vehiculos/<id>/` | Hero, datos y piezas relacionadas | Integración vehículo-piezas | “Detalle de unidad con información técnica y accesos al inventario relacionado.” |
| Listado de piezas | `/piezas/` | Filtros de precio/estado, imágenes, tabla | Gestión central del inventario | “Listado de piezas con filtros múltiples y visualización responsiva.” |
| Detalle de pieza | `/piezas/<id>/` | Imagen, badges, precio/ubicación | Presentación de autoparte | “Detalle de pieza con compatibilidad y datos de inventario.” |
| Búsqueda avanzada | `/busqueda/` | Buscador principal y filtros avanzados | Consulta de inventario | “Pantalla de búsqueda avanzada de piezas.” |
| Resultados de búsqueda | `/busqueda/?pieza=...` | Cards de resultados | Flujo de consulta | “Resultados de piezas con acceso al detalle.” |
| Importación | `/importaciones/nueva/` | Selector y archivo | Carga de datos | “Formulario de importación de archivo Excel.” |
| Auditoría | `/auditoria/` | Filtros, timeline y tabla | Consulta administrativa | “Listado de eventos con filtros y doble visualización.” |
| Vista móvil | Cualquier listado | Drawer/sidebar y cards | Adaptación responsive | “Adaptación móvil con menú lateral desplegable y cards.” |

## 16. Tablas recomendadas

- **Tecnologías frontend utilizadas**: tecnología, función, archivo, evidencia. Propósito: justificar stack real.
- **Pantallas por módulo**: módulo, pantalla, URL, template, estado. Propósito: delimitar alcance.
- **Formularios del sistema**: formulario, campos, origen Django/manual, método, archivos. Propósito: documentar captura de datos.
- **Componentes reutilizables**: componente, archivo, variables, pantallas. Propósito: explicar reutilización.
- **Funciones JavaScript**: función/bloque, evento, selector, efecto. Propósito: describir interactividad.
- **Comparación responsive**: componente, móvil, tablet, escritorio, evidencia CSS. Propósito: documentar adaptabilidad.
- **Rutas de navegación**: origen, destino, acción, template. Propósito: explicar flujo entre pantallas.

## 17. Pruebas encontradas

Confirmado:
- Existen carpetas `apps/*/tests/`, pero no se encontraron pruebas frontend automatizadas de UI, snapshots, Selenium, Playwright, Cypress ni pruebas responsive.
- `apps/inventario/tests/test_role_permissions.py` prueba permisos de inventario, no desarrollo visual frontend.
- README declara “QA visual” y responsive, pero no incluye casos, evidencias, capturas ni comandos.

Pendiente recomendado:
- Pruebas manuales documentadas de login, navegación por sidebar, filtros GET, altas/ediciones, carga de imagen, importación Excel y empty states.
- Pruebas responsive en anchos declarados en README: 320, 375, 390, 414, 768, 1024 y 1440 px.
- Pruebas de accesibilidad básica: teclado, foco visible, contraste, labels, aria-expanded.
- Pruebas visuales de tablas grandes en móvil.

## 18. Problemas y mejoras

**Problemas comprobados:**
- `showSearchFeedback()` está definida en `base.js` pero no se invoca.
- No hay templates de confirmación para eliminación de catálogos; las rutas existen como acciones directas.
- No hay paginación visible en listados; puede afectar rendimiento/usabilidad con muchos registros.
- JavaScript específico de módulos no existe; por ejemplo, no hay actualización dinámica modelo/marca aunque el queryset del formulario depende de la marca enviada.
- `requirements.txt` parece guardado con caracteres nulos/encoding UTF-16, lo que puede dificultar herramientas estándar.
- README declara Bootstrap Icons, pero no se encontró carga real.

**Riesgos potenciales:**
- `base.css` monolítico dificulta mantenimiento y trazabilidad.
- Listados duplican cards y tablas en templates, aumentando costo de cambios.
- Accesibilidad parcial: hay labels y ARIA en layout, pero no se verificó contraste automático ni navegación completa.
- Cargas de imagen/archivo no tienen previsualización ni estado de carga.
- Tablas anchas pueden requerir scroll horizontal excesivo en teléfono.

**Mejoras recomendadas:**
- Dividir CSS por capas: variables/base, layout, componentes, módulos.
- Crear includes parciales para campos de formulario, empty states, tablas y acciones.
- Agregar paginación de listados.
- Añadir confirmación visual antes de eliminar catálogos.
- Agregar JS opcional para selects dependientes, previsualización de imágenes y estados de carga.
- Crear pruebas E2E mínimas con Playwright o Selenium.

## 19. Cronología técnica reconstruida

No se puede conocer el orden histórico real. Secuencia lógica recomendable para documentar:
1. Definir stack: Django Templates, CSS propio, JS vanilla y staticfiles.
2. Crear estructura `templates/`, `static/css`, `static/js` y configuración de recursos.
3. Diseñar variables CSS, paleta, tipografía, botones, cards, tablas y formularios.
4. Crear login y registro como pantallas independientes.
5. Crear `layout/base.html` con navbar, sidebar, breadcrumbs, mensajes y footer.
6. Implementar dashboard y accesos rápidos.
7. Implementar patrón de listado con filtros, cards, tabla responsive y empty states.
8. Desarrollar yonkes como módulo operativo base.
9. Desarrollar catálogos para alimentar selects.
10. Desarrollar vehículos con imagen y relación a yonkes/catálogos.
11. Desarrollar piezas con imagen, precios, cantidad y compatibilidad.
12. Implementar búsqueda avanzada y conexión desde navbar/dashboard.
13. Incorporar importaciones por archivo.
14. Incorporar usuarios, perfil y configuración.
15. Incorporar auditoría como consulta de eventos.
16. Ajustar responsive y accesibilidad básica.
17. Realizar pruebas manuales y documentar evidencias.

## 20. Archivos esenciales

| Ruta | Función | Módulo | Dependencias | Importancia | Apartado de memoria |
|---|---|---|---|---|---|
| `templates/layout/base.html` | Layout global | Todos | `base.css`, `base.js`, contexto permisos/mensajes | Base de reutilización | Plantilla base, navegación, componentes |
| `static/css/base.css` | Sistema visual | Todos | Variables CSS | Define identidad visual y responsive | CSS y diseño |
| `static/js/base.js` | Interactividad global | Todos internos | Selectores data/clases | Drawer, menú, búsqueda, mensajes | JavaScript |
| `config/settings.py` | Static/media/templates | Global | Django | Explica carga de recursos | Integración Django |
| `config/urls.py` | Inclusión de rutas HTML | Global | `html_urls.py` | Mapa de navegación | Navegación |
| `apps/*/html_urls.py` | URLs por módulo | Cada módulo | Vistas HTML | Inventario de pantallas | Pantallas/rutas |
| `apps/*/html_views.py` | Contexto de templates | Cada módulo | Modelos/forms | Datos que reciben pantallas | Integración visible |
| `apps/*/forms.py` | Formularios y clases CSS | CRUD | Django forms | Campos y estilos | Formularios |
| `templates/yonkes/*` | CRUD yonkes | Yonkes | Base/form | Primer módulo operativo | Yonkes |
| `templates/catalogos/*` | Catálogos genéricos | Catálogos | Forms dinámicos | Reutilización avanzada | Catálogos |
| `templates/vehiculos/*` | CRUD vehículos | Inventario | VehiculoForm | Carga imágenes | Vehículos |
| `templates/piezas/*` | CRUD piezas | Inventario | PiezaForm | Inventario central | Piezas |
| `templates/busqueda/piezas.html` | Búsqueda | Búsqueda | Filtros/resultados | Consulta principal | Búsqueda |
| `templates/importaciones/*` | Carga Excel | Importaciones | ImportacionExcelForm | Flujo de archivos | Importaciones |
| `templates/usuarios/*` | Gestión usuarios | Usuarios | Forms accounts | Gestión visible | Usuarios |
| `templates/auditoria/*` | Logs | Auditoría | Contexto logs | Consulta administrativa | Auditoría |
| `README.md` | Declaraciones de stack/alcance | Global | N/A | Contrastar código vs documentación | Introducción técnica |

## 21. Información faltante y preguntas al desarrollador

Preguntas concretas:
1. ¿Qué herramienta se usó para diseñar bocetos o mockups antes de implementar HTML/CSS?
2. ¿Cuál fue el orden histórico real de implementación de módulos?
3. ¿Qué navegadores se probaron manualmente y en qué versiones?
4. ¿Se probaron dispositivos físicos o solo emulación responsive?
5. ¿Qué capturas reales existen del QA visual mencionado en README?
6. ¿Qué criterios se usaron para elegir la paleta verde/teal?
7. ¿Por qué se documenta Bootstrap Icons si los íconos parecen SVG inline?
8. ¿Se descartó usar Bootstrap/Tailwind o nunca se contempló?
9. ¿Cuántos registros se esperaban por listado y por qué no se agregó paginación visible?
10. ¿Se planeó agregar confirmaciones de eliminación para catálogos?
11. ¿Se requiere previsualización de imágenes en vehículos, piezas y marcas?
12. ¿Qué validaciones manuales se realizaron en formularios de alta/edición?
13. ¿Qué problemas visuales se encontraron durante el desarrollo?
14. ¿Qué cambios solicitó el usuario final o asesor del proyecto?
15. ¿Qué funciones frontend quedaron pendientes o fuera del MVP?

# Evidencias rápidas para verificar

```bash
# Listar templates frontend
rg --files templates

# Ver carga global de CSS/JS
sed -n '1,220p' templates/layout/base.html

# Ver variables, breakpoints y componentes CSS
rg -n "^:root|@media|\.btn|\.card|\.table|\.sidebar|\.form-control|empty-state" static/css/base.css

# Ver interacciones JavaScript
sed -n '1,220p' static/js/base.js

# Ver rutas HTML por módulo
for f in apps/*/html_urls.py; do echo "--- $f"; sed -n '1,220p' "$f"; done

# Ver formularios que asignan clases CSS
rg -n "form-control|form-select|form-checkbox|form-textarea|class Meta|fields =" apps/*/forms.py

# Ver pantallas con herencia de la plantilla base
rg -n "extends \"layout/base.html\"" templates

# Ver listados con filtros, tablas y estados vacíos
rg -n "method=\"get\"|table-responsive|empty-state|list-card|for .* in" templates

# Ver uso de imágenes y archivos subidos
rg -n "multipart/form-data|imagen_principal|\.url|archivo" templates apps/*/forms.py config/settings.py

# Ver dependencias declaradas/documentación del frontend
sed -n '1,220p' README.md
cat requirements.txt
```
