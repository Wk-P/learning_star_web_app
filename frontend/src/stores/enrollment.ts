import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { courseApi } from '@/api/course'
import type { EnrollmentRecord, CourseStatus } from '@/types'

export const useEnrollmentStore = defineStore('enrollment', () => {
  // key: courseId
  const enrollments = ref<Map<number, EnrollmentRecord>>(new Map())
  const loaded = ref(false)
  const loading = ref(false)

  const enrolledCourseIds = computed(() => new Set(enrollments.value.keys()))

  function isEnrolled(courseId: number): boolean {
    return enrollments.value.has(courseId)
  }

  function getCourseStatus(courseId: number): CourseStatus | null {
    return enrollments.value.get(courseId)?.courseStatus ?? null
  }

  // HomeLayout 挂载时调用一次，后台静默加载
  async function fetchEnrollments() {
    if (loading.value) return
    loading.value = true
    try {
      const { data } = await courseApi.myEnrollments()
      const map = new Map<number, EnrollmentRecord>()
      for (const r of data) map.set(r.courseId, r)
      enrollments.value = map
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  // 用户操作（加入课程）后局部更新，不重新拉取
  function addEnrollment(record: EnrollmentRecord) {
    enrollments.value.set(record.courseId, record)
  }

  function removeEnrollment(courseId: number) {
    enrollments.value.delete(courseId)
  }

  function reset() {
    enrollments.value = new Map()
    loaded.value = false
    loading.value = false
  }

  return {
    enrollments,
    loaded,
    loading,
    enrolledCourseIds,
    isEnrolled,
    getCourseStatus,
    fetchEnrollments,
    addEnrollment,
    removeEnrollment,
    reset,
  }
})
