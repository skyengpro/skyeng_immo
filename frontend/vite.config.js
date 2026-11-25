import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import { VitePWA } from 'vite-plugin-pwa'

const BASE = '/assets/skyeng_immo/frontend/'
// the running site; `npm run dev` proxies API calls to it
const SITE = process.env.SITE_URL || 'http://localhost:8080'

export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/sky-immo',
      frappeProxy: false,
      jinjaBootData: false,
      buildConfig: {
        outDir: '../skyeng_immo/public/frontend',
        indexHtmlPath: '../skyeng_immo/www/sky-immo.html',
        baseUrl: BASE,
      },
    }),
    vue(),
    VitePWA({
      // registered by hand from /sky-immo/sw.js, see src/pwa.js and skyeng_immo/sky_immo/service_worker.py
      injectRegister: null,
      registerType: 'autoUpdate',
      filename: 'sw.js',
      includeAssets: ['favicon.png', 'apple-touch-icon.png', 'logo-mark.svg'],
      manifest: {
        id: '/sky-immo/',
        name: 'Sky-immo',
        short_name: 'Sky-immo',
        description: 'Properties, leases, rent and repairs for landlords and tenants',
        start_url: '/sky-immo/',
        scope: '/sky-immo/',
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#f5f4ef',
        theme_color: '#123b63',
        icons: [
          { src: `${BASE}icon-192.png`, sizes: '192x192', type: 'image/png' },
          { src: `${BASE}icon-512.png`, sizes: '512x512', type: 'image/png' },
          { src: `${BASE}icon-maskable-512.png`, sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,svg,png,woff2,html}'],
        // precache entries are relative; make them absolute so they resolve from /sky-immo/sw.js
        modifyURLPrefix: { '': BASE },
        navigateFallback: `${BASE}index.html`,
        navigateFallbackAllowlist: [/^\/sky-immo(\/|$)/],
        cleanupOutdatedCaches: true,
        inlineWorkboxRuntime: true,
        maximumFileSizeToCacheInBytes: 4 * 1024 * 1024,
      },
    }),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: {
    port: 8090,
    proxy: { '^/(api|assets|files|private|login)': { target: SITE, changeOrigin: false } },
  },
})
