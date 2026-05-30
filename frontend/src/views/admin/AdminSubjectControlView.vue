<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">科目管理</h1>
      <div class="toolbar-spacer" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增科目</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="subjects.length === 0" class="empty"><span class="empty-icon">🗂️</span><p>科目列表为空...</p></div>
    <div v-else class="grid grid-auto">
      <div v-for="s in subjects" :key="s.id" class="card">
        <div class="card-body">
          <div class="flex-between" style="margin-bottom:10px">
            <div class="flex" style="gap:10px;align-items:center">
              <span style="font-size:28px">{{ s.icon }}</span>
              <div>
                <div style="font-size:15px;font-weight:600">{{ s.name }}</div>
                <router-link
                  :to="{ name: 'admin-courses', query: { subjectId: s.id } }"
                  class="subject-course-link"
                >{{ s.courseCount }} 门课程 →</router-link>
              </div>
            </div>
            <span class="color-dot" :style="{ background: s.color }" />
          </div>
          <p style="font-size:13px;color:var(--c-text-2);margin-bottom:14px;min-height:36px">
            {{ s.description || '暂无描述' }}
          </p>
          <div class="flex" style="gap:8px">
            <button class="btn btn-secondary btn-sm" @click="openEdit(s)">编辑</button>
            <button class="btn btn-danger btn-sm" @click="handleDelete(s.id)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header">
            <span>{{ editTarget ? '编辑科目' : '新增科目' }}</span>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field"><label class="field-label">科目名称</label><input v-model="form.name" class="input" /></div>
            <div class="field"><label class="field-label">描述</label><textarea v-model="form.description" class="textarea" /></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
              <div class="field">
                <label class="field-label">图标（emoji）</label>
                <input v-model="form.icon" class="input" placeholder="📖" maxlength="2" style="font-size:20px;text-align:center" />
              </div>
              <div class="field">
                <label class="field-label">主题色（hex）</label>
                <div style="display:flex;gap:8px;align-items:center">
                  <input v-model="form.color" class="input" placeholder="#6366f1" />
                  <input type="color" v-model="form.color" style="width:36px;height:36px;border:none;padding:0;border-radius:4px;cursor:pointer" />
                </div>
              </div>
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
import { adminSubjectApi } from '@/api/admin'
import type { Subject } from '@/types'

const toast = useToast(); const { confirm } = useConfirm()
const loading = ref(false); const saving = ref(false); const showForm = ref(false)
const subjects = ref<Subject[]>([])
const editTarget = ref<Subject | null>(null)
const form = ref({ name: '', description: '', icon: '📖', color: '#6366f1' })

onMounted(async () => { loading.value = true; try { subjects.value = (await adminSubjectApi.list()).data } finally { loading.value = false } })

function openCreate() { editTarget.value = null; form.value = { name: '', description: '', icon: '📖', color: '#6366f1' }; showForm.value = true }
function openEdit(s: Subject) { editTarget.value = s; form.value = { name: s.name, description: s.description, icon: s.icon, color: s.color }; showForm.value = true }

async function handleSave() {
  saving.value = true
  try {
    if (editTarget.value) {
      const { data } = await adminSubjectApi.update(editTarget.value.id, form.value)
      const i = subjects.value.findIndex(s => s.id === editTarget.value!.id); if (i !== -1) subjects.value[i] = data
    } else {
      subjects.value.push((await adminSubjectApi.create(form.value)).data)
    }
    showForm.value = false; toast.success('保存成功')
  } finally { saving.value = false }
}

async function handleDelete(id: number) {
  const ok = await confirm({ title: '删除科目', message: '确认删除该科目？已关联的课程将变为无科目。', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await adminSubjectApi.delete(id); subjects.value = subjects.value.filter(s => s.id !== id); toast.success('删除成功')
}
</script>

<style scoped>
.color-dot { width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0; }
.subject-course-link {
  font-size: 12px; color: var(--c-primary); font-weight: 500;
  transition: color var(--t);
}
.subject-course-link:hover { color: var(--c-primary-hover); text-decoration: underline; }
</style>
