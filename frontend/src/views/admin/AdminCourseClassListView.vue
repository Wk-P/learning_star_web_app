<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">课节管理</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增课节</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="classes.length === 0" class="empty">
      <span class="empty-icon">📅</span>
      <p>该课程暂无课节，点击右上角新增</p>
    </div>
    <template v-else>
      <!-- 桌面表格 -->
      <div class="table-wrap cls-table">
        <table class="table">
          <thead>
            <tr>
              <th>课节</th>
              <th>上课时间</th>
              <th>讲课人</th>
              <th>会议室</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cls in classes" :key="cls.id">
              <td style="font-weight:500">{{ cls.title }}</td>
              <td class="text-secondary">{{ fmt(cls.classTime) }}</td>
              <td class="text-secondary">{{ cls.teacherName || '—' }}</td>
              <td>
                <a v-if="cls.meetingUrl" :href="cls.meetingUrl" target="_blank" class="btn btn-link btn-sm">链接</a>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <div class="table-actions">
                  <button v-if="auth.isAdmin || canManageCourse" class="btn btn-secondary btn-sm" @click="router.push(`/admin/courses/${courseId}/classes/${cls.id}`)">编辑</button>
                  <button v-if="auth.isAdmin || cls.teacherId === auth.user?.id" class="btn btn-danger btn-sm" @click="handleDelete(cls.id)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 移动端卡片 -->
      <div class="cls-cards">
        <div v-for="cls in classes" :key="cls.id" class="cls-card">
          <div class="cls-card-header">
            <span style="font-weight:600;font-size:15px">{{ cls.title }}</span>
            <a v-if="cls.meetingUrl" :href="cls.meetingUrl" target="_blank" class="btn btn-link btn-sm">会议室</a>
          </div>
          <div class="cls-card-meta">
            <span class="text-secondary text-sm">{{ fmt(cls.classTime) }}</span>
            <span v-if="cls.teacherName" class="text-secondary text-sm">{{ cls.teacherName }}</span>
          </div>
          <div class="cls-card-actions">
            <button v-if="auth.isAdmin || canManageCourse" class="btn btn-secondary btn-sm" @click="router.push(`/admin/courses/${courseId}/classes/${cls.id}`)">编辑</button>
            <button v-if="auth.isAdmin || cls.teacherId === auth.user?.id" class="btn btn-danger btn-sm" @click="handleDelete(cls.id)">删除</button>
          </div>
        </div>
      </div>
    </template>

    <!-- 新增课节弹窗 -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header">
            <span>新增课节</span>
            <button class="modal-close" @click="showCreate = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field">
              <label class="field-label">上课时间</label>
              <input type="datetime-local" v-model="form.classTime" class="input" style="height:36px;padding:0 12px" />
            </div>
            <div class="field">
              <label class="field-label">会议室链接</label>
              <input v-model="form.meetingUrl" class="input" placeholder="https://..." />
            </div>
            <div class="field">
              <label class="field-label">讲课人（可选）</label>
              <select v-model="form.teacherId" class="select">
                <option :value="null">— 暂不指定 —</option>
                <option v-for="t in teachers" :key="t.id" :value="t.id">
                  {{ t.username }}（{{ roleLabel(t.role) }}）
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCreate = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleCreate">创建</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { fmt, toDatetimeLocal, datetimeLocalToISO } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { adminClassApi, adminUserApi, adminCourseApi } from '@/api/admin'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { useAuthStore } from '@/stores/auth'
import type { ClassSession, AdminUserDetail, UserRole, Course } from '@/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { confirm } = useConfirm()
const { setSegments } = useBreadcrumb()

const auth = useAuthStore()
const courseId = Number(route.params.courseId)
const loading = ref(false)
const saving = ref(false)
const showCreate = ref(false)
const classes = ref<ClassSession[]>([])
const teachers = ref<AdminUserDetail[]>([])
const course = ref<Course | null>(null)

// 能管理课程：admin 全权；staff 是课程主讲人，或担任该课程下任意课节教师
const canManageCourse = computed(() =>
  auth.isAdmin ||
  course.value?.teacherId === auth.user?.id ||
  classes.value.some(c => c.teacherId === auth.user?.id)
)

const form = ref({
  week: 1,
  session: 1,
  classTime: '',
  meetingUrl: '',
  teacherId: null as number | null,
})

onMounted(async () => {
  loading.value = true
  try {
    const [clsRes, courseRes] = await Promise.all([
      adminClassApi.list(courseId),
      adminCourseApi.get(courseId),
    ])
    classes.value = clsRes.data
    course.value = courseRes.data
    if (auth.isAdmin) {
      const userRes = await adminUserApi.list()
      teachers.value = userRes.data.filter((u: AdminUserDetail) => u.role === 'staff' || u.role === 'admin')
    } else {
      teachers.value = auth.user ? [auth.user as unknown as AdminUserDetail] : []
    }
    setSegments([
      { label: '课程管理', path: '/admin/courses' },
      { label: `${courseRes.data.name} — 课节` },
    ])
  } finally {
    loading.value = false
  }
})

const roleLabel = (r: UserRole) => ({ user: '学生', staff: '教师', admin: '管理员' }[r])

function openCreate() {
  const maxWeek = classes.value.reduce((m, c) => Math.max(m, c.week), 0)
  form.value = {
    week: maxWeek + 1,
    session: 1,
    classTime: toDatetimeLocal(new Date().toISOString()),
    meetingUrl: '',
    teacherId: null,
  }
  showCreate.value = true
}

async function handleCreate() {
  if (!form.value.classTime) { toast.warning('请填写上课时间'); return }
  saving.value = true
  try {
    const payload = {
      courseId,
      week: form.value.week,
      session: form.value.session,
      classTime: form.value.classTime,
      meetingUrl: form.value.meetingUrl,
      ...(form.value.teacherId ? { teacherId: form.value.teacherId } : {}),
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { data } = await adminClassApi.create(courseId, { ...payload, classTime: datetimeLocalToISO((payload as any).classTime) })
    classes.value.push(data)
    classes.value.sort((a, b) => a.week !== b.week ? a.week - b.week : a.session - b.session)
    showCreate.value = false
    toast.success('创建成功')
  } finally {
    saving.value = false
  }
}

async function handleDelete(classId: number) {
  const ok = await confirm({ title: '删除课节', message: '确认删除该课节？', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await adminClassApi.delete(courseId, classId)
  classes.value = classes.value.filter(c => c.id !== classId)
  toast.success('删除成功')
}


</script>

<style scoped>
.cls-cards { display: none; }

@media (max-width: 700px) {
  .cls-table { display: none; }
  .cls-cards {
    display: flex; flex-direction: column; gap: 10px;
  }
  .cls-card {
    background: var(--c-surface);
    border: 1px solid var(--c-border);
    border-radius: var(--r);
    padding: 14px 16px;
    display: flex; flex-direction: column; gap: 6px;
  }
  .cls-card-header {
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
  }
  .cls-card-meta {
    display: flex; gap: 12px; flex-wrap: wrap;
  }
  .cls-card-actions {
    display: flex; gap: 8px; margin-top: 4px;
  }
}
</style>
