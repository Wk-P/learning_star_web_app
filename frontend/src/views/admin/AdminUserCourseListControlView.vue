<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">用户课程管理</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openAdd">＋ 加入课程</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="enrollments.length === 0" class="empty">
      <span class="empty-icon">📚</span>
      <p>该用户暂未加入任何课程</p>
    </div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>课程名称</th><th>课程状态</th><th>申请时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="r in enrollments" :key="r.courseId">
            <td>
              <span class="course-dot" :style="{ background: courseColor(r.courseId) }" />
              {{ r.courseName }}
            </td>
            <td><span :class="['badge', statusBadge(r.courseStatus)]">{{ statusLabel(r.courseStatus) }}</span></td>
            <td class="text-secondary">{{ new Date(r.enrolledAt).toLocaleDateString('zh-CN') }}</td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/users/${userId}/courses/${r.courseId}`)">详情</button>
                <button class="btn btn-danger btn-sm" @click="handleRemove(r.courseId)">移除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 加入课程弹窗 -->
    <Teleport to="body">
      <div v-if="showAdd" class="modal-backdrop" @click.self="showAdd = false">
        <div class="modal">
          <div class="modal-header">
            <span>将用户加入课程</span>
            <button class="modal-close" @click="showAdd = false">✕</button>
          </div>
          <div class="modal-body" style="padding-top:20px;display:flex;flex-direction:column;gap:14px">
            <div class="field">
              <label class="field-label">选择课程</label>
              <select v-model="selectedCourseId" class="select">
                <option :value="0" disabled>— 请选择课程 —</option>
                <option
                  v-for="c in availableCourses"
                  :key="c.id"
                  :value="c.id"
                >
                  {{ c.name }}
                  <template v-if="c.subjectName">（{{ c.subjectName }}）</template>
                  — {{ statusLabel2(c.status) }}
                </option>
              </select>
              <div v-if="availableCourses.length === 0" style="font-size:13px;color:var(--c-text-3);margin-top:6px">
                该用户已加入所有课程
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAdd = false">取消</button>
            <button
              class="btn btn-primary"
              :class="{ loading: adding }"
              :disabled="!selectedCourseId"
              @click="handleAdd"
            >
              加入
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { adminUserApi, adminCourseApi } from '@/api/admin'
import type { EnrollmentRecord, Course, CourseStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const { confirm } = useConfirm()

const userId = Number(route.params.userId)
const loading = ref(false)
const adding = ref(false)
const showAdd = ref(false)
const enrollments = ref<EnrollmentRecord[]>([])
const allCourses = ref<Course[]>([])
const selectedCourseId = ref(0)

// 过滤掉已加入的课程
const availableCourses = computed(() => {
  const enrolledIds = new Set(enrollments.value.map(e => e.courseId))
  return allCourses.value.filter(c => !enrolledIds.has(c.id))
})

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#64748b', '#8b5cf6']
const courseColor = (id: number) => COLORS[id % COLORS.length]

onMounted(async () => {
  loading.value = true
  try {
    const [er, cr] = await Promise.all([
      adminUserApi.enrollments(userId),
      adminCourseApi.list(),
    ])
    enrollments.value = er.data
    allCourses.value = cr.data
  } finally {
    loading.value = false }
})

function openAdd() {
  selectedCourseId.value = availableCourses.value[0]?.id ?? 0
  showAdd.value = true
}

async function handleAdd() {
  if (!selectedCourseId.value) return
  adding.value = true
  try {
    const { data } = await adminUserApi.addEnrollment(userId, selectedCourseId.value)
    enrollments.value.push(data)
    showAdd.value = false
    toast.success('已成功加入课程')
  } finally {
    adding.value = false
  }
}

async function handleRemove(courseId: number) {
  const ok = await confirm({ title: '移除课程', message: '确认移除该用户的课程申请？', type: 'warning' })
  if (!ok) return
  await adminUserApi.removeEnrollment(userId, courseId)
  enrollments.value = enrollments.value.filter(e => e.courseId !== courseId)
  toast.success('已移除')
}

function statusLabel(s: CourseStatus) { return { not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s] }
function statusLabel2(s: CourseStatus) { return { not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s] }
function statusBadge(s: CourseStatus) { return { not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s] }
</script>

<style scoped>
.course-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
</style>
