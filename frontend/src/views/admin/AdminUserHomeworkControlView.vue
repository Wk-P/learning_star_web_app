<template>
  <div>
    <h1 class="page-title">作业评分</h1>
    <div v-if="loading" class="skeleton" style="height:250px" />
    <div v-else-if="submission" class="card" style="max-width:560px">
      <div class="card-body" style="display:flex;flex-direction:column;gap:20px">
        <div class="desc-list">
          <div class="desc-row"><span class="desc-label">提交时间</span><span class="desc-value">{{ fmt(submission.submittedAt) }}</span></div>
          <div class="desc-row"><span class="desc-label">提交文件</span><span class="desc-value"><a :href="submission.fileUrl" target="_blank" class="btn btn-link btn-sm">{{ submission.fileName }}</a></span></div>
          <div class="desc-row"><span class="desc-label">当前评分</span><span class="desc-value">{{ submission.graded ? `${submission.score} 分` : '未评分' }}</span></div>
        </div>
        <div class="field">
          <label class="field-label">评分（0 - 100）</label>
          <div class="num-input" style="width:160px">
            <button @click="score = Math.max(0, score - 1)">−</button>
            <input type="number" v-model="score" min="0" max="100" />
            <button @click="score = Math.min(100, score + 1)">＋</button>
          </div>
        </div>
        <div><button class="btn btn-primary" :class="{ loading: saving }" @click="handleGrade">提交评分</button></div>
      </div>
    </div>
    <div v-else class="empty"><span class="empty-icon">📭</span><p>暂无提交记录...</p></div>
  </div>
</template>
<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { adminUserApi } from '@/api/admin'
import type { HomeworkSubmission } from '@/types'
const route = useRoute(); const toast = useToast()
const userId = Number(route.params.userId); const homeworkId = Number(route.params.homeworkId)
const loading = ref(false); const saving = ref(false)
const submission = ref<HomeworkSubmission | null>(null); const score = ref(0)
onMounted(async () => {
  loading.value = true
  try { const list = (await adminUserApi.homeworkList(userId)).data; submission.value = list.find(s => s.homeworkId === homeworkId) ?? null; if (submission.value?.graded) score.value = submission.value.score ?? 0 }
  finally { loading.value = false }
})
async function handleGrade() {
  saving.value = true
  try { await adminUserApi.gradeHomework(userId, homeworkId, score.value); if (submission.value) { submission.value.score = score.value; submission.value.graded = true }; toast.success('评分成功') }
  finally { saving.value = false }
}
</script>
