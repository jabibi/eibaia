ElosuE!
=======

Gestión del hogar: un pequeño ERP doméstico construido como monorepo con
`Nuxt 4 <https://nuxt.com/>`_ (frontend) y `FastAPI <https://fastapi.tiangolo.com/>`_
(backend), desplegado sobre Firebase (Hosting, Cloud Functions v2 en Python,
Firestore y Authentication).

Producción: https://elosue.web.app

Stack
-----

- **Frontend**: Nuxt 4 (modo SPA, ``ssr: false``), Pinia, Tailwind CSS v4,
  Nuxt Icon, ``@nuxtjs/i18n``, PWA instalable con actualización automática
  (``@vite-pwa/nuxt``).
- **Backend**: FastAPI sobre Cloud Functions v2 (Python), Firebase Admin SDK,
  Firestore en modo nativo.
- **Auth**: Firebase Authentication (Google) con RBAC vía *custom claims*
  (ver «Roles y permisos» más abajo).
- **Hosting**: Firebase Hosting sirviendo el build estático de Nuxt y
  redirigiendo ``/api/**`` a la función ``api``.

Librerías principales
----------------------

Frontend (``frontend/package.json``):

- **Nuxt** — framework de Vue 3; enrutado por ficheros, auto-imports,
  configuración de build (``nuxt.config.ts``). Corre en modo SPA puro
  (``ssr: false``), sin renderizado en servidor.
- **Pinia** (+ ``@pinia/nuxt``) — estado global reactivo: sesión de usuario
  (``core/stores/auth.ts``) y permisos (``core/stores/permissions.ts``).
- **Tailwind CSS** (v4, vía ``@tailwindcss/vite``) — utilidades CSS; toda la
  UI propia (``core/components/ui/``) se construye con clases de Tailwind
  sobre elementos nativos, sin librería de componentes visuales.
- **Nuxt Icon** (+ ``@iconify-json/lucide``, ``@iconify-json/logos``,
  ``@iconify-json/simple-icons``) — iconos vía el componente
  ``<Icon name="lucide:...">``; sustituyó a PrimeIcons. ``logos:`` solo se
  usa para el logo de Google en el login; ``simple-icons:`` para logos de
  marca monocromos que deben respetar ``currentColor`` (p. ej. GitHub).
- **@nuxtjs/i18n** — internacionalización; la interfaz vive en inglés a
  nivel de código, los textos visibles se sirven en español desde
  ``frontend/i18n/locales/es.json`` (ver sección i18n más abajo).
- **firebase** (SDK cliente) — autenticación con Google y obtención del ID
  token que se envía al backend en cada petición.
- **@vite-pwa/nuxt** — genera el manifest y un Service Worker (Workbox) con
  ``registerType: "autoUpdate"``: en cada deploy, cualquier pestaña abierta
  (o la PWA instalada) actualiza y recarga sola, sin quedarse atascada en
  una versión vieja cacheada.
- **exceljs** — genera el ``.xlsx`` con estilos de la exportación de
  Informes y Analítica, en el propio navegador (sin llamada al backend).

Backend (``functions/requirements.txt``):

- **FastAPI** — framework HTTP; expone los endpoints bajo ``/api`` que
  Firebase Hosting redirige a la Cloud Function.
- **pydantic** — esquemas/validación de los payloads de entrada y salida de
  cada endpoint.
- **firebase-admin** — Admin SDK: verifica los ID tokens de Firebase Auth,
  gestiona *custom claims* (rol del usuario) y lee/escribe en Firestore.
- **firebase-functions** + **asgiref** — envuelven la app de FastAPI (ASGI)
  para que se ejecute como Cloud Function v2 (``functions/main.py``).

Roles y permisos
-----------------

RBAC de dos niveles — **roles** y **grupos de permisos** —, ambos como colecciones de
Firestore (``functions/app/modules/roles/``):

- Un **grupo de permisos** (``permission_groups``) es la unidad atómica de autorización:
  un código (p. ej. ``CASHBOX_MANAGE``) con nombre y descripción legibles. Endpoints y
  páginas se protegen comprobando ese código directamente, no hay más granularidad por
  debajo — un grupo *es* un permiso.
- Un **rol** (``user_roles``) es solo un nombre más una lista de códigos de grupo que
  concede. Los tres roles ya sembrados (``roles/services.py``, vía
  ``functions/scripts/seed_rbac.py``):

  ============ ========================================== ==============================
  Rol          Grupos concedidos                           Alcance
  ============ ========================================== ==============================
  ``admin``    ``CASHBOX_BASIC`` + ``CASHBOX_MANAGE`` +     Acceso total a la aplicación.
               ``SYSTEM_ADMIN``
  ``manager``  ``CASHBOX_BASIC`` + ``CASHBOX_MANAGE``       Gestiona la caja: revisa,
                                                             confirma y elimina cualquier
                                                             movimiento; ve Informes.
  ``employee`` ``CASHBOX_BASIC``                            Operación básica: crear
                                                             gastos/ingresos, editar o
                                                             eliminar solo sus borradores.
  ============ ========================================== ==============================

El sistema no está cerrado a esos tres: ``POST /roles`` (protegido con ``SYSTEM_ADMIN``)
crea roles nuevos combinando libremente los grupos existentes — hoy no hay pantalla en el
frontend para ello, solo API.

**Cómo viaja el permiso de una petición a otra:** al asignar un rol a un usuario
(``PATCH /users/{uid}/role``, desde Configuración → Usuarios) el backend fija un *custom
claim* ``role_id`` en su token de Firebase Auth. En cada petición, ``get_current_user``
(``functions/app/core/security.py``) decodifica ese ``role_id`` del token, y
``require_permission("CODE")``/``check_permission(user, "CODE")`` lo resuelven contra
``user_roles/{role_id}.group_ids`` para decidir si el código pedido está concedido. El
frontend replica esta misma comprobación del lado del cliente contra
``GET /users/me/permissions`` (``core/stores/permissions.ts``): guarda la lista de códigos
del usuario y decide qué mostrar/ocultar con ``permissionsStore.has("CODE")`` — es solo para
UX (ocultar botones sin permiso), la autorización real siempre la impone el backend.

Un usuario recién registrado no tiene rol asignado (``role_id: null``, acceso nulo) hasta que
un admin se lo concede — **excepto el primer usuario que se registra en toda la aplicación,
que se promueve automáticamente a** ``admin`` (``ensure_first_admin``, en
``functions/app/modules/users/services.py``).

Módulos
-------

- **Caja**: resumen de saldo, listado paginado de movimientos (gasto/ingreso,
  efectivo/tarjeta) con flujo borrador → confirmado, pantalla de revisión
  para que un manager consolide los movimientos, etiquetas para
  categorizarlos, e Informes y Analítica (filtros por fecha/tipo/etiqueta,
  totales y exportación a Excel/PDF sobre los movimientos ya confirmados).
- **Calendario / Horarios**: próximamente.
- **Configuración**: gestión de usuarios (activar/desactivar, asignar rol) y
  restablecimiento de fábrica de la aplicación.

i18n
----

Toda la interfaz vive en inglés a nivel de código (rutas, componentes,
identificadores); los textos visibles se sirven en español desde
``frontend/i18n/locales/es.json`` a través de ``@nuxtjs/i18n``. El backend no
necesita traducción: sus errores no se muestran directamente al usuario.

Estructura del repositorio
---------------------------

.. code-block:: text

    .
    ├── firebase.json           # Hosting, Functions, Firestore
    ├── firestore.rules         # Acceso denegado por defecto (solo Admin SDK)
    ├── firestore.indexes.json
    ├── run_dev.sh              # Arranca backend + frontend en local en un comando
    ├── frontend/               # Nuxt 4 (srcDir: src/)
    │   ├── i18n/locales/es.json
    │   ├── public/             # Assets estáticos (favicon, iconos...) — fuera de
    │   │                       # src/ desde Nuxt 4, ver CLAUDE.md
    │   └── src/
    │       ├── layouts/        # Layout por defecto (sidebar + contenido)
    │       ├── middleware/     # Guard de autenticación global de rutas
    │       ├── core/           # componentes/stores/composables compartidos
    │       ├── modules/        # módulos de dominio (finance, users, roles)
    │       └── pages/          # rutas
    └── functions/              # FastAPI sobre Cloud Functions v2
        ├── main.py             # entrypoint, puente ASGI manual
        ├── scripts/            # scripts puntuales (seed_rbac.py, seed_cashbox.py)
        └── app/
            ├── core/           # firebase, seguridad/RBAC
            └── modules/        # users, roles, finance, system

Desarrollo local
-----------------

Frontend:

.. code-block:: bash

    cd frontend
    cp .env.example .env   # rellenar credenciales de Firebase
    npm install
    npm run dev

Backend (Cloud Functions emulado o directamente con ``uvicorn`` sobre
``app.main:app``, usando ``functions/serviceAccountKey.json`` para
credenciales locales):

.. code-block:: bash

    cd functions
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Con ambos entornos ya preparados (``node_modules`` y ``functions/venv``), ``./run_dev.sh``
desde la raíz arranca backend y frontend juntos en un solo comando (frontend apuntando al
backend local, sin tocar ``frontend/.env`` — ver el footgun documentado en ``CLAUDE.md``).

Despliegue
----------

.. code-block:: bash

    # Frontend
    cd frontend && npm run generate

    # Todo (hosting + functions)
    firebase deploy --project elosue

    # Solo hosting
    firebase deploy --only hosting --project elosue
