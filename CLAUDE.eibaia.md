# eibaia — notas específicas de este fork

Este fichero es propio de `eibaia` y no existe en `elosue` — así que nunca puede entrar
en conflicto con un futuro `git pull upstream main`. Todo lo que sea código/funcionalidad
compartida con elosue se documenta en `CLAUDE.md` (heredado); todo lo que sea específico
de esta marca (branding, credenciales locales, decisiones de identidad visual) va aquí.

## Relación con elosue

- `origin` → `github.com/jabibi/eibaia` (este repo). `upstream` → `github.com/jabibi/elosue`.
- Los cambios de funcionalidad/lógica de la app se hacen en elosue y se traen aquí con
  `git pull upstream main`. Este repo solo debe divergir en estética: logos, colores,
  textos de marca. Si vas a tocar algo que no sea puramente visual, plantéate si debería
  ir a elosue en su lugar — evita que ese fichero se convierta en un conflicto permanente.
- Ficheros que ya son y seguirán siendo divergencia intencional (no intentar "resincronizar"
  con elosue): `.firebaserc` (apunta a `eibaia`), `frontend/.env` (credenciales propias),
  y todo lo listado en la sección de branding más abajo.

## Firebase

- Proyecto real propio: `eibaia` (no comparte backend/Firestore con `elosue`). Firestore y
  Google Sign-In ya habilitados.
- `authDomain` en `frontend/.env` es **`eibaia.web.app`** (no el `.firebaseapp.com` por
  defecto) — mismo criterio que elosue, para que el popup de login no muestre un dominio
  distinto al de la app.
- El cliente OAuth (Google Cloud Console → APIs & Services → Credentials → "Web client
  (auto created by Google Service)", proyecto `eibaia`) tiene añadidos manualmente
  `https://eibaia.web.app` como origen autorizado y `https://eibaia.web.app/__/auth/handler`
  como URI de redirección — el alta automática de Firebase solo cubre `.firebaseapp.com`.
- `functions/serviceAccountKey.json` (gitignored) ya existe para desarrollo local — se generó
  desde Firebase Console → Configuración del proyecto → Cuentas de servicio → "Generar nueva
  clave privada". Si se pierde/rota, hay que regenerarlo ahí (no reutilizar el de elosue, es
  por proyecto).
- Firestore ya seedeado una vez (`cd functions && venv/bin/python scripts/seed_rbac.py` y
  `scripts/seed_cashbox.py`): roles (`admin`/`manager`/`employee`/`user`), permission groups
  (`CASHBOX_BASIC`/`CASHBOX_MANAGE`/`SYSTEM_ADMIN`) y la caja única ("La caja"). El primer
  login se auto-promociona a `admin` vía `ensure_first_admin` (ver `app/modules/users/router.py`)
  ahora que el rol `admin` ya existe en `user_roles`.

## Identidad de marca

- Paleta: `indigo` (color primario de elosue) sustituido por **`sky`** en toda la UI
  (botones, focus rings, tab activa, toggle). `emerald` (éxito), `amber` (aviso) y `slate`
  (neutro) se mantienen igual que en elosue — coinciden con la paleta pedida para eibaia.
  `indigo` sigue existiendo tal cual en `core/ui/categoryColors.ts` porque ahí es una opción
  de color de categoría seleccionable por el usuario, no branding — no tocar.
- Nombre de marca: **"E!Ibaia"** (con esa capitalización y el `!` a mitad) en todo texto/
  metadato: PWA manifest, `<title>`, meta tags, `es.json` (`app.name`/`app.title`), título de
  FastAPI, wordmark del panel lateral (`Sidebar.vue`, en dos tonos: "E!" en `#0284c7` /
  "Ibaia" en `#1e293b`) y el wordmark dentro de los SVG (`Logo.vue`, `logo-home(-full).svg`,
  `og-share.jpg`: `<tspan>E!</tspan>Ibaia`).
  - Excepción deliberada: nombres de fichero/`docTitle` de informes exportados usan
    **"EIbaia"** (sin `!`, más seguro para nombres de fichero) — `reports.vue` y
    `finance.reports.export.docTitle` en `es.json`.
- Logo/ilustración — **dos composiciones de edificio distintas, no mezclar**:
  - "Portada" (`Logo.vue`, usado en `pages/index.vue` y `pages/pending.vue`, más
    `logo-home.svg`/`logo-home-full.svg` como copias estáticas sin uso en código): edificio
    con cornisa plana (`rect` `-27,-45,54x4`) y 2 ventanas grises de planta superior
    (`fill="#94a3b8"` en `y="-35"`). Sol en `translate(0, -70)` — ojo, si se mueve el sol o
    el grupo del edificio (`translate(0, 8)`), comprobar que no se solapan (ya pasó una vez:
    el tejado pintaba encima del sol).
  - "Icono de app" (`favicon.svg`, `logo-mark.svg`, usado en PWA/favicon/panel lateral):
    edificio más simple, tejado triangular (`path` a `-60`/`-52`), sin ventanas de planta
    superior, dentro de una máscara squircle (`favicon.svg`) o recortado sin máscara
    (`logo-mark.svg`).
  - `og-share.jpg` es un JPG generado a mano (no hay build step automático) desde un SVG en
    scratchpad usando la composición de "portada" + texto aparte a la derecha, rasterizado
    con `rsvg-convert` + `convert -background white -flatten`. Si vuelve a cambiar el logo o
    el texto de marca, hay que regenerarlo manualmente igual — no se actualiza solo.
- Dominio de la app en metadatos (`SITE_URL`, OG tags, `authDomain`, comentarios): siempre
  `eibaia.web.app`, nunca `elosue.web.app` ni `eibaia.firebaseapp.com`.

## Desarrollo local

- `functions/venv` ya creado con el runtime compartido de `/opt/firebase/.python-runtime`
  (mismo criterio que elosue, ver `CLAUDE.md`) + `pip install -r requirements.txt`.
- `./run_dev.sh` desde la raíz arranca backend (`:8000`) y frontend (`:3000` — el puerto por
  defecto de `nuxt dev`, sin `--port` explícito) juntos. Si un `nuxt dev` anterior queda vivo
  en otro puerto, `run_dev.sh` falla con "Another Nuxt dev is already running" — matar ese
  proceso (por PID, no solo `pkill -f "nuxt dev"`, que a veces no matcha) antes de reintentar.
