import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      children: [

      ]
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'admin-dashboard' } },
        { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'video', name: 'admin-video', component: () => import('@/views/admin/VideoView.vue') },
        { path: 'audio', name: 'admin-audio', component: () => import('@/views/admin/AudioView.vue') },
      ],
    },
    {
      path: '/user',
      component: () => import('@/views/user/UserLayout.vue'),
      children: [
        {
          path: '',
          redirect: { name: 'user-dashboard'}
        },
        {
          path: 'dashboard',
          name: 'user-dashboard',
          component: () => import('@/views/user/DashboardView.vue'),
        },
        {
          path: 'video',
          name: 'user-video',
          component: () => import('@/views/user/UserVideoView.vue')
        },
        {
          path: 'audio',
          name: 'user-audio',
          component: () => import('@/views/user/UserAudioView.vue')
        }
      ]
    }
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/admin/login' }
  }
  if (to.path === '/admin/login' && auth.isLoggedIn) {
    return { path: '/admin/dashboard' }
  }
})

export default router
