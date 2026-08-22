import tailwindcss from "@tailwindcss/vite";
import Aura from "@primeuix/themes/aura";

// `ssr: false` means only build-time config (this file) makes it into the
// static HTML that `nuxt generate` writes to disk — `useSeoMeta`/`useHead`
// called from Vue components (e.g. app.vue) only apply after client-side
// hydration, which non-JS crawlers (WhatsApp, Facebook, Twitter) never run.
// Open Graph tags MUST live here, not in a component, or link previews break.
const SITE_URL = "https://elosue.web.app";
const SITE_TITLE = "ElosuE! - Gestión del Hogar";
const SITE_DESCRIPTION = "Aplicación de gestión de caja, gastos y organización del hogar.";
const OG_IMAGE = `${SITE_URL}/images/og-share.jpg`;

export default defineNuxtConfig({
  compatibilityDate: "2026-08-21",
  telemetry: false,
  srcDir: "src/",
  devtools: { enabled: true },
  ssr: false,
  modules: ["@pinia/nuxt", "@primevue/nuxt-module", "@nuxtjs/i18n", "@nuxt/icon"],
  vite: {
    plugins: [tailwindcss()],
  },
  i18n: {
    locales: [{ code: "es", name: "Español", file: "es.json" }],
    defaultLocale: "es",
    strategy: "no_prefix",
  },
  css: ["~/assets/css/main.css"],
  primevue: {
    options: { ripple: true, theme: { preset: Aura } },
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
      htmlAttrs: { lang: "es" },
      title: "Gestión del hogar",
      titleTemplate: "%s · ElosuE!",
      link: [
        { rel: "icon", type: "image/svg+xml", href: "/img/favicon.svg" },
        { rel: "manifest", href: "/manifest.webmanifest" },
        { rel: "apple-touch-icon", href: "/icons/apple-touch-icon.png" },
        { rel: "canonical", href: SITE_URL },
      ],
      meta: [
        { name: "color-scheme", content: "light" },
        { name: "theme-color", content: "#15803d" },
        { name: "apple-mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "default" },
        { name: "apple-mobile-web-app-title", content: "ElosuE!" },
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
