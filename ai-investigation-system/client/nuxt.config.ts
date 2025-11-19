// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    '@vueuse/nuxt'
  ],

  app: {
    head: {
      title: 'AI Investigation System'
    }
  },

  devtools: {
    enabled: false
  },

  css: [
    '~/assets/css/main.css',
    "v-network-graph/lib/style.css"
  ],

  routeRules: {
    '/api/**': {
      cors: true
    }
  },

  compatibilityDate: '2024-07-11',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
