<template>
  <div>
    <h1 class="page-title">我的课程</h1>
    <div v-if="loading" class="grid grid-auto">
      <div v-for="i in 4" :key="i" class="card" style="height:140px">
        <div class="card-body"><div class="skeleton skeleton-text" /><div class="skeleton skeleton-text" /></div>
      </div>
    </div>
    <div v-else-if="courses.length === 0" class="empty">
      <span class="empty-icon">📭</span>
      <p>暂无分配课程，请联系管理员</p>
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
            <button class="btn btn-primary btn-sm" @click="router.push(`/teacher/courses/${c.id}/classes`)">
              课节管理
            </button>
            <button class="btn btn-secondary btn-sm" @click="router.push(`/teacher/courses/${c.id}/homework`)">
              作业 & 评分
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { teacherApi } from '@/api/teacher'
import type { Course, CourseStatus } from '@/types'

const router = useRouter()
const loading = ref(false)
const courses = ref<Course[]>([])

onMounted(async () => {
  loading.value = true
  try { courses.value = (await teacherApi.courses()).data }
  finally { loading.value = false }
})

const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>
