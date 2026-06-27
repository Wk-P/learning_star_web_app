<template>
  <div>
    <div v-if="loading" style="display:flex;flex-direction:column;gap:16px">
      <div class="skeleton skeleton-text" style="height:32px;width:40%" />
      <div class="skeleton" style="height:120px" />
    </div>
    <template v-else-if="course">
      <div style="margin-bottom:20px">
        <div style="font-size:13px;color:var(--c-text-3);margin-bottom:6px">{{ course.subjectName }}</div>
        <h1 style="font-size:22px;font-weight:700;margin-bottom:10px">{{ course.name }}</h1>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="course-meta-item">
            <div class="course-meta-label">课程描述</div>
            <div class="course-meta-value">{{ course.description || '暂无描述' }}</div>
          </div>
        </div>
      </div>
    </template>
    <div v-else class="empty"><span class="empty-icon">📭</span><p>课程不存在</p></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { courseApi } from '@/api/course'
import type { Course } from '@/types'

const route = useRoute()
const course = ref<Course | null>(null)
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await courseApi.get(Number(route.params.courseId))
    course.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.course-meta-item { margin-bottom: 12px; }
.course-meta-label { font-size: 12px; font-weight: 600; color: var(--c-text-3); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.course-meta-value { font-size: 14px; color: var(--c-text); line-height: 1.6; }
</style>
