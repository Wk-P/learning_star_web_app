<template>
  <div>
    <!-- 科目标题 -->
    <div v-if="subject" class="subject-header" :style="{ borderLeftColor: subject.color }">
      <span class="subject-icon">{{ subject.icon }}</span>
      <div>
        <h1 style="font-size:22px;font-weight:700;margin-bottom:4px">{{ subject.name }}</h1>
        <p style="color:var(--c-text-2);font-size:14px">{{ subject.description || '暂无描述' }}</p>
      </div>
    </div>

    <div v-if="loading" class="grid grid-auto-lg" style="margin-top:20px">
      <div v-for="i in 4" :key="i" class="card" style="height:180px">
        <div class="card-body"><div class="skeleton skeleton-text" /><div class="skeleton skeleton-text" /></div>
      </div>
    </div>

    <div v-else-if="courses.length === 0" class="empty" style="margin-top:32px">
      <span class="empty-icon">📭</span>
      <p>该科目暂无课程...</p>
    </div>

    <div v-else class="grid grid-auto-lg" style="margin-top:20px">
      <div
        v-for="course in courses" :key="course.id"
        class="card card-hover"
        @click="router.push(`/courses/${course.id}`)"
      >
        <div class="card-body">
          <div class="flex-between" style="margin-bottom:10px">
            <span style="font-size:15px;font-weight:600">{{ course.name }}</span>
            <span :class="['badge', statusBadge(course.status)]">{{ statusLabel(course.status) }}</span>
          </div>
          <p style="font-size:13px;color:var(--c-text-2);margin-bottom:12px;line-height:1.6">
            {{ course.description || '暂无描述' }}
          </p>
          <div style="display:flex;flex-direction:column;gap:6px;font-size:13px;color:var(--c-text-2)">
            <div v-if="course.schedule">🕐 {{ course.schedule }}</div>
            <div>📅 共 {{ course.durationWeeks }} 周（{{ fmtDate(course.startTime) }} — {{ fmtDate(course.endTime) }}）</div>
          </div>
          <div style="margin-top:12px;display:flex;gap:8px;align-items:center">
            <span v-if="enrollment.isEnrolled(course.id)" class="badge badge-primary">已申请</span>
            <span v-else class="badge badge-info">未申请</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { subjectApi } from '@/api/course'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import type { Subject, Course, CourseStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const enrollment = useEnrollmentStore()
const { setSegments } = useBreadcrumb()
const subjectId = Number(route.params.subjectId)

const loading = ref(false)
const subject = ref<Subject | null>(null)
const courses = ref<Course[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [subjects, coursesRes] = await Promise.all([
      subjectApi.list(),
      subjectApi.courses(subjectId),
    ])
    subject.value = subjects.data.find(s => s.id === subjectId) ?? null
    courses.value = coursesRes.data
    if (subject.value) {
      setSegments([
        { label: '课程目录', path: '/courses' },
        { label: subject.value.name },
      ])
    }
  } finally {
    loading.value = false
  }
})

const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>

<style scoped>
.subject-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: var(--c-surface);
  border-radius: var(--r);
  border: 1px solid var(--c-border);
  border-left-width: 5px;
}
.subject-icon { font-size: 36px; flex-shrink: 0; }
</style>
