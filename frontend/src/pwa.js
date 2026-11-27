// The service worker is served from /sky-immo/sw.js (see skyeng_immo/sky_immo/service_worker.py) so it
// controls every page under /sky-immo and keeps the app opening with no connection.
export function registerServiceWorker() {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return
  const register = () => navigator.serviceWorker.register('/sky-immo/sw.js', { scope: '/sky-immo/' }).catch(() => {})
  if (document.readyState === 'complete') register()
  else window.addEventListener('load', register)
}
