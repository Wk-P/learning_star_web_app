<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">{{ homeworkName }} — 提交记录</h1>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="submissions.length === 0" class="empty">
      <span class="empty-icon">📄</span><p>暂无提交记录</p>
    </div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr>
            <th>学生</th>
            <th>提交时间</th>
            <th>文件</th>
            <th>评分</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in submissions" :key="s.id">
            <td style="font-weight:500">{{ s.userId }}</td>
            <td class="text-secondary">{{ fmt(s.submittedAt) }}</td>
            <td>
              <a v-if="s.fileUrl" :href="s.fileUrl" target="_blank" class="btn btn-link btn-sm">
                📎 {{ s.fileName || '查看文件' }}
              </a>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <span v-if="s.graded" class="badge badge-success">{{ s.score }} 分</span>
              <span v-else class="badge badge-info">未评分</span>
            </td>
            <td>
              <div style="display:flex;align-items:center;gap:8px">
                <input
                  type="number"
                  v-model.number="scoreInputs[s.id]"
                  class="input"
                  style="width:70px;height:30px"
                  :placeholder="s.score != null ? String(s.score) : '分数'"
                  min="0"
                />
                <button
                  class="btn btn-primary btn-sm"
                  :class="{ loading: grading[s.id] }"
                  @click="handleGrade(s)"
                >评分</button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { adminHomeworkApi } from '@/api/admin'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import type { HomeworkSubmission } from '@/types'

const route = useRoute()
const toast = useToast()
const { setSegments } = useBreadcrumb()

const homeworkId = Number(route.params.homeworkId)
const loading = ref(false)
const homeworkName = ref('')
const submissions = ref<HomeworkSubmission[]>([])
const scoreInputs = reactive<Record<number, number | null>>({})
const grading = reactive<Record<number, boolean>>({})

onMounted(async () => {
  loading.value = true
  try {
    const [subRes, hwRes] = await Promise.all([
      adminHomeworkApi.submissions(homeworkId),
      adminHomeworkApi.get(homeworkId),
    ])
    submissions.value = subRes.data
    homeworkName.value = hwRes.data.name
    for (const s of submissions.value) {
      scoreInputs[s.id] = s.score ?? null
    }
    setSegments([
      { label: '作业管理', path: '/admin/homework' },
      { label: `${hwRes.data.name} — 提交记录` },
    ])
  } finally {
    loading.value = false
  }
})

async function handleGrade(s: HomeworkSubmission) {
  const score = scoreInputs[s.id]
  if (score == null || score < 0) { toast.warning('请输入有效分数'); return }
  grading[s.id] = true
  try {
    const { data } = await adminHomeworkApi.grade(homeworkId, s.id, score)
    const idx = submissions.value.findIndex(x => x.id === s.id)
    if (idx !== -1) submissions.value[idx] = data
    toast.success('评分成功')
  } finally {
    grading[s.id] = false
  }
}
</script>
