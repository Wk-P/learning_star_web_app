<template>
  <div>
    <h1 class="page-title">我的学习</h1>

    <div v-if="loading" class="grid grid-auto">
      <div v-for="i in 4" :key="i" class="card" style="height:100px">
        <div class="card-body">
          <div class="skeleton skeleton-text" />
          <div class="skeleton skeleton-text" />
        </div>
      </div>
    </div>

    <template v-else>
      <section v-for="group in courseGroups" :key="group.label" style="margin-bottom:32px">
        <h2 class="section-title">{{ group.label }}</h2>
        <div v-if="group.courses.length === 0" class="empty">
          <span class="empty-icon">📭</span>
          <p>{{ group.label }}为空...</p>
        </div>
        <div v-else class="grid grid-auto">
          <div
            v-for="course in group.courses" :key="course.courseId"
            class="card card-hover"
            @click="router.push(`/courses/${course.courseId}`)"
          >
            <div class="card-body">
              <div style="font-size:15px;font-weight:600;margin-bottom:10px">{{ course.courseName }}</div>
              <span :class="['badge', statusBadge(course.courseStatus)]">
                <span class="badge-dot" />{{ statusLabel(course.courseStatus) }}
              </span>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEnrollmentStore } from '@/stores/enrollment'
import type { CourseStatus } from '@/types'

const router = useRouter()
const enrollment = useEnrollmentStore()
const loading = ref(false)

onMounted(async () => {
  if (!enrollment.loaded) { loading.value = true; await enrollment.fetchEnrollments().finally(() => loading.value = false) }
})

const all = computed(() => [...enrollment.enrollments.values()])
const courseGroups = computed(() => [
  { label: '进行中的课程', courses: all.value.filter(r => r.courseStatus === 'in_progress') },
  { label: '未开始的课程', courses: all.value.filter(r => r.courseStatus === 'not_started') },
  { label: '已完成的课程', courses: all.value.filter(r => r.courseStatus === 'ended') },
])

function statusLabel(s: CourseStatus) { return { not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s] }
function statusBadge(s: CourseStatus) { return { not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s] }
</script>
