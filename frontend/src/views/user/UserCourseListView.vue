<template>
  <div>
    <h1 class="page-title">我的课程</h1>
    <div v-if="enrollment.enrollments.size === 0" class="empty"><span class="empty-icon">📚</span><p>我的课程为空...</p></div>
    <div v-else class="grid grid-auto">
      <div v-for="r in enrollment.enrollments.values()" :key="r.courseId" class="card card-hover" @click="router.push(`/courses/${r.courseId}`)">
        <div class="card-body">
          <div style="font-size:15px;font-weight:600;margin-bottom:10px">{{ r.courseName }}</div>
          <span :class="['badge', statusBadge(r.courseStatus)]">{{ statusLabel(r.courseStatus) }}</span>
          <div style="font-size:12px;color:var(--c-text-3);margin-top:10px">申请时间：{{ new Date(r.enrolledAt).toLocaleDateString('zh-CN') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useEnrollmentStore } from '@/stores/enrollment'
import type { CourseStatus } from '@/types'
const router = useRouter(); const enrollment = useEnrollmentStore()
const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>
