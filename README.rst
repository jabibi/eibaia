ElosuE!
=======

Gestión del hogar: un pequeño ERP doméstico construido como monorepo con
`Nuxt 3 <https://nuxt.com/>`_ (frontend) y `FastAPI <https://fastapi.tiangolo.com/>`_
(backend), desplegado sobre Firebase (Hosting, Cloud Functions v2 en Python,
Firestore y Authentication).

Producción: https://elosue.web.app

Stack
-----

- **Frontend**: Nuxt 3 (modo SPA, ``ssr: false``), Pinia, Tailwind CSS,
  PrimeVue, ``@nuxtjs/i18n``.
- **Backend**: FastAPI sobre Cloud Functions v2 (Python), Firebase Admin SDK,
  Firestore en modo nativo.
- **Auth**: Firebase Authentication (Google) con roles vía *custom claims*.
- **Hosting**: Firebase Hosting sirviendo el build estático de Nuxt y
  redirigiendo ``/api/**`` a la función ``api``.

Roles y permisos
-----------------

Jerarquía acumulativa: ``admin`` ⊇ ``manager`` ⊇ ``user``. Un usuario recién
registrado no tiene rol asignado (acceso nulo) hasta que un administrador se
lo concede; el primer usuario que se registra en la aplicación se promueve
automáticamente a ``admin``.

Módulos
-------

- **Caja Fuerte**: resumen de saldo, listado paginado de movimientos
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
