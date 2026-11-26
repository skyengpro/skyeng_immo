import { createRouter, createWebHistory } from 'vue-router'
import { session, loadSession, space, home } from './session'

const owner = { space: 'owner' }
const tenant = { space: 'tenant' }

const routes = [
  { path: '/connexion', name: 'login', component: () => import('./pages/Login.vue'), meta: { public: true } },
  { path: '/mot-de-passe-oublie', name: 'forgot', component: () => import('./pages/Forgot.vue'), meta: { public: true } },
  { path: '/', name: 'root', redirect: () => home() },

  { path: '/proprietaire', name: 'owner-home', component: () => import('./pages/owner/Home.vue'), meta: owner },
  { path: '/proprietaire/biens', name: 'properties', component: () => import('./pages/owner/Properties.vue'), meta: owner },
  { path: '/proprietaire/biens/:id', name: 'property', component: () => import('./pages/owner/Property.vue'), props: true, meta: owner },
  { path: '/proprietaire/locataires', name: 'tenants', component: () => import('./pages/owner/Tenants.vue'), meta: owner },
  { path: '/proprietaire/baux/:id', name: 'owner-lease', component: () => import('./pages/Lease.vue'), props: true, meta: owner },
  { path: '/proprietaire/factures/:id', name: 'owner-invoice', component: () => import('./pages/Invoice.vue'), props: true, meta: owner },
  { path: '/proprietaire/maintenance', name: 'owner-issues', component: () => import('./pages/Issues.vue'), meta: owner },
  { path: '/proprietaire/maintenance/:id', name: 'owner-issue', component: () => import('./pages/Issue.vue'), props: true, meta: owner },
  { path: '/proprietaire/compte', name: 'owner-account', component: () => import('./pages/Account.vue'), meta: owner },

  { path: '/locataire', name: 'tenant-home', component: () => import('./pages/tenant/Home.vue'), meta: tenant },
  { path: '/locataire/bail', name: 'my-lease', component: () => import('./pages/tenant/MyLease.vue'), meta: tenant },
  { path: '/locataire/bail/:id', name: 'tenant-lease', component: () => import('./pages/Lease.vue'), props: true, meta: tenant },
  { path: '/locataire/factures', name: 'invoices', component: () => import('./pages/tenant/Invoices.vue'), meta: tenant },
  { path: '/locataire/factures/:id', name: 'tenant-invoice', component: () => import('./pages/Invoice.vue'), props: true, meta: tenant },
  { path: '/locataire/maintenance', name: 'tenant-issues', component: () => import('./pages/Issues.vue'), meta: tenant },
  { path: '/locataire/maintenance/nouvelle', name: 'new-issue', component: () => import('./pages/tenant/NewIssue.vue'), meta: tenant },
  { path: '/locataire/maintenance/:id', name: 'tenant-issue', component: () => import('./pages/Issue.vue'), props: true, meta: tenant },
  { path: '/locataire/compte', name: 'tenant-account', component: () => import('./pages/Account.vue'), meta: tenant },

  { path: '/acces', name: 'no-access', component: () => import('./pages/NoAccess.vue'), meta: { public: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/sky-immo/'),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

router.beforeEach(async (to) => {
  if (!session.ready) await loadSession()
  if (session.noAccess && to.name !== 'no-access') return { name: 'no-access' }
  if (to.meta.public) return session.user && to.name === 'login' ? home() : true
  if (!session.user) return { name: 'login', query: to.fullPath !== '/' ? { next: to.fullPath } : {} }
  // a tenant on a landlord page (or the reverse) goes to their own home
  if (to.meta.space && to.meta.space !== space()) return home()
  return true
})

export default router
