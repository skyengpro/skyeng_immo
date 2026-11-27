import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { registerServiceWorker } from './pwa'
import './install' // catches the browser's install offer, which can come before the first screen
import './theme'
import './style.css'

createApp(App).use(router).mount('#app')
registerServiceWorker()
