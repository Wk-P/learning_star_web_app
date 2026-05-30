<template>
  <div>
    <div class="flex-between" style="margin-bottom:20px;align-items:center">
      <h1 class="page-title" style="margin:0">作业 & 评分</h1>
      <div class="flex" style="gap:10px">
        <button class="btn btn-secondary" @click="router.push(`/admin/teacher/courses/${courseId}/classes`)">← 课节管理</button>
        <button class="btn btn-primary" @click="openCreate">＋ 新增作业</button>
      </div>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="homework.length === 0" class="empty"><span class="empty-icon">📄</span><p>暂无作业</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>作业名称</th><th>状态</th><th>截止时间</th><th>满分</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="hw in homework" :key="hw.id">
            <td style="font-weight:500">{{ hw.name }}</td>
            <td><span :class="['badge', statusBadge(hw.status)]">{{ statusLabel(hw.status) }}</span></td>
            <td class="text-secondary">{{ fmt(hw.endTime) }}</td>
            <td class="text-secondary">{{ hw.maxScore }}</td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="openEdit(hw)">编辑</button>
                <button class="btn btn-primary btn-sm" @click="router.push(`/admin/teacher/courses/${courseId}/homework/${hw.id}/submissions`)">评分</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(hw.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header"><span>{{ editTarget ? '编辑作业' : '新增作业' }}</span><button class="modal-close" @click="showForm = false">✕</button></div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field"><label class="field-label">作业名称</label><input v-model="form.name" class="input" /></div>
            <div class="field"><label class="field-label">作业描述</label><textarea v-model="form.description" class="textarea" /></div>
            <div class="field"><label class="field-label">开始时间</label><input type="datetime-local" v-model="form.startTime" class="input" style="height:36px;padding:0 12px" /></div>
            <div class="field"><label class="field-label">截止时间</label><input type="datetime-local" v-model="form.endTime" class="input" style="height:36px;padding:0 12px" /></div>
            <div class="field"><label class="field-label">满分</label>
              <div class="num-input" style="width:120px"><button @click="form.maxScore = Math.max(0, form.maxScore - 10)">−</button><input type="number" v-model="form.maxScore" min="0" /><button @click="form.maxScore += 10">＋</button></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showForm = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal, datetimeLocalToISO } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { teacherApi } from '@/api/teacher'
import type { Homework, HomeworkStatus } from '@/types'

const route = useRoute(); const router = useRouter()
const toast = useToast(); const { confirm } = useConfirm()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId)
const loading = ref(false); const saving = ref(false); const showForm = ref(false)
const homework = ref<Homework[]>([]); const editTarget = ref<Homework | null>(null)
const form = ref({ name: '', description: '', startTime: '', endTime: '', maxScore: 100 })

onMounted(async () => {
  loading.value = true
  try {
    const [hwRes, courseRes] = await Promise.all([teacherApi.homework(courseId), teacherApi.courseDetail(courseId)])
    homework.value = hwRes.data
    setSegments([{ label: `${courseRes.data.name} — 作业管理` }])
  }
  finally { loading.value = false }
})

function openCreate() { editTarget.value = null; form.value = { name: '', description: '', startTime: '', endTime: '', maxScore: 100 }; showForm.value = true }
function openEdit(hw: Homework) { editTarget.value = hw; form.value = { name: hw.name, description: hw.description, startTime: toDatetimeLocal(hw.startTime), endTime: toDatetimeLocal(hw.endTime), maxScore: hw.maxScore }; showForm.value = true }

async function handleSave() {
  saving.value = true
  try {
    if (editTarget.value) {
      const payload = { ...form.value, startTime: datetimeLocalToISO(form.value.startTime), endTime: datetimeLocalToISO(form.value.endTime) }
      const { data } = await teacherApi.updateHomework(courseId, editTarget.value.id, payload)
      const i = homework.value.findIndex(h => h.id === editTarget.value!.id); if (i !== -1) homework.value[i] = data
    } else {
      const payload = { ...form.value, startTime: datetimeLocalToISO(form.value.startTime), endTime: datetimeLocalToISO(form.value.endTime) }
      homework.value.push((await teacherApi.createHomework(courseId, payload)).data)
    }
    showForm.value = false; toast.success('保存成功')
  } finally { saving.value = false }
}
async function handleDelete(id: number) {
  const ok = await confirm({ title: '删除作业', message: '确认删除该作业？', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await teacherApi.deleteHomework(courseId, id); homework.value = homework.value.filter(h => h.id !== id); toast.success('删除成功')
}

const statusLabel = (s: HomeworkStatus) => ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: HomeworkStatus) => ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>
