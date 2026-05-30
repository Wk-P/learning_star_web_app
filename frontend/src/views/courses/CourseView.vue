<template>
  <div>
    <div v-if="loading" style="display:flex;flex-direction:column;gap:16px">
      <div class="skeleton skeleton-text" style="height:32px;width:40%" />
      <div class="skeleton" style="height:120px" />
    </div>
    <template v-else-if="course">
      <!-- 课程头 -->
      <div class="flex-between" style="margin-bottom:20px;flex-wrap:wrap;gap:12px">
        <div>
          <div style="font-size:13px;color:var(--c-text-3);margin-bottom:6px">{{ course.subjectName }}</div>
          <h1 style="font-size:22px;font-weight:700;margin-bottom:10px">{{ course.name }}</h1>
          <div class="flex" style="gap:8px;flex-wrap:wrap">
            <span :class="['badge', statusBadge(course.status)]">{{ statusLabel(course.status) }}</span>
            <span v-if="isEnrolled" class="badge badge-primary">已申请</span>
            <span v-else class="badge badge-info">未申请</span>
          </div>
        </div>
        <div class="flex" style="gap:10px">
          <button v-if="!isEnrolled && course.status !== 'ended'" class="btn btn-primary" :class="{ loading: enrolling }" @click="handleEnroll">
            {{ enrolling ? '' : '申请加入' }}
          </button>
          <button v-if="isEnrolled && course.status === 'in_progress'" class="btn btn-success" @click="router.push('/user/homework')">随堂作业</button>
        </div>
      </div>

      <!-- 课程概览 -->
      <div class="card" style="margin-bottom:20px">
        <div class="card-body">
          <div class="course-meta">
            <div class="course-meta-item">
              <div class="course-meta-label">课程描述</div>
              <div class="course-meta-value">{{ course.description || '暂无描述' }}</div>
            </div>
            <div v-if="course.schedule" class="course-meta-item">
              <div class="course-meta-label">上课日程</div>
              <div class="course-meta-value">{{ course.schedule }}</div>
            </div>
            <div class="course-meta-item">
              <div class="course-meta-label">课程时长</div>
              <div class="course-meta-value">共 {{ course.durationWeeks }} 周（{{ fmtDate(course.startTime) }} — {{ fmtDate(course.endTime) }}）</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程时间表 -->
      <div class="card" style="margin-bottom:20px">
        <div class="card-header">课程时间表</div>
        <div v-if="classes.length === 0" class="empty"><span class="empty-icon">📅</span><p>课节列表为空...</p></div>
        <div v-else class="table-wrap">
          <table class="table">
            <thead><tr><th>课节</th><th>上课时间</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="cls in classes" :key="cls.id">
                <td>{{ cls.title }}</td>
                <td>{{ fmt(cls.classTime) }}</td>
                <td>
                  <button class="btn btn-link btn-sm" @click="router.push(`/courses/${courseId}/classes/${cls.id}`)">查看</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 作业时间表 -->
      <div class="card">
        <div class="card-header">作业时间表</div>
        <div v-if="visibleHomework.length === 0" class="empty"><span class="empty-icon">📝</span><p>作业列表为空...</p></div>
        <div v-else class="table-wrap">
          <table class="table">
            <thead><tr><th>作业名称</th><th>开始时间</th><th>截止时间</th><th>状态</th><th v-if="isEnrolled">操作</th></tr></thead>
            <tbody>
              <tr v-for="hw in visibleHomework" :key="hw.id">
                <td>{{ hw.name }}</td>
                <td>{{ fmt(hw.startTime) }}</td>
                <td>{{ fmt(hw.endTime) }}</td>
                <td><span :class="['badge', statusBadge(hw.status)]">{{ statusLabel(hw.status) }}</span></td>
                <td v-if="isEnrolled">
                  <button class="btn btn-link btn-sm" @click="router.push(`/user/homework/${hw.id}`)">查看</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { fmt, fmtDate } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useToast } from '@/composables/useToast'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { courseApi } from '@/api/course'
import { classApi } from '@/api/class'
import { homeworkApi } from '@/api/homework'
import type { Course, ClassSession, Homework, CourseStatus, HomeworkStatus } from '@/types'

const route = useRoute(); const router = useRouter()
const enrollment = useEnrollmentStore(); const toast = useToast()
const { setSegments } = useBreadcrumb()
const courseId = Number(route.params.courseId)
const loading = ref(false); const enrolling = ref(false)
const course = ref<Course | null>(null)
const classes = ref<ClassSession[]>([])
const homework = ref<Homework[]>([])

const isEnrolled = computed(() => enrollment.isEnrolled(courseId))
const visibleHomework = computed(() => isEnrolled.value ? homework.value.filter(h => h.status !== 'not_started') : homework.value.filter(h => h.status === 'in_progress'))

onMounted(async () => {
  loading.value = true
  try {
    const [c, cl, hw] = await Promise.all([courseApi.get(courseId), classApi.listByCourse(courseId), homeworkApi.listByCourse(courseId)])
    course.value = c.data; classes.value = cl.data; homework.value = hw.data
    setSegments([
      { label: '课程目录', path: '/courses' },
      { label: course.value.name },
    ])
  } finally { loading.value = false }
})

async function handleEnroll() {
  enrolling.value = true
  try {
    await courseApi.enroll(courseId)
    enrollment.addEnrollment({ courseId, courseName: course.value!.name, enrolledAt: new Date().toISOString(), courseStatus: course.value!.status })
    toast.success('申请成功')
  } finally { enrolling.value = false }
}

function statusLabel(s: CourseStatus | HomeworkStatus) { return { not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s] }
function statusBadge(s: CourseStatus | HomeworkStatus) { return { not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s] }
</script>

<style scoped>
.course-meta { display: flex; flex-direction: column; gap: 14px; }
.course-meta-item { display: flex; gap: 12px; }
.course-meta-label { width: 80px; flex-shrink: 0; font-size: 13px; font-weight: 500; color: var(--c-text-2); padding-top: 1px; }
.course-meta-value { font-size: 14px; color: var(--c-text); line-height: 1.6; }
</style>
