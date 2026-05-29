<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">作业管理</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增作业</button>
    </div>
    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="homework.length === 0" class="empty"><span class="empty-icon">📄</span><p>作业列表为空...</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>课程</th><th>作业名称</th><th>状态</th><th>截止时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="hw in homework" :key="hw.id">
            <td>
              <span class="hw-dot" :style="{ background: courseColor(hw.courseId) }" />
              {{ hw.courseName }}
            </td>
            <td style="font-weight:500">{{ hw.name }}</td>
            <td><span :class="['badge', statusBadge(hw.status)]">{{ statusLabel(hw.status) }}</span></td>
            <td class="text-secondary">{{ fmt(hw.endTime) }}</td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/homework/${hw.id}`)">详情</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(hw.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header"><span>新增作业</span><button class="modal-close" @click="showCreate = false">✕</button></div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field">
              <label class="field-label">所属课程</label>
              <select v-model="form.courseId" class="select">
                <option :value="0" disabled>— 请选择课程 —</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="field"><label class="field-label">作业名称</label><input v-model="form.name" class="input" /></div>
            <div class="field"><label class="field-label">作业描述</label><textarea v-model="form.description" class="textarea" /></div>
            <div class="field"><label class="field-label">开始时间</label><input type="datetime-local" v-model="form.startTime" /></div>
            <div class="field"><label class="field-label">截止时间</label><input type="datetime-local" v-model="form.endTime" /></div>
            <div class="field"><label class="field-label">满分</label>
              <div class="num-input" style="width:120px"><button @click="form.maxScore = Math.max(0, form.maxScore - 10)">−</button><input type="number" v-model="form.maxScore" min="0" /><button @click="form.maxScore += 10">＋</button></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCreate = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleCreate">创建</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal, datetimeLocalToISO } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { adminHomeworkApi, adminCourseApi } from '@/api/admin'
import type { Homework, Course, HomeworkStatus } from '@/types'

const router = useRouter(); const toast = useToast(); const { confirm } = useConfirm()
const loading = ref(false); const saving = ref(false); const showCreate = ref(false)
const homework = ref<Homework[]>([])
const courses = ref<Course[]>([])
const form = ref({ courseId: 0, name: '', description: '', startTime: '', endTime: '', maxScore: 100 })
const COLORS = ['#6366f1','#10b981','#f59e0b','#ef4444','#64748b','#8b5cf6']
const courseColor = (id: number) => COLORS[id % COLORS.length]

onMounted(async () => {
  loading.value = true
  try {
    const [hwRes, cRes] = await Promise.all([adminHomeworkApi.list(), adminCourseApi.list()])
    homework.value = hwRes.data
    courses.value = cRes.data
  } finally { loading.value = false }
})
function openCreate() { form.value = { courseId: courses.value[0]?.id ?? 0, name: '', description: '', startTime: '', endTime: '', maxScore: 100 }; showCreate.value = true }
async function handleCreate() {
  saving.value = true
  try {
    const payload = { ...form.value, startTime: datetimeLocalToISO(form.value.startTime), endTime: datetimeLocalToISO(form.value.endTime) }
    homework.value.unshift((await adminHomeworkApi.create(payload)).data)
    showCreate.value = false
    toast.success('创建成功')
  } finally { saving.value = false }
}
async function handleDelete(id: number) {
  const ok = await confirm({ title: '删除作业', message: '确认删除该作业？', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await adminHomeworkApi.delete(id); homework.value = homework.value.filter(h => h.id !== id); toast.success('删除成功')
}
const statusLabel = (s: HomeworkStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: HomeworkStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>
<style scoped>
.hw-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
</style>
