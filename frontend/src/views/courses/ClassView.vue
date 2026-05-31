<template>
  <div>
    <div v-if="loading" class="skeleton" style="height:300px" />
    <div v-else-if="cls" class="card">
      <div class="card-header">{{ cls.title }}</div>
      <div class="card-body" style="display:flex;flex-direction:column;gap:20px">
        <div class="desc-list">
          <div class="desc-row"><span class="desc-label">上课时间</span><span class="desc-value">{{ fmt(cls.classTime) }}</span></div>
          <div class="desc-row">
            <span class="desc-label">会议室</span>
            <span class="desc-value">
              <a v-if="meetingActive" :href="cls.meetingUrl" target="_blank" class="btn btn-primary btn-sm">进入会议室 →</a>
              <span v-else class="badge badge-warning">已过期</span>
            </span>
          </div>
          <div class="desc-row"><span class="desc-label">讲课人</span><span class="desc-value">{{ cls.teacherName || '暂无' }}</span></div>
          <div v-if="cls.memo" class="desc-row"><span class="desc-label">备注</span><span class="desc-value">{{ cls.memo }}</span></div>
        </div>

        <div>
          <h3 class="section-title">学生列表</h3>
          <div v-if="cls.students.length === 0" class="empty"><span class="empty-icon">👥</span><p>学生列表为空...</p></div>
          <div v-else style="display:flex;flex-wrap:wrap;gap:8px">
            <span v-for="s in cls.students" :key="s" class="badge badge-info">{{ s }}</span>
          </div>
        </div>

        <div>
          <h3 class="section-title">课程文件</h3>
          <div v-if="cls.files.length === 0" class="empty"><span class="empty-icon">📁</span><p>文件列表为空...</p></div>
          <div v-else style="display:flex;flex-direction:column;gap:8px">
            <a v-for="f in cls.files" :key="f.id" :href="f.url" target="_blank" class="btn btn-secondary btn-sm" style="justify-content:flex-start">📎 {{ f.name }}</a>
          </div>
        </div>

        <div v-if="isEnrolled">
          <button class="btn btn-primary" @click="router.push('/user/homework')">本周作业</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmt } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { courseApi } from '@/api/course'
import { classApi } from '@/api/class'
import type { ClassSession } from '@/types'

const route = useRoute(); const router = useRouter()
const enrollment = useEnrollmentStore()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId); const classId = Number(route.params.classId)
const loading = ref(false); const cls = ref<ClassSession | null>(null)
const isEnrolled = computed(() => enrollment.isEnrolled(courseId))
const meetingActive = computed(() => {
  if (!cls.value) return false
  const t = new Date(cls.value.classTime).getTime(); const n = Date.now()
  return n >= t - 30 * 60000 && n <= t + 2 * 3600000
})
onMounted(async () => {
  loading.value = true
  try {
    const [clsRes, courseRes] = await Promise.all([classApi.get(courseId, classId), courseApi.get(courseId)])
    cls.value = clsRes.data
    setSegments([
      { label: '课程目录', path: '/courses' },
      { label: courseRes.data.name, path: `/courses/${courseId}` },
      { label: cls.value.title },
    ])
  } finally { loading.value = false }
})
</script>
