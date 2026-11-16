import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { BRAND, BRAND_CN } from '@/core/brand'

const AppShell = () => import('@/core/layouts/AppShell.vue')
const CourseScope = () => import('@/core/layouts/CourseScope.vue')

// 旧网址 → 新网址，书签与分享链接继续有效。合并前只有韩语，旧的语言栏目网址都指向 ko
const legacy: RouteRecordRaw[] = [
  { path: '/topik', redirect: '/language/ko' },
  { path: '/topik/video', redirect: '/language/ko/video' },
  { path: '/topik/audio', redirect: '/language/ko/audio' },
  { path: '/topik/file', redirect: '/language/ko/file' },
  { path: '/user', redirect: '/language/ko' },
  { path: '/user/dashboard', redirect: '/language/ko' },
  { path: '/user/video', redirect: '/language/ko/video' },
  { path: '/user/audio', redirect: '/language/ko/audio' },
  { path: '/user/file', redirect: '/language/ko/file' },
  { path: '/user/account', redirect: '/me' },
  { path: '/user/profile', redirect: '/me' },
  { path: '/home', redirect: '/course' },
  { path: '/roadmap', redirect: '/course/path' },
  { path: '/course/roadmap', redirect: '/course/path' },
  { path: '/mindmap', redirect: '/course/path' },
  { path: '/course/mindmap', redirect: '/course/path' },
  { path: '/admin/login', redirect: (to) => ({ path: '/login', query: { redirect: '/admin', ...to.query } }) },
  { path: '/admin/home', redirect: '/admin' },
  { path: '/admin/video', redirect: '/admin/language/resources' },
  { path: '/admin/audio', redirect: '/admin/language/resources' },
  { path: '/admin/pdf', redirect: '/admin/language/resources' },
  { path: '/admin/topik/:kind', redirect: '/admin/language/resources' },
  { path: '/admin/permissions', redirect: '/admin/language/permissions' },
  { path: '/admin/subjects', redirect: '/admin/course/subjects' },
  { path: '/admin/roadmap', redirect: '/admin' },
  { path: '/admin/course/roadmap', redirect: '/admin' },
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

        // ── 语言学习：分类 → 语言 → 视频 / 音频 / 资料 ──────────
        {
          path: 'language',
          meta: { section: 'language', requiresAuth: true },
          children: [
            { path: '',            name: 'language',       component: () => import('@/language/views/LanguageHubView.vue'),  meta: { title: '语言学习' } },
            { path: ':lang',       name: 'language-home',  component: () => import('@/language/views/DashboardView.vue'),    meta: { title: '概览' } },
            { path: ':lang/video', name: 'language-video', component: () => import('@/language/views/UserVideoView.vue'),    meta: { title: '视频' } },
            { path: ':lang/audio', name: 'language-audio', component: () => import('@/language/views/UserAudioView.vue'),    meta: { title: '音频' } },
            { path: ':lang/file',  name: 'language-file',  component: () => import('@/language/views/FileDownloadView.vue'), meta: { title: '资料' } },
          ],
        },

        // ── 课程 ────────────────────────────────────────────────
        {
          path: 'course',
          component: CourseScope,
          meta: { section: 'course', requiresAuth: true },
          children: [
            { path: '',        name: 'course',         component: () => import('@/course/views/HomeView.vue'),    meta: { title: '课程' } },
            { path: 'path',    name: 'course-path',    component: () => import('@/course/views/LearningPathView.vue'), meta: { title: '完整学习路线' } },
          ],
        },

        { path: 'me', name: 'me', component: () => import('@/core/views/AccountView.vue'), meta: { title: '我的账户', requiresAuth: true } },
      ],
    },

    // ── 管理后台 ─────────────────────────────────────────────────
    {
      path: '/admin',
      component: () => import('@/core/layouts/AdminShell.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '',                     name: 'admin',                    component: () => import('@/core/views/AdminDashboardView.vue'),     meta: { title: '概览' } },
        { path: 'users',                name: 'admin-users',              component: () => import('@/core/views/AdminUsersView.vue'),         meta: { title: '用户管理' } },
        { path: 'language/languages',   name: 'admin-language-languages', component: () => import('@/language/admin/LanguagesView.vue'),      meta: { title: '语言学习 · 分类与语言' } },
        { path: 'language/resources',   name: 'admin-language-resources', component: () => import('@/language/admin/ResourcesView.vue'),      meta: { title: '语言学习 · 学习资源' } },
        { path: 'language/permissions', name: 'admin-language-perms',     component: () => import('@/language/admin/PermissionsView.vue'),    meta: { title: '语言学习 · 学习权限' } },
        {
          path: 'course',
          component: CourseScope,
          children: [
            { path: 'subjects',                 name: 'admin-course-subjects', component: () => import('@/course/admin/AdminSubjectControlView.vue'), meta: { title: '课程 · 科目' } },
            { path: 'subjects/:subjectId/videos', name: 'admin-course-videos', component: () => import('@/course/admin/AdminSubjectVideosView.vue'),  meta: { title: '课程 · 视频链接' } },
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
  document.title = title ? `${title} · ${BRAND}` : `${BRAND} · ${BRAND_CN}`

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
