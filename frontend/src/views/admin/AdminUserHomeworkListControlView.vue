<template>
  <div>
    <h1 class="page-title">用户作业管理</h1>
    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="submissions.length === 0" class="empty"><span class="empty-icon">📄</span><p>该用户作业为空...</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>作业</th><th>提交时间</th><th>评分状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="s in submissions" :key="s.id">
            <td>
              <span class="hw-dot" :style="{ background: hwColor(s.homeworkId) }" />
              作业 #{{ s.homeworkId }}
            </td>
            <td class="text-secondary">{{ fmt(s.submittedAt) }}</td>
            <td>
              <span v-if="s.graded" class="badge badge-success">{{ s.score }} 分</span>
              <span v-else class="badge badge-warning">未评分</span>
            </td>
            <td><button class="btn btn-link btn-sm" @click="router.push(`/admin/users/${userId}/homework/${s.homeworkId}`)">评分</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { fmt } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminUserApi } from '@/api/admin'
import type { HomeworkSubmission } from '@/types'
const route = useRoute(); const router = useRouter()
const userId = Number(route.params.userId); const loading = ref(false); const submissions = ref<HomeworkSubmission[]>([])
const COLORS = ['#6366f1','#10b981','#f59e0b','#ef4444','#64748b','#8b5cf6']
const hwColor = (id: number) => COLORS[id % COLORS.length]
onMounted(async () => { loading.value = true; try { submissions.value = (await adminUserApi.homeworkList(userId)).data } finally { loading.value = false } })
</script>
<style scoped>
.hw-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
</style>
