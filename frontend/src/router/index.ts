import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const BRAND = '韩途'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: '' },
    },
    // ── user login ─────────────────────────────────
    {
      path: '/login',
      name: 'user-login',
      component: () => import('@/views/user/UserLoginView.vue'),
      meta: { title: '登录' },
    },
    // ── admin ──────────────────────────────────────
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
      meta: { title: '管理员登录' },
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: { name: 'admin-dashboard' } },
        { path: 'dashboard',   name: 'admin-dashboard',   component: () => import('@/views/admin/DashboardView.vue'),   meta: { title: '控制台' } },
        { path: 'video',       name: 'admin-video',       component: () => import('@/views/admin/VideoView.vue'),       meta: { title: '视频管理' } },
        { path: 'audio',       name: 'admin-audio',       component: () => import('@/views/admin/AudioView.vue'),       meta: { title: '音频管理' } },
        { path: 'pdf',         name: 'admin-pdf',         component: () => import('@/views/admin/PdfView.vue'),         meta: { title: 'PDF 管理' } },
        { path: 'users',       name: 'admin-users',       component: () => import('@/views/admin/UsersView.vue'),       meta: { title: '用户管理' } },
        { path: 'permissions', name: 'admin-permissions', component: () => import('@/views/admin/PermissionsView.vue'), meta: { title: '权限管理' } },
      ],
    },
    // ── user ───────────────────────────────────────
    {
      path: '/user',
      component: () => import('@/views/user/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'user-dashboard' } },
        { path: 'dashboard', name: 'user-dashboard', component: () => import('@/views/user/DashboardView.vue'),   meta: { title: '主页' } },
        { path: 'video',     name: 'user-video',     component: () => import('@/views/user/UserVideoView.vue'),   meta: { title: '视频' } },
        { path: 'audio',     name: 'user-audio',     component: () => import('@/views/user/UserAudioView.vue'),   meta: { title: '音频' } },
        { path: 'file',      name: 'user-file',      component: () => import('@/views/user/FileDownloadView.vue'), meta: { title: '文件' } },
        { path: 'account',   name: 'user-account',   component: () => import('@/views/user/UserAccountView.vue'),  meta: { title: '我的账户' } },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // set document title
  const pageTitle = to.meta.title as string | undefined
  document.title = pageTitle ? `${BRAND} · ${pageTitle}` : BRAND

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
