<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">课程管理</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增课程</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="courses.length === 0" class="empty"><span class="empty-icon">📖</span><p>课程列表为空</p></div>

    <div v-else class="table-wrap">
      <table class="table">
        <thead>
          <tr><th>科目</th><th>课程名称</th><th>描述</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in courses" :key="c.id">
            <td class="text-secondary text-sm">{{ c.subjectName || '—' }}</td>
            <td style="font-weight:500">{{ c.name }}</td>
            <td class="text-secondary text-sm">{{ c.description || '—' }}</td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="openEdit(c)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(c.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header">
            <span>{{ editTarget ? '编辑课程' : '新增课程' }}</span>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:16px;padding-top:20px">
            <div class="field">
              <label class="field-label">所属科目</label>
              <select v-model="form.subjectId" class="select">
                <option :value="null">— 不归属科目 —</option>
                <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.icon }} {{ s.name }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">课程名称</label>
              <input v-model="form.name" class="input" />
            </div>
            <div class="field">
              <label class="field-label">课程描述</label>
              <textarea v-model="form.description" class="textarea" />
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
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { adminCourseApi, adminSubjectApi } from '@/api/admin'
import type { Course, Subject } from '@/types'

const toast = useToast()
const { confirm } = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const courses = ref<Course[]>([])
const subjects = ref<Subject[]>([])
const editTarget = ref<Course | null>(null)
const form = ref({ subjectId: null as number | null, name: '', description: '' })

onMounted(async () => {
  loading.value = true
  try {
    const [cr, sr] = await Promise.all([adminCourseApi.list(), adminSubjectApi.list()])
    courses.value = cr.data
    subjects.value = sr.data
  } finally { loading.value = false }
})

function openCreate() {
  editTarget.value = null
  form.value = { subjectId: null, name: '', description: '' }
  showForm.value = true
}

function openEdit(c: Course) {
  editTarget.value = c
  form.value = { subjectId: c.subjectId, name: c.name, description: c.description }
  showForm.value = true
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value, subjectId: form.value.subjectId ?? undefined }
    if (editTarget.value) {
      const { data } = await adminCourseApi.update(editTarget.value.id, payload)
      const i = courses.value.findIndex(c => c.id === editTarget.value!.id)
      if (i !== -1) courses.value[i] = data
    } else {
      const { data } = await adminCourseApi.create(payload)
      courses.value.unshift(data)
    }
    showForm.value = false
    toast.success('保存成功')
  } finally { saving.value = false }
}

async function handleDelete(id: number) {
  const ok = await confirm('确认删除该课程？')
  if (!ok) return
  await adminCourseApi.delete(id)
  courses.value = courses.value.filter(c => c.id !== id)
  toast.success('删除成功')
}
</script>
