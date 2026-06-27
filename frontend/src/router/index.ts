import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/error',
      name: 'error',
      component: () => import('@/views/ErrorView.vue'),
      meta: { public: true },
    },

    // ── HomeLayout：学生浏览中心 ─────────────────────────────────────────────
    {
      path: '/',
      component: () => import('@/layouts/HomeLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/home' },
        { path: 'home', name: 'home', component: () => import('@/views/home/HomeView.vue') },
      ],
    },

    // ── UserLayout：学生个人中心 ─────────────────────────────────────────────
    {
      path: '/user',
      component: () => import('@/layouts/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/user/profile' },
        { path: 'profile', name: 'user-profile', component: () => import('@/views/user/UserProfileView.vue') },
      ],
    },

    // ── AdminLayout：管理后台（仅 admin） ────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/home' },
        { path: 'home', name: 'admin-home', component: () => import('@/views/admin/AdminHomeView.vue') },
        { path: 'users', name: 'admin-users', component: () => import('@/views/admin/AdminUserControlView.vue') },
        { path: 'subjects', name: 'admin-subjects', component: () => import('@/views/admin/AdminSubjectControlView.vue') },
        {
          path: 'subjects/:subjectId/videos',
          name: 'admin-subject-videos',
          component: () => import('@/views/admin/AdminSubjectVideosView.vue'),
        },
      ],
    },

    { path: '/:pathMatch(.*)*', redirect: '/error' },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.public) return true

  if (!auth.isLoggedIn) return { name: 'login', query: { redirect: to.fullPath } }

  if (!auth.user) {
    try { await auth.fetchMe() }
    catch { return { name: 'login' } }
  }

  if (auth.isAdmin && (to.path.startsWith('/home') || to.path.startsWith('/user') || to.path.startsWith('/subjects'))) {
    return { name: 'admin-home' }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) return { name: 'error' }

  return true
})

export default router
