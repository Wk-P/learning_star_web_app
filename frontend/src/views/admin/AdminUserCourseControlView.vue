<template>
  <div style="display:flex;flex-direction:column;gap:20px">
    <div v-if="loading" class="skeleton" style="height:200px" />
    <template v-else-if="course">
      <div class="card">
        <div class="card-header">{{ course.courseName }} — 课程管理</div>
        <div class="card-body" style="display:flex;flex-direction:column;gap:14px">
          <div class="field">
            <label class="field-label">申请时间</label>
            <input type="datetime-local" v-model="form.enrolledAt" />
          </div>
          <div><button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button></div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">课节列表</div>
        <div v-if="classes.length === 0" class="empty"><span class="empty-icon">📅</span><p>课节列表为空...</p></div>
        <div v-else class="table-wrap">
          <table class="table">
            <thead><tr><th>课节</th><th>上课时间</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="cls in classes" :key="cls.id">
                <td>{{ cls.title }}</td>
                <td>{{ fmt(cls.classTime) }}</td>
                <td><button class="btn btn-link btn-sm" @click="router.push(`/admin/users/${userId}/courses/${courseId}/classes/${cls.id}`)">详情</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { fmt, toDatetimeLocal, datetimeLocalToISO } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { adminUserApi, adminClassApi } from '@/api/admin'
import type { EnrollmentRecord, ClassSession } from '@/types'
const route = useRoute(); const router = useRouter(); const toast = useToast()
const userId = Number(route.params.userId); const courseId = Number(route.params.courseId)
const loading = ref(false); const saving = ref(false)
const course = ref<EnrollmentRecord | null>(null); const classes = ref<ClassSession[]>([])
const form = ref({ enrolledAt: '' })
onMounted(async () => {
  loading.value = true
  try {
    const [er, cr] = await Promise.all([adminUserApi.enrollments(userId), adminClassApi.list(courseId)])
    course.value = er.data.find(e => e.courseId === courseId) ?? null
    if (course.value) form.value.enrolledAt = toDatetimeLocal(course.value.enrolledAt)
    classes.value = cr.data
  } finally { loading.value = false }
})
async function handleSave() {
  saving.value = true
  try { await adminUserApi.updateEnrollmentTime(userId, courseId, datetimeLocalToISO(form.value.enrolledAt)); toast.success('保存成功') }
  finally { saving.value = false }
}
</script>
