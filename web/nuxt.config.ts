export default defineNuxtConfig({
  compatibilityDate: '2026-09-30',
  modules: ['@nuxt/eslint'],
  css: ['maplibre-gl/dist/maplibre-gl.css', '~/assets/css/fonts.css', '~/assets/css/base.css', '~/assets/css/brand.css', '~/assets/css/layout.css', '~/assets/css/map.css', '~/assets/css/admin.css', '~/assets/css/context.css', '~/assets/css/gallery.css'],
  app: {
    head: {
      title: 'Le Clos du Verger | Démonstration lotimap',
      htmlAttrs: { lang: 'fr' },
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preload', as: 'font', type: 'font/woff2', href: '/fonts/ibm-plex-sans-latin.woff2', crossorigin: '' },
        { rel: 'preload', as: 'font', type: 'font/woff2', href: '/fonts/space-grotesk-latin.woff2', crossorigin: '' },
      ],
      meta: [
        { name: 'robots', content: 'noindex,nofollow,noarchive' },
        { name: 'description', content: 'Plan de lotissement fictif pour une démonstration géomatique.' },
      ],
    },
  },
  routeRules: {
    '/**': { headers: { 'X-Robots-Tag': 'noindex, nofollow, noarchive' } },
  },
  typescript: { strict: true },
})
