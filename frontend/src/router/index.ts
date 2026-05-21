import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    // ── user login ─────────────────────────────────
    {
      path: '/login',
      name: 'user-login',
      component: () => import('@/views/user/UserLoginView.vue'),
    },
    // ── admin ──────────────────────────────────────
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: { name: 'admin-dashboard' } },
        { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'video',     name: 'admin-video',     component: () => import('@/views/admin/VideoView.vue') },
        { path: 'audio',     name: 'admin-audio',     component: () => import('@/views/admin/AudioView.vue') },
        { path: 'pdf',       name: 'admin-pdf',       component: () => import('@/views/admin/PdfView.vue') },
        { path: 'users',     name: 'admin-users',     component: () => import('@/views/admin/UsersView.vue') },
      ],
    },
    // ── user ───────────────────────────────────────
    {
      path: '/user',
      component: () => import('@/views/user/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'user-dashboard' } },
        { path: 'dashboard', name: 'user-dashboard', component: () => import('@/views/user/DashboardView.vue') },
        { path: 'video',     name: 'user-video',     component: () => import('@/views/user/UserVideoView.vue') },
        { path: 'audio',     name: 'user-audio',     component: () => import('@/views/user/UserAudioView.vue') },
        { path: 'file',      name: 'user-file',      component: () => import('@/views/user/FileDownloadView.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAdmin) {
    if (!auth.isLoggedIn) return { name: 'admin-login' }
    if (!auth.isAdmin)    return { name: 'home' }
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'user-login' }
  }

  if (to.name === 'admin-login' && auth.isLoggedIn && auth.isAdmin) {
    return { name: 'admin-dashboard' }
  }
  if (to.name === 'user-login' && auth.isLoggedIn) {
    return { name: 'user-dashboard' }
  }
})

export default router
