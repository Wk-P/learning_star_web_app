import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── 登录 ──────────────────────────────────────────────────────────────────
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },

    // ── 错误页 ────────────────────────────────────────────────────────────────
    {
      path: '/error',
      name: 'error',
      component: () => import('@/views/ErrorView.vue'),
      meta: { public: true },
    },

    // ── HomeLayout：学生课程浏览中心 ─────────────────────────────────────────
    {
      path: '/',
      component: () => import('@/layouts/HomeLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/home' },
        { path: 'home', name: 'home', component: () => import('@/views/home/HomeView.vue') },
        { path: 'courses', name: 'course-list', component: () => import('@/views/courses/CourseListView.vue') },
        { path: 'courses/subject/:subjectId', name: 'subject-courses', component: () => import('@/views/courses/SubjectCoursesView.vue') },
        { path: 'courses/:courseId', name: 'course', component: () => import('@/views/courses/CourseView.vue') },
        { path: 'courses/:courseId/classes/:classId', name: 'class', component: () => import('@/views/courses/ClassView.vue') },
      ],
    },

    // ── UserLayout：学生个人账户中心 ─────────────────────────────────────────
    {
      path: '/user',
      component: () => import('@/layouts/UserLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/user/profile' },
        { path: 'profile', name: 'user-profile', component: () => import('@/views/user/UserProfileView.vue') },
        { path: 'courses', name: 'user-courses', component: () => import('@/views/user/UserCourseListView.vue') },
        { path: 'homework', name: 'user-homework-list', component: () => import('@/views/user/UserHomeworkListView.vue') },
        { path: 'homework/:homeworkId', name: 'homework', component: () => import('@/views/user/HomeworkView.vue') },
        { path: 'scores', name: 'user-scores', component: () => import('@/views/user/UserScoresView.vue') },
      ],
    },

    // ── AdminLayout：统一后台（admin + staff 共用，按 role 精细化控制） ───────
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/home' },

        // admin 专属首页
        {
          path: 'home',
          name: 'admin-home',
          component: () => import('@/views/admin/AdminHomeView.vue'),
          meta: { requiresAdminOnly: true },
        },

        // ── 用户管理（仅 admin） ──────────────────────────────────────────────
        { path: 'users', name: 'admin-users', component: () => import('@/views/admin/AdminUserControlView.vue'), meta: { requiresAdminOnly: true } },
        { path: 'users/:userId/courses', name: 'admin-user-courses', component: () => import('@/views/admin/AdminUserCourseListControlView.vue'), meta: { requiresAdminOnly: true } },
        { path: 'users/:userId/courses/:courseId', name: 'admin-user-course', component: () => import('@/views/admin/AdminUserCourseControlView.vue'), meta: { requiresAdminOnly: true } },
        { path: 'users/:userId/courses/:courseId/classes/:classId', name: 'admin-user-class', component: () => import('@/views/admin/AdminUserClassControlView.vue'), meta: { requiresAdminOnly: true } },
        { path: 'users/:userId/homework', name: 'admin-user-homework-list', component: () => import('@/views/admin/AdminUserHomeworkListControlView.vue'), meta: { requiresAdminOnly: true } },
        { path: 'users/:userId/homework/:homeworkId', name: 'admin-user-homework', component: () => import('@/views/admin/AdminUserHomeworkControlView.vue'), meta: { requiresAdminOnly: true } },

        // ── 科目管理（admin + staff） ─────────────────────────────────────────
        { path: 'subjects', name: 'admin-subjects', component: () => import('@/views/admin/AdminSubjectControlView.vue') },

        // ── 课程管理（admin + staff，编辑权限由视图内控制） ──────────────────
        { path: 'courses', name: 'admin-courses', component: () => import('@/views/admin/AdminCourseControlView.vue') },
        { path: 'courses/:courseId/classes', name: 'admin-course-classes', component: () => import('@/views/admin/AdminCourseClassListView.vue') },
        { path: 'courses/:courseId/classes/:classId', name: 'admin-class', component: () => import('@/views/admin/AdminClassControlView.vue') },

        // ── 作业管理（admin + staff） ─────────────────────────────────────────
        { path: 'homework', name: 'admin-homework-list', component: () => import('@/views/admin/AdminHomeworkListView.vue') },
        { path: 'homework/:homeworkId', name: 'admin-homework', component: () => import('@/views/admin/AdminHomeworkView.vue') },

        // ── 教师专属视图（staff + admin，原 /teacher/* 迁移至此） ────────────
        { path: 'my-courses', name: 'teacher-home', component: () => import('@/views/teacher/TeacherHomeView.vue') },
        { path: 'teacher/courses/:courseId/classes', name: 'teacher-course-classes', component: () => import('@/views/teacher/TeacherCourseClassListView.vue') },
        { path: 'teacher/courses/:courseId/classes/:classId', name: 'teacher-class', component: () => import('@/views/teacher/TeacherClassView.vue') },
        { path: 'teacher/courses/:courseId/homework', name: 'teacher-homework', component: () => import('@/views/teacher/TeacherHomeworkListView.vue') },
        { path: 'teacher/courses/:courseId/homework/:homeworkId/submissions', name: 'teacher-submissions', component: () => import('@/views/teacher/TeacherSubmissionsView.vue') },
      ],
    },

    // ── 404 ───────────────────────────────────────────────────────────────────
    { path: '/:pathMatch(.*)*', redirect: '/error' },
  ],
})

// ── 全局路由守卫 ──────────────────────────────────────────────────────────────
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.public) return true

  if (!auth.isLoggedIn) return { name: 'login', query: { redirect: to.fullPath } }

  if (!auth.user) {
    try { await auth.fetchMe() }
    catch { return { name: 'login' } }
  }

  const role = auth.user?.role
  const isAdmin = role === 'admin'
  const isStaff = role === 'staff'

  // admin / staff 不进学生台前和个人中心
  if (auth.isStaff && (to.path.startsWith('/home') || to.path.startsWith('/user') || to.path.startsWith('/courses'))) {
    return { name: isAdmin ? 'admin-home' : 'admin-courses' }
  }

  // 仅 admin 可访问的页面，staff 重定向到课程管理
  if (to.meta.requiresAdminOnly && !isAdmin) {
    return auth.isStaff ? { name: 'admin-courses' } : { name: 'error' }
  }

  // admin + staff 才可访问后台（学生不能进）
  if (to.meta.requiresAdmin && !auth.isStaff) return { name: 'error' }

  return true
})

export default router
