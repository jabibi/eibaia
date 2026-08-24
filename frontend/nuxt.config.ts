import tailwindcss from "@tailwindcss/vite";

// `ssr: false` means only build-time config (this file) makes it into the
// static HTML that `nuxt generate` writes to disk — `useSeoMeta`/`useHead`
// called from Vue components (e.g. app.vue) only apply after client-side
// hydration, which non-JS crawlers (WhatsApp, Facebook, Twitter) never run.
// Open Graph tags MUST live here, not in a component, or link previews break.
const SITE_URL = "https://eibaia.web.app";
const SITE_TITLE = "E!Ibaia - Gestión del Hogar";
const SITE_DESCRIPTION = "Aplicación de gestión de caja, gastos y organización del hogar.";
const OG_IMAGE = `${SITE_URL}/images/og-share.jpg`;

export default defineNuxtConfig({
  compatibilityDate: "2026-08-21",
  telemetry: false,
  srcDir: "src/",
  devtools: { enabled: true },
  ssr: false,
  modules: ["@pinia/nuxt", "@nuxtjs/i18n", "@nuxt/icon", "@vite-pwa/nuxt"],
  // Con ssr:false + hosting estático no hay servidor en producción que sirva el bundle
  // local de iconos de @nuxt/icon — sin esto, cada carga de página pedía los SVG en vivo a
  // api.iconify.design (confirmado viendo las peticiones de red en eibaia.web.app), un CDN de
  // terceros del que la app quedaba dependiendo en runtime. Listar aquí los iconos usados los
  // incrusta en el bundle en build time — cero peticiones externas. Si se añade un icono
  // nuevo en el código y no aparece aquí, seguirá funcionando (cae de vuelta al CDN), pero
  // hay que añadirlo a esta lista para que también quede embebido.
  icon: {
    clientBundle: {
      icons: [
        "logos:google-icon",
        "lucide:arrow-left",
        "lucide:arrow-right",
        "lucide:check",
        "lucide:chevron-left",
        "lucide:circle-check-big",
        "lucide:file-spreadsheet",
        "lucide:file-text",
        "lucide:house",
        "lucide:loader-circle",
        "lucide:log-out",
        "lucide:menu",
        "lucide:panel-left-close",
        "lucide:pencil",
        "lucide:plus",
        "lucide:settings",
        "lucide:star",
        "lucide:trash-2",
        "lucide:undo-2",
        "lucide:user",
        "lucide:wallet",
        "lucide:x",
        "simple-icons:github",
      ],
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  i18n: {
    locales: [{ code: "es", name: "Español", file: "es.json" }],
    defaultLocale: "es",
    strategy: "no_prefix",
  },
  // registerType "autoUpdate" + skipWaiting/clientsClaim: en cuanto hay un
  // deploy nuevo, el Service Worker lo activa de inmediato en cualquier
  // pestaña abierta en vez de esperar a que el usuario las cierre todas —
  // sin esto, un usuario con la PWA ya instalada podría quedarse atascado
  // en una versión vieja indefinidamente. cleanupOutdatedCaches borra el
  // caché de la versión anterior una vez el nuevo SW toma el control.
  pwa: {
    registerType: "autoUpdate",
    manifest: {
      name: "E!Ibaia",
      short_name: "E!Ibaia",
      description: SITE_DESCRIPTION,
      start_url: "/",
      scope: "/",
      display: "standalone",
      orientation: "portrait",
      background_color: "#ffffff",
      theme_color: "#0284c7",
      lang: "es",
      icons: [
        { src: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" },
        { src: "/icons/icon-512x512.png", sizes: "512x512", type: "image/png" },
        { src: "/icons/icon-512x512-maskable.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
      ],
    },
    workbox: {
      navigateFallback: "/",
      // Firebase Hosting reserva /__/** para sus propias páginas especiales (p. ej.
      // /__/auth/handler, que el popup de signInWithPopup carga en nuestro propio
      // dominio — authDomain es eibaia.web.app — para completar el login con Google).
      // Sin excluirlo, la NavigationRoute del Service Worker se lo roba y le sirve el
      // SPA en su lugar: el popup de login "solo vuelve a abrir la web" y el login
      // nunca se completa. Reproducido y confirmado en Android tras añadir la PWA.
      navigateFallbackDenylist: [/^\/__\//],
      globPatterns: ["**/*.{js,css,html,png,svg,ico}"],
      cleanupOutdatedCaches: true,
      skipWaiting: true,
      clientsClaim: true,
    },
    client: {
      // false: no hay ningún botón "Instalar app" propio que consuma el evento
      // capturado (@vite-pwa/nuxt expondría $pwa.install() para eso) — con
      // true, intercepta beforeinstallprompt vía preventDefault() y nunca
      // vuelve a llamar a prompt(), así que el navegador solo avisa por
      // consola ("Banner not shown") sin mostrar nunca su banner nativo.
      // Dejarlo en false deja que Chrome/Android muestren su propio banner.
      installPrompt: false,
      periodicSyncForUpdates: 3600,
    },
  },
  css: ["~/assets/css/main.css"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "/api",
      firebase: {
        apiKey: process.env.NUXT_PUBLIC_FIREBASE_API_KEY,
        authDomain: process.env.NUXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
        projectId: process.env.NUXT_PUBLIC_FIREBASE_PROJECT_ID,
        storageBucket: process.env.NUXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
        messagingSenderId: process.env.NUXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
        appId: process.env.NUXT_PUBLIC_FIREBASE_APP_ID,
      },
    },
  },
  app: {
    head: {
      htmlAttrs: { lang: "es" },
      title: "Gestión del hogar",
      titleTemplate: "%s · E!Ibaia",
      link: [
        { rel: "icon", type: "image/svg+xml", href: "/img/favicon.svg" },
        // @vite-pwa/nuxt inyecta este link en tiempo de ejecución (vía JS), pero con
        // ssr:false ese HTML estático que escribe `nuxt generate` no lleva nada
        // inyectado dinámicamente (mismo motivo que las etiquetas OG de más abajo) —
        // se deja explícito aquí para que quede horneado en el build.
        { rel: "manifest", href: "/manifest.webmanifest" },
        { rel: "apple-touch-icon", href: "/icons/apple-touch-icon.png" },
        { rel: "canonical", href: SITE_URL },
      ],
      meta: [
        { name: "color-scheme", content: "light" },
        { name: "theme-color", content: "#0284c7" },
        { name: "mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "default" },
        { name: "apple-mobile-web-app-title", content: "E!Ibaia" },
        { name: "description", content: SITE_DESCRIPTION },

        { property: "og:title", content: SITE_TITLE },
        { property: "og:description", content: SITE_DESCRIPTION },
        { property: "og:image", content: OG_IMAGE },
        { property: "og:image:secure_url", content: OG_IMAGE },
        { property: "og:image:type", content: "image/jpeg" },
        { property: "og:image:width", content: "1200" },
        { property: "og:image:height", content: "630" },
        { property: "og:url", content: SITE_URL },
        { property: "og:type", content: "website" },
        { property: "og:locale", content: "es_ES" },

        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:title", content: SITE_TITLE },
        { name: "twitter:description", content: SITE_DESCRIPTION },
        { name: "twitter:image", content: OG_IMAGE },
      ],
    },
  },
});
