import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { BRAND } from '@/core/brand'

const AppShell = () => import('@/core/layouts/AppShell.vue')
const CourseScope = () => import('@/core/layouts/CourseScope.vue')

// 旧网址（原 topik 站 /user/*、原 course 站 /home 等）→ 新网址，书签与分享链接继续有效
const legacy: RouteRecordRaw[] = [
  { path: '/user', redirect: '/topik' },
  { path: '/user/dashboard', redirect: '/topik' },
  { path: '/user/video', redirect: '/topik/video' },
  { path: '/user/audio', redirect: '/topik/audio' },
  { path: '/user/file', redirect: '/topik/file' },
  { path: '/user/account', redirect: '/me' },
  { path: '/user/profile', redirect: '/me' },
  { path: '/home', redirect: '/course' },
  { path: '/roadmap', redirect: '/course/roadmap' },
  { path: '/mindmap', redirect: '/course/mindmap' },
  { path: '/admin/login', redirect: (to) => ({ path: '/login', query: { redirect: '/admin', ...to.query } }) },
  { path: '/admin/home', redirect: '/admin' },
  { path: '/admin/video', redirect: '/admin/topik/video' },
  { path: '/admin/audio', redirect: '/admin/topik/audio' },
  { path: '/admin/pdf', redirect: '/admin/topik/pdf' },
  { path: '/admin/subjects', redirect: '/admin/course/subjects' },
  { path: '/admin/roadmap', redirect: '/admin/course/roadmap' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: (to, _from, saved) => saved ?? (to.hash ? { el: to.hash, top: 72 } : { top: 0 }),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/core/views/LoginView.vue'),
      meta: { title: '登录' },
    },
    {
      path: '/',
      component: AppShell,
      children: [
        { path: '', name: 'home', component: () => import('@/core/views/HomeView.vue') },

        // ── 韩语 TOPIK ──────────────────────────────────────────
        { path: 'topik',       name: 'topik',       component: () => import('@/topik/views/DashboardView.vue'),    meta: { title: '韩语', section: 'topik', requiresAuth: true } },
        { path: 'topik/video', name: 'topik-video', component: () => import('@/topik/views/UserVideoView.vue'),    meta: { title: '视频', section: 'topik', requiresAuth: true } },
        { path: 'topik/audio', name: 'topik-audio', component: () => import('@/topik/views/UserAudioView.vue'),    meta: { title: '音频', section: 'topik', requiresAuth: true } },
        { path: 'topik/file',  name: 'topik-file',  component: () => import('@/topik/views/FileDownloadView.vue'), meta: { title: '资料', section: 'topik', requiresAuth: true } },

        // ── 课程 ────────────────────────────────────────────────
        {
          path: 'course',
          component: CourseScope,
          meta: { section: 'course', requiresAuth: true },
          children: [
            { path: '',        name: 'course',         component: () => import('@/course/views/HomeView.vue'),    meta: { title: '课程' } },
            { path: 'path',    name: 'course-path',    component: () => import('@/course/views/LearningPathView.vue'), meta: { title: '完整学习路线' } },
            { path: 'roadmap', name: 'course-roadmap', component: () => import('@/course/views/RoadmapView.vue'), meta: { title: '学习路线图' } },
            { path: 'mindmap', name: 'course-mindmap', component: () => import('@/course/views/MindmapView.vue'), meta: { title: '思维导图' } },
          ],
        },

        { path: 'me', name: 'me', component: () => import('@/core/views/AccountView.vue'), meta: { title: '我的账户', requiresAuth: true } },
      ],
    },

    // ── 管理后台（两个栏目合在一起） ─────────────────────────────
    {
      path: '/admin',
      component: () => import('@/core/layouts/AdminShell.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '',                 name: 'admin',              component: () => import('@/core/views/AdminDashboardView.vue'), meta: { title: '概览' } },
        { path: 'users',            name: 'admin-users',        component: () => import('@/topik/admin/UsersView.vue'),          meta: { title: '用户管理' } },
        { path: 'permissions',      name: 'admin-permissions',  component: () => import('@/topik/admin/PermissionsView.vue'),    meta: { title: '韩语 · 权限管理' } },
        { path: 'topik/video',      name: 'admin-topik-video',  component: () => import('@/topik/admin/VideoView.vue'),          meta: { title: '韩语 · 视频' } },
        { path: 'topik/audio',      name: 'admin-topik-audio',  component: () => import('@/topik/admin/AudioView.vue'),          meta: { title: '韩语 · 音频' } },
        { path: 'topik/pdf',        name: 'admin-topik-pdf',    component: () => import('@/topik/admin/PdfView.vue'),            meta: { title: '韩语 · 资料' } },
        {
          path: 'course',
          component: CourseScope,
          children: [
            { path: 'subjects',                 name: 'admin-course-subjects', component: () => import('@/course/admin/AdminSubjectControlView.vue'), meta: { title: '课程 · 科目' } },
            { path: 'subjects/:subjectId/videos', name: 'admin-course-videos', component: () => import('@/course/admin/AdminSubjectVideosView.vue'),  meta: { title: '课程 · 视频链接' } },
            { path: 'roadmap',                  name: 'admin-course-roadmap',  component: () => import('@/course/admin/AdminRoadmapView.vue'),        meta: { title: '课程 · 路线图' } },
          ],
        },
      ],
    },

    ...legacy,
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  const title = to.meta.title as string | undefined
  document.title = title ? `${title} · ${BRAND}` : BRAND

  const needsAdmin = to.matched.some((r) => r.meta.requiresAdmin)
  const needsAuth = needsAdmin || to.matched.some((r) => r.meta.requiresAuth)

  if (needsAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (needsAdmin && !auth.isAdmin) return { name: 'home' }

  if (to.name === 'login' && auth.isLoggedIn) {
    return (to.query.redirect as string) || { name: 'home' }
  }
})

export default router
