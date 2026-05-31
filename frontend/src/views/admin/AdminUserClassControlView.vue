<template>
  <div style="display:flex;flex-direction:column;gap:20px">
    <div v-if="loading" class="skeleton" style="height:300px" />
    <template v-else-if="cls">
      <div class="card">
        <div class="card-header">{{ cls.title }} — 出勤管理</div>
        <div class="card-body">
          <div class="desc-list" style="margin-bottom:20px">
            <div class="desc-row"><span class="desc-label">上课时间</span><span class="desc-value">{{ fmt(cls.classTime) }}</span></div>
            <div class="desc-row"><span class="desc-label">讲课人</span><span class="desc-value">{{ cls.teacherName || '暂无' }}</span></div>
            <div v-if="cls.memo" class="desc-row"><span class="desc-label">备注</span><span class="desc-value">{{ cls.memo }}</span></div>
          </div>
          <h3 class="section-title">出勤记录</h3>
          <div v-if="attendance.length === 0" class="empty"><span class="empty-icon">📋</span><p>出勤记录为空...</p></div>
          <div v-else class="table-wrap">
            <table class="table">
              <thead><tr><th>用户 ID</th><th>出勤</th><th>备注</th></tr></thead>
              <tbody>
                <tr v-for="r in attendance" :key="r.userId">
                  <td class="font-mono">{{ r.userId }}</td>
                  <td>
                    <label class="toggle"><input type="checkbox" v-model="r.present" /><span class="toggle-slider" /></label>
                  </td>
                  <td><input v-model="r.note" class="input" style="height:30px" /></td>
                </tr>
              </tbody>
            </table>
          </div>
          <button class="btn btn-primary mt-12" :class="{ loading: saving }" @click="handleSave">保存出勤</button>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { fmt } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { adminClassApi, adminCourseApi } from '@/api/admin'
import type { ClassSession, AttendanceRecord } from '@/types'
const route = useRoute(); const toast = useToast()
const courseId = Number(route.params.courseId); const classId = Number(route.params.classId)
const loading = ref(false); const saving = ref(false)
const cls = ref<ClassSession | null>(null); const attendance = ref<AttendanceRecord[]>([])
onMounted(async () => {
  loading.value = true
  try { const [cr, ar] = await Promise.all([adminClassApi.get(courseId, classId), adminCourseApi.attendance(courseId, classId)]); cls.value = cr.data; attendance.value = ar.data }
  finally { loading.value = false }
})
async function handleSave() {
  saving.value = true
  try { await adminCourseApi.updateAttendance(courseId, classId, attendance.value); toast.success('保存成功') }
  finally { saving.value = false }
}
</script>
