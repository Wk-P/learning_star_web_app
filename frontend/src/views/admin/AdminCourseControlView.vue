<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">课程管理</h1>
      <span v-if="filterSubjectName" class="badge badge-primary" style="font-size:13px">
        {{ filterSubjectName }}
        <router-link :to="{ name: 'admin-courses' }" style="margin-left:4px;color:inherit;opacity:0.7">✕</router-link>
      </span>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增课程</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="courses.length === 0" class="empty"><span class="empty-icon">📖</span><p>课程列表为空...</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>科目</th><th>课程名称</th><th>主讲教师</th><th>上课日程</th><th>状态</th><th>时长</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="c in courses" :key="c.id">
            <td class="text-secondary text-sm">{{ c.subjectName || '—' }}</td>
            <td style="font-weight:500">{{ c.name }}</td>
            <td class="text-secondary">{{ c.teacherName || '—' }}</td>
            <td class="text-secondary">{{ c.schedule || '—' }}</td>
            <td><span :class="['badge', statusBadge(c.status)]">{{ statusLabel(c.status) }}</span></td>
            <td class="text-secondary">{{ c.durationWeeks }} 周</td>
            <td>
              <div class="table-actions">
                <button v-if="canEdit(c)" class="btn btn-secondary btn-sm" @click="openEdit(c)">编辑</button>
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/courses/${c.id}/classes`)">课节</button>
                <button v-if="canEdit(c)" class="btn btn-danger btn-sm" @click="handleDelete(c.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal modal-lg">
          <div class="modal-header">
            <span>{{ editTarget ? '编辑课程' : '新增课程' }}</span>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:16px;padding-top:20px">

            <!-- 科目：从科目页进入时已确定，新增时隐藏；编辑时始终显示 -->
            <div v-if="editTarget || !filterSubjectId" class="field">
              <label class="field-label">所属科目</label>
              <select v-model="form.subjectId" class="select">
                <option :value="null">— 不归属科目 —</option>
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
              </select>
            </div>

            <!-- 主讲教师 -->
            <div class="field">
              <label class="field-label">主讲教师</label>
              <select v-model="form.teacherId" class="select">
                <option :value="null">— 暂不指定 —</option>
                <option v-for="t in teachers" :key="t.id" :value="t.id">{{ t.displayName || t.username }}</option>
              </select>
            </div>

            <!-- 课程名称 -->
            <div class="field">
              <label class="field-label">课程名称</label>
              <input v-model="form.name" class="input" />
            </div>

            <!-- 课程描述 -->
            <div class="field">
              <label class="field-label">课程描述</label>
              <textarea v-model="form.description" class="textarea" />
            </div>

            <!-- 上课日程 -->
            <div class="field">
              <label class="field-label">上课日程</label>
              <!-- 星期选择 -->
              <div class="day-selector">
                <button
                  v-for="(day, i) in DAYS"
                  :key="i"
                  type="button"
                  :class="['day-btn', { active: selectedDays.includes(i) }]"
                  @click="toggleDay(i)"
                >
                  {{ day }}
                </button>
              </div>
              <!-- 时间段 -->
              <div class="time-row">
                <input
                  v-model="scheduleStart"
                  type="time"
                  class="input time-input"
                  placeholder="开始"
                />
                <span class="time-sep">—</span>
                <input
                  v-model="scheduleEnd"
                  type="time"
                  class="input time-input"
                  placeholder="结束"
                />
              </div>
              <!-- 预览 -->
              <div class="schedule-preview" v-if="schedulePreview">
                📅 {{ schedulePreview }}
              </div>
            </div>

            <!-- 课程时间（开始/结束日期） -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
              <div class="field">
                <label class="field-label">课程开始日期</label>
                <input type="date" v-model="form.startTime" class="input" />
              </div>
              <div class="field">
                <label class="field-label">课程结束日期</label>
                <input type="date" v-model="form.endTime" class="input" />
              </div>
            </div>

          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showForm = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { toDateLocal, dateToISOStart, dateToISOEnd } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { useAuthStore } from '@/stores/auth'
import { adminCourseApi, adminSubjectApi, adminClassApi, adminUserApi } from '@/api/admin'
import type { Course, Subject, AdminUserDetail, CourseStatus } from '@/types'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const auth = useAuthStore()

const canEdit = (c: Course) => auth.isAdmin || c.teacherId === auth.user?.id
const { confirm } = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const allCourses = ref<Course[]>([])
const subjects = ref<Subject[]>([])
const teachers = ref<AdminUserDetail[]>([])
const editTarget = ref<Course | null>(null)

const filterSubjectId = computed(() => route.query.subjectId ? Number(route.query.subjectId) : null)
const filterSubjectName = computed(() => filterSubjectId.value
  ? subjects.value.find(s => s.id === filterSubjectId.value)?.name ?? ''
  : ''
)
const courses = computed(() =>
  filterSubjectId.value
    ? allCourses.value.filter(c => c.subjectId === filterSubjectId.value)
    : allCourses.value
)

const form = ref({
  subjectId: null as number | null,
  teacherId: null as number | null,
  name: '',
  description: '',
  schedule: '',
  startTime: '',
  endTime: '',
})

// ── 日程选择器状态 ────────────────────────────────────────────────────────────
const DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const selectedDays = ref<number[]>([])
const scheduleStart = ref('')
const scheduleEnd = ref('')

function toggleDay(i: number) {
  const idx = selectedDays.value.indexOf(i)
  if (idx === -1) {
    selectedDays.value = [...selectedDays.value, i].sort((a, b) => a - b)
  } else {
    selectedDays.value = selectedDays.value.filter(d => d !== i)
  }
}

const schedulePreview = computed(() => {
  if (selectedDays.value.length === 0) return ''
  const days = selectedDays.value.map(i => DAYS[i]).join('、')
  const time = scheduleStart.value && scheduleEnd.value
    ? ` ${scheduleStart.value}–${scheduleEnd.value}`
    : ''
  return `每${days}${time}`
})

// 解析已有 schedule 字符串，回填选择器（格式：每周一、三 09:00–11:00）
function parseSchedule(schedule: string) {
  selectedDays.value = []
  scheduleStart.value = ''
  scheduleEnd.value = ''
  if (!schedule) return

  // 提取时间段
  const timeMatch = schedule.match(/(\d{2}:\d{2})[–-](\d{2}:\d{2})/)
  if (timeMatch) {
    scheduleStart.value = timeMatch[1] ?? ''
    scheduleEnd.value = timeMatch[2] ?? ''
  }

  // 提取星期
  selectedDays.value = DAYS
    .map((d, i) => (schedule.includes(d) ? i : -1))
    .filter(i => i !== -1)
}

// ── 表单操作 ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const [cr, sr, ur] = await Promise.all([
      adminCourseApi.list(),
      adminSubjectApi.list(),
      adminUserApi.list(),
    ])
    allCourses.value = cr.data
    subjects.value = sr.data
    teachers.value = ur.data.filter(u => u.role === 'staff')
  } finally { loading.value = false }
})

function openCreate() {
  editTarget.value = null
  form.value = { subjectId: filterSubjectId.value, teacherId: null, name: '', description: '', schedule: '', startTime: '', endTime: '' }
  parseSchedule('')
  showForm.value = true
}

function openEdit(c: Course) {
  editTarget.value = c
  form.value = {
    subjectId: c.subjectId,
    teacherId: c.teacherId,
    name: c.name,
    description: c.description,
    schedule: c.schedule,
    startTime: toDateLocal(c.startTime),
    endTime: toDateLocal(c.endTime),
  }
  parseSchedule(c.schedule)
  showForm.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      schedule: schedulePreview.value,
      subjectId: form.value.subjectId ?? undefined,
      teacherId: form.value.teacherId ?? undefined,
      // date → UTC ISO
      startTime: dateToISOStart(form.value.startTime),
      endTime: dateToISOEnd(form.value.endTime),
    }
    let savedCourse: Course
    if (editTarget.value) {
      const { data } = await adminCourseApi.update(editTarget.value.id, payload)
      const i = allCourses.value.findIndex(c => c.id === editTarget.value!.id)
      if (i !== -1) allCourses.value[i] = data
      savedCourse = data
    } else {
      const { data } = await adminCourseApi.create(payload)
      allCourses.value.unshift(data)
      savedCourse = data
    }

    // 日程有效时自动生成课节（有日程 + 有起止日期）
    if (schedulePreview.value && payload.startTime && payload.endTime) {
      try {
        const { data: genRes } = await adminClassApi.generate(savedCourse.id)
        toast.success(`课程已保存，已自动生成 ${genRes.count} 个课节`)
      } catch {
        toast.success('课程已保存（课节生成失败，请检查日程格式）')
      }
    } else {
      toast.success('保存成功')
    }

    showForm.value = false
  } finally { saving.value = false }
}

async function handleDelete(id: number) {
  const ok = await confirm({ title: '删除课程', message: '确认删除该课程？', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await adminCourseApi.delete(id)
  allCourses.value = allCourses.value.filter(c => c.id !== id)
  toast.success('删除成功')
}

const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>

<style scoped>
/* 星期选择器 */
.day-selector {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.day-btn {
  width: 44px;
  height: 44px;
  border-radius: var(--r-sm);
  border: 1.5px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text-2);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--t), border-color var(--t), color var(--t);
}
.day-btn:hover { border-color: var(--c-primary); color: var(--c-primary); }
.day-btn.active {
  background: var(--c-primary);
  border-color: var(--c-primary);
  color: #fff;
}
.day-btn.active:nth-child(6),
.day-btn.active:nth-child(7) {
  background: var(--c-danger);
  border-color: var(--c-danger);
}
.day-btn:nth-child(6),
.day-btn:nth-child(7) { color: var(--c-danger); }

/* 时间段 */
.time-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.time-input { width: 110px; height: 36px; }
.time-sep { color: var(--c-text-3); font-size: 16px; }

/* 预览 */
.schedule-preview {
  margin-top: 8px;
  padding: 8px 12px;
  background: var(--c-primary-light);
  border-radius: var(--r-sm);
  font-size: 13px;
  color: var(--c-primary);
  font-weight: 500;
}
</style>
