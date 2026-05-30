<template>
  <div style="display:flex;flex-direction:column;gap:20px">
    <div v-if="loading" class="skeleton" style="height:300px" />
    <template v-else-if="cls">
      <div class="card">
        <div class="card-header">{{ cls.title }} — 编辑</div>
        <div class="card-body" style="display:flex;flex-direction:column;gap:14px">
          <div class="field">
            <label class="field-label">上课时间</label>
            <input type="datetime-local" v-model="form.classTime" class="input" style="height:36px;padding:0 12px" />
          </div>
          <div class="field">
            <label class="field-label">会议室链接</label>
            <input v-model="form.meetingUrl" class="input" />
          </div>
          <div class="field">
            <label class="field-label">讲课人</label>
            <div class="input" style="background:var(--c-info-light);color:var(--c-text-2)">
              {{ cls.teacherName || '（未指定）' }}
            </div>
          </div>
          <div>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button>
          </div>
        </div>
      </div>

      <!-- 资料文件 -->
      <div class="card">
        <div class="card-header">
          课节资料
          <div style="display:flex;align-items:center;gap:8px">
            <input ref="fileInputRef" type="file" style="display:none" @change="handleUpload" />
            <button class="btn btn-primary btn-sm" :class="{ loading: uploading }" :disabled="uploading" @click="fileInputRef?.click()">
              {{ uploading ? '' : '上传资料' }}
            </button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="cls.files.length === 0" class="empty" style="padding:24px">
            <span class="empty-icon">📁</span><p>暂无资料文件</p>
          </div>
          <div v-else style="display:flex;flex-direction:column;gap:8px">
            <div v-for="f in cls.files" :key="f.id" class="file-row">
              <a :href="f.url" target="_blank" class="file-name">📎 {{ f.name }}</a>
              <button class="btn btn-danger btn-sm" @click="handleDeleteFile(f.id)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 出勤表 -->
      <div class="card">
        <div class="card-header">出勤记录</div>
        <div class="card-body">
          <div v-if="attendance.length === 0" class="empty"><span class="empty-icon">📋</span><p>出勤记录为空...</p></div>
          <div v-else class="table-wrap">
            <table class="table">
              <thead><tr><th>用户 ID</th><th>出勤</th><th>备注</th></tr></thead>
              <tbody>
                <tr v-for="r in attendance" :key="r.userId">
                  <td class="font-mono">{{ r.userId }}</td>
                  <td><label class="toggle"><input type="checkbox" v-model="r.present" /><span class="toggle-slider" /></label></td>
                  <td><input v-model="r.note" class="input" style="height:30px" /></td>
                </tr>
              </tbody>
            </table>
          </div>
          <button class="btn btn-secondary mt-12" :class="{ loading: savingAtt }" @click="handleSaveAtt">保存出勤</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { toDatetimeLocal, datetimeLocalToISO } from '@/utils/time'
import { useToast } from '@/composables/useToast'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { teacherApi } from '@/api/teacher'
import type { ClassSession, AttendanceRecord } from '@/types'

const route = useRoute()
const toast = useToast()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId)
const classId = Number(route.params.classId)
const loading = ref(false)
const saving = ref(false)
const savingAtt = ref(false)
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const cls = ref<ClassSession | null>(null)
const attendance = ref<AttendanceRecord[]>([])
const form = ref({ classTime: '', meetingUrl: '', teacherId: null as number | null })

onMounted(async () => {
  loading.value = true
  try {
    const [cr, ar] = await Promise.all([
      teacherApi.classDetail(courseId, classId),
      teacherApi.attendance(courseId, classId),
    ])
    cls.value = cr.data
    attendance.value = ar.data
    const courseRes = await teacherApi.courseDetail(courseId)
    setSegments([
      { label: `${courseRes.data.name} — 课节管理`, path: `/admin/teacher/courses/${courseId}/classes` },
      { label: cls.value.title },
    ])
    form.value = {
      classTime: toDatetimeLocal(cls.value.classTime),
      meetingUrl: cls.value.meetingUrl,
      teacherId: cls.value.teacherId ?? null,
    }
  } finally { loading.value = false }
})

async function handleSave() {
  saving.value = true
  try {
    await teacherApi.updateClass(courseId, classId, { ...form.value, classTime: datetimeLocalToISO(form.value.classTime) })
    toast.success('保存成功')
  } finally { saving.value = false }
}

async function handleSaveAtt() {
  savingAtt.value = true
  try {
    await teacherApi.updateAttendance(courseId, classId, attendance.value)
    toast.success('出勤已保存')
  } finally { savingAtt.value = false }
}

async function handleUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]; if (!file) return
  if (file.size > 50 * 1024 * 1024) { toast.error('文件不能超过 50MB'); input.value = ''; return }
  uploading.value = true
  try {
    const { data } = await teacherApi.uploadClassFile(courseId, classId, file)
    cls.value!.files.push(data); toast.success('上传成功')
  } catch { toast.error('上传失败') }
  finally { uploading.value = false; input.value = '' }
}

async function handleDeleteFile(fileId: number) {
  await teacherApi.deleteClassFile(courseId, classId, fileId)
  cls.value!.files = cls.value!.files.filter(f => f.id !== fileId)
  toast.success('已删除')
}
</script>

<style scoped>
.file-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 10px 14px; border-radius: var(--r-sm);
  border: 1px solid var(--c-border); background: var(--c-surface);
}
.file-name {
  color: var(--c-primary); font-size: 13px; font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.file-name:hover { text-decoration: underline; }
</style>
