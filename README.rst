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
  PrimeVue (solo directivas), Nuxt Icon, ``@nuxtjs/i18n``.
- **Backend**: FastAPI sobre Cloud Functions v2 (Python), Firebase Admin SDK,
  Firestore en modo nativo.
- **Auth**: Firebase Authentication (Google) con roles vía *custom claims*.
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
- **PrimeVue** (``@primevue/nuxt-module``, fijado a v4.x) — ya no se usa
  ningún componente suyo; se mantiene solo por la directiva ``v-tooltip``
  (tooltips del sidebar) y ``v-ripple``. Fijado a v4 a propósito: la v5
  introduce un gate de licencia comercial (ver ``CLAUDE.md``).
- **Nuxt Icon** (+ ``@iconify-json/lucide``, ``@iconify-json/logos``) —
  iconos vía el componente ``<Icon name="lucide:...">``; sustituyó a
  PrimeIcons. ``logos:`` solo se usa para el logo de Google en el login.
- **@nuxtjs/i18n** — internacionalización; la interfaz vive en inglés a
  nivel de código, los textos visibles se sirven en español desde
  ``frontend/i18n/locales/es.json`` (ver sección i18n más abajo).
- **firebase** (SDK cliente) — autenticación con Google y obtención del ID
  token que se envía al backend en cada petición.

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

Jerarquía acumulativa: ``admin`` ⊇ ``manager`` ⊇ ``user``. Un usuario recién
registrado no tiene rol asignado (acceso nulo) hasta que un administrador se
lo concede; el primer usuario que se registra en la aplicación se promueve
automáticamente a ``admin``.

Módulos
-------

- **Caja**: resumen de saldo, listado paginado de movimientos
  (gasto/ingreso/ajuste, efectivo/tarjeta) con flujo borrador → confirmado, y
  pantalla de revisión para que un manager consolide los movimientos.
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
    ├── frontend/               # Nuxt 3 (srcDir: src/)
    │   ├── i18n/locales/es.json
    │   └── src/
    │       ├── core/           # componentes/stores/composables compartidos
    │       ├── modules/        # módulos de dominio (finance, users, ...)
    │       └── pages/          # rutas
    └── functions/              # FastAPI sobre Cloud Functions v2
        ├── main.py             # entrypoint, puente ASGI manual
        └── app/
            ├── core/           # firebase, seguridad/RBAC
            └── modules/        # users, finance, system

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

Despliegue
----------

.. code-block:: bash

    # Frontend
    cd frontend && npm run generate

    # Todo (hosting + functions)
    firebase deploy --project elosue

    # Solo hosting
    firebase deploy --only hosting --project elosue
