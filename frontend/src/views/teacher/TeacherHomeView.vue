<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">我的课程</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增课程</button>
    </div>

    <div v-if="loading" class="grid grid-auto">
      <div v-for="i in 4" :key="i" class="card" style="height:140px">
        <div class="card-body"><div class="skeleton skeleton-text" /><div class="skeleton skeleton-text" /></div>
      </div>
    </div>
    <div v-else-if="courses.length === 0" class="empty">
      <span class="empty-icon">📭</span>
      <p>暂无课程，点击右上角新增</p>
    </div>
    <div v-else class="grid grid-auto-lg">
      <div v-for="c in courses" :key="c.id" class="card">
        <div class="card-body">
          <div class="flex-between" style="margin-bottom:8px">
            <span style="font-size:15px;font-weight:700">{{ c.name }}</span>
            <span :class="['badge', statusBadge(c.status)]">{{ statusLabel(c.status) }}</span>
          </div>
          <div style="font-size:13px;color:var(--c-text-2);margin-bottom:4px">{{ c.subjectName || '未分科' }}</div>
          <div v-if="c.schedule" style="font-size:13px;color:var(--c-text-3);margin-bottom:12px">🕐 {{ c.schedule }}</div>
          <div style="font-size:12px;color:var(--c-text-3);margin-bottom:14px">
            📅 {{ fmtDate(c.startTime) }} — {{ fmtDate(c.endTime) }}（{{ c.durationWeeks }} 周）
          </div>
          <div class="flex" style="gap:8px;flex-wrap:wrap">
            <button class="btn btn-primary btn-sm" @click="router.push(`/admin/teacher/courses/${c.id}/classes`)">
              课节管理
            </button>
            <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/teacher/courses/${c.id}/homework`)">
              作业 & 评分
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal modal-lg">
          <div class="modal-header">
            <span>新增课程</span>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:16px;padding-top:20px">

            <div class="field">
              <label class="field-label">所属科目</label>
              <select v-model="form.subjectId" class="select">
                <option :value="null">— 不归属科目 —</option>
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
              </select>
            </div>

            <div class="field">
              <label class="field-label">课程名称</label>
              <input v-model="form.name" class="input" placeholder="请输入课程名称" />
            </div>

            <div class="field">
              <label class="field-label">课程描述</label>
              <textarea v-model="form.description" class="textarea" />
            </div>

            <div class="field">
              <label class="field-label">上课日程</label>
              <div class="day-selector">
                <button
                  v-for="(day, i) in DAYS" :key="i" type="button"
                  :class="['day-btn', { active: selectedDays.includes(i) }]"
                  @click="toggleDay(i)"
                >{{ day }}</button>
              </div>
              <div class="time-row">
                <input v-model="scheduleStart" type="time" class="input time-input" />
                <span class="time-sep">—</span>
                <input v-model="scheduleEnd" type="time" class="input time-input" />
              </div>
              <div class="schedule-preview" v-if="schedulePreview">📅 {{ schedulePreview }}</div>
            </div>

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
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleCreate">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { fmtDate, dateToISOStart, dateToISOEnd } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { teacherApi } from '@/api/teacher'
import { adminClassApi } from '@/api/admin'
import http from '@/api/http'
import type { Course, Subject, CourseStatus } from '@/types'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const courses = ref<Course[]>([])
const subjects = ref<Subject[]>([])

const form = ref({ subjectId: null as number | null, name: '', description: '', startTime: '', endTime: '' })

const DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const selectedDays = ref<number[]>([])
const scheduleStart = ref('')
const scheduleEnd = ref('')

function toggleDay(i: number) {
  const idx = selectedDays.value.indexOf(i)
  if (idx === -1) selectedDays.value = [...selectedDays.value, i].sort((a, b) => a - b)
  else selectedDays.value = selectedDays.value.filter(d => d !== i)
}

const schedulePreview = computed(() => {
  if (selectedDays.value.length === 0) return ''
  const days = selectedDays.value.map(i => DAYS[i]).join('、')
  const time = scheduleStart.value && scheduleEnd.value ? ` ${scheduleStart.value}–${scheduleEnd.value}` : ''
  return `每${days}${time}`
})

onMounted(async () => {
  loading.value = true
  try {
    const [cr, sr] = await Promise.all([
      teacherApi.courses(),
      http.get<Subject[]>('/api/subjects/'),
    ])
    courses.value = cr.data
    subjects.value = sr.data
  } finally { loading.value = false }
})

function openCreate() {
  form.value = { subjectId: null, name: '', description: '', startTime: '', endTime: '' }
  selectedDays.value = []
  scheduleStart.value = ''
  scheduleEnd.value = ''
  showForm.value = true
}

async function handleCreate() {
  if (!form.value.name.trim()) { toast.warning('请填写课程名称'); return }
  if (!form.value.startTime || !form.value.endTime) { toast.warning('请选择课程起止日期'); return }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      schedule: schedulePreview.value,
      subjectId: form.value.subjectId ?? undefined,
      startTime: dateToISOStart(form.value.startTime),
      endTime: dateToISOEnd(form.value.endTime),
    }
    const { data: newCourse } = await teacherApi.createCourse(payload)
    courses.value.unshift(newCourse)

    if (schedulePreview.value) {
      try {
        const { data: genRes } = await adminClassApi.generate(newCourse.id)
        toast.success(`课程已创建，已自动生成 ${genRes.count} 个课节`)
      } catch {
        toast.success('课程已创建（课节生成失败，可手动添加）')
      }
    } else {
      toast.success('课程已创建')
    }
    showForm.value = false
  } finally { saving.value = false }
}

const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>

<style scoped>
.day-selector { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
.day-btn {
  width:44px; height:44px; border-radius:var(--r-sm);
  border:1.5px solid var(--c-border); background:var(--c-surface);
  color:var(--c-text-2); font-size:13px; font-weight:500; cursor:pointer;
  transition:background var(--t),border-color var(--t),color var(--t);
}
.day-btn:hover { border-color:var(--c-primary); color:var(--c-primary); }
.day-btn.active { background:var(--c-primary); border-color:var(--c-primary); color:#fff; }
.day-btn.active:nth-child(6), .day-btn.active:nth-child(7) { background:var(--c-danger); border-color:var(--c-danger); }
.day-btn:nth-child(6), .day-btn:nth-child(7) { color:var(--c-danger); }
.time-row { display:flex; align-items:center; gap:10px; }
.time-input { width:110px; height:36px; }
.time-sep { color:var(--c-text-3); font-size:16px; }
.schedule-preview {
  margin-top:8px; padding:8px 12px;
  background:var(--c-primary-light); border-radius:var(--r-sm);
  font-size:13px; color:var(--c-primary); font-weight:500;
}
</style>
