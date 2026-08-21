export default defineNuxtConfig({
  compatibilityDate: "2026-08-21",
  telemetry: false,
  srcDir: "src/",
  devtools: { enabled: true },
  ssr: false,
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt", "nuxt-primevue", "@nuxtjs/i18n"],
  i18n: {
    locales: [{ code: "es", name: "Español", file: "es.json" }],
    defaultLocale: "es",
    strategy: "no_prefix",
  },
  css: [
    "primevue/resources/themes/lara-light-indigo/theme.css",
    "primevue/resources/primevue.min.css",
    "primeicons/primeicons.css",
    "~/assets/css/main.css",
  ],
  primevue: {
    options: { ripple: true },
  },
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
      title: "ElosuE! - Gestión del hogar",
      link: [{ rel: "icon", type: "image/svg+xml", href: "/img/favicon.svg" }],
    },
  },
});
