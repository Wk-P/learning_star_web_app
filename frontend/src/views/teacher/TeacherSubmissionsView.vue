<template>
  <div>
    <h1 class="page-title">学生提交 & 评分</h1>
    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="submissions.length === 0" class="empty">
      <span class="empty-icon">📭</span><p>暂无学生提交记录</p>
    </div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>学生</th><th>提交时间</th><th>文件</th><th>评分状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="s in submissions" :key="s.id">
            <td style="font-weight:500">用户 #{{ s.userId }}</td>
            <td class="text-secondary">{{ fmt(s.submittedAt) }}</td>
            <td>
              <a :href="s.fileUrl" target="_blank" class="btn btn-link btn-sm">{{ s.fileName || '查看文件' }}</a>
            </td>
            <td>
              <span v-if="s.graded" class="badge badge-success">{{ s.score }} 分</span>
              <span v-else class="badge badge-warning">未评分</span>
            </td>
            <td>
              <div style="display:flex;align-items:center;gap:8px">
                <div class="num-input" style="width:110px">
                  <button @click="scores[s.id] = Math.max(0, (scores[s.id] ?? 0) - 1)">−</button>
                  <input type="number" :value="scores[s.id] ?? s.score ?? 0" @input="scores[s.id] = Number(($event.target as HTMLInputElement).value)" min="0" :max="maxScore" />
                  <button @click="scores[s.id] = Math.min(maxScore, (scores[s.id] ?? 0) + 1)">＋</button>
                </div>
                <button
                  class="btn btn-primary btn-sm"
                  :class="{ loading: grading[s.id] }"
                  @click="handleGrade(s.id)"
                >
                  {{ grading[s.id] ? '' : '提交' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmt } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { teacherApi } from '@/api/teacher'
import type { HomeworkSubmission } from '@/types'

const route = useRoute(); const toast = useToast()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId); const homeworkId = Number(route.params.homeworkId)
const loading = ref(false); const maxScore = ref(100)
const submissions = ref<HomeworkSubmission[]>([])
const scores = ref<Record<number, number>>({})
const grading = ref<Record<number, boolean>>({})

onMounted(async () => {
  loading.value = true
  try {
    const [subRes, hwRes, courseRes] = await Promise.all([
      teacherApi.submissions(courseId, homeworkId),
      teacherApi.homeworkDetail(courseId, homeworkId),
      teacherApi.courseDetail(courseId),
    ])
    submissions.value = subRes.data
    maxScore.value = hwRes.data.maxScore
    for (const s of subRes.data) {
      if (s.graded && s.score != null) scores.value[s.id] = s.score
    }
    setSegments([
      { label: `${courseRes.data.name} — 作业管理`, path: `/admin/teacher/courses/${courseId}/homework` },
      { label: `${hwRes.data.name} 提交评分` },
    ])
  } finally { loading.value = false }
})

async function handleGrade(submissionId: number) {
  const score = scores.value[submissionId] ?? 0
  grading.value[submissionId] = true
  try {
    const { data } = await teacherApi.grade(courseId, homeworkId, submissionId, score)
    const i = submissions.value.findIndex(s => s.id === submissionId)
    if (i !== -1) submissions.value[i] = data
    toast.success('评分成功')
  } finally { grading.value[submissionId] = false }
}

</script>
