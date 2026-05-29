<template>
  <div>
    <h1 class="page-title">我的成绩</h1>
    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="scores.length === 0" class="empty"><span class="empty-icon">🏆</span><p>成绩列表为空...</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>课程名称</th><th>课程状态</th><th>最终成绩</th></tr></thead>
        <tbody>
          <tr v-for="s in scores" :key="s.courseId">
            <td>{{ s.courseName }}</td>
            <td><span :class="['badge', statusBadge(s.courseStatus)]">{{ statusLabel(s.courseStatus) }}</span></td>
            <td>
              <span v-if="s.courseStatus !== 'ended'" class="badge badge-info">课程进行中</span>
              <span v-else-if="s.graded" class="badge badge-success">{{ s.finalScore }} / 100</span>
              <span v-else class="badge badge-warning">未评分</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { courseApi } from '@/api/course'
import type { CourseScore, CourseStatus } from '@/types'
const loading = ref(false); const scores = ref<CourseScore[]>([])
onMounted(async () => { loading.value = true; try { scores.value = (await courseApi.myScores()).data } finally { loading.value = false } })
const statusLabel = (s: CourseStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: CourseStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>
