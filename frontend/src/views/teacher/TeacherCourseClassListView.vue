<template>
  <div>
    <div class="flex-between" style="margin-bottom:20px;align-items:center">
      <h1 class="page-title" style="margin:0">课节管理</h1>
      <div class="flex" style="gap:10px">
        <button class="btn btn-secondary" @click="router.push(`/admin/teacher/courses/${courseId}/homework`)">作业 & 评分 →</button>
        <button class="btn btn-primary" @click="showCreate = true">＋ 新增课节</button>
      </div>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="classes.length === 0" class="empty">
      <span class="empty-icon">📅</span><p>暂无课节</p>
    </div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>课节</th><th>上课时间</th><th>讲课人</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="cls in classes" :key="cls.id">
            <td style="font-weight:500">{{ cls.title }}</td>
            <td class="text-secondary">{{ fmt(cls.classTime) }}</td>
            <td class="text-secondary">{{ cls.teacherName || '—' }}</td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/teacher/courses/${courseId}/classes/${cls.id}`)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(cls.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增课节 -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header"><span>新增课节</span><button class="modal-close" @click="showCreate = false">✕</button></div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field"><label class="field-label">上课时间</label><input type="datetime-local" v-model="form.classTime" class="input" style="height:36px;padding:0 12px" /></div>
            <div class="field"><label class="field-label">会议室链接</label><input v-model="form.meetingUrl" class="input" placeholder="https://..." /></div>
            <!-- 讲课人默认为当前教师 -->
            <div class="field">
              <label class="field-label">讲课人</label>
              <div class="input" style="background:var(--c-info-light);color:var(--c-text-2)">
                {{ auth.user?.username }}（自动）
              </div>
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
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { teacherApi } from '@/api/teacher'
import { useAuthStore } from '@/stores/auth'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import type { ClassSession } from '@/types'

const route = useRoute(); const router = useRouter()
const toast = useToast(); const { confirm } = useConfirm()
const auth = useAuthStore()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId)
const loading = ref(false); const saving = ref(false); const showCreate = ref(false)
const classes = ref<ClassSession[]>([])

const form = ref({ classTime: toDatetimeLocal(new Date().toISOString()), meetingUrl: '', teacherId: null as number | null })

onMounted(async () => {
  loading.value = true
  try {
    const [clsRes, courseRes] = await Promise.all([teacherApi.classes(courseId), teacherApi.courseDetail(courseId)])
    classes.value = clsRes.data
    form.value.teacherId = auth.user?.id ?? null
    setSegments([{ label: `${courseRes.data.name} — 课节管理` }])
  }
  finally { loading.value = false }
})

async function handleCreate() {
  if (!form.value.classTime) { toast.warning('请填写上课时间'); return }
  saving.value = true
  try {
    const { data } = await teacherApi.createClass(courseId, { ...form.value, classTime: datetimeLocalToISO(form.value.classTime) })
    classes.value.push(data)
    classes.value.sort((a, b) => new Date(a.classTime).getTime() - new Date(b.classTime).getTime())
    showCreate.value = false; toast.success('创建成功')
  } finally { saving.value = false }
}

async function handleDelete(classId: number) {
  const ok = await confirm({ title: '删除课节', message: '确认删除该课节？', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await teacherApi.deleteClass(courseId, classId)
  classes.value = classes.value.filter(c => c.id !== classId)
  toast.success('删除成功')
}

</script>
