<template>
  <div>
    <!-- 科目标题 -->
    <div v-if="subject" class="subject-header" :style="{ borderLeftColor: subject.color }">
      <span class="subject-icon">{{ subject.icon }}</span>
      <div>
        <h1 style="font-size:22px;font-weight:700;margin-bottom:4px">{{ subject.name }}</h1>
        <p style="color:var(--c-text-2);font-size:14px">{{ subject.description || '暂无描述' }}</p>
      </div>
    </div>

    <!-- 视频列表 -->
    <section style="margin-top:28px">
      <h2 class="section-title">B 站视频</h2>
      <div v-if="loading" class="skeleton" style="height:120px" />
      <div v-else-if="videos.length === 0" class="empty">
        <span class="empty-icon">📹</span><p>暂无视频</p>
      </div>
      <div v-else class="video-list">
        <a
          v-for="(v, i) in videos" :key="v.index"
          :href="v.url" target="_blank" rel="noopener"
          class="video-card card card-hover"
        >
          <div class="video-num text-muted">{{ i + 1 }}</div>
          <div class="video-info">
            <div class="video-title">{{ v.title }}</div>
            <div class="video-url text-sm text-secondary">{{ v.url }}</div>
          </div>
          <span class="video-badge">▶ B站</span>
        </a>
      </div>
    </section>

    <!-- 课程列表 -->
    <section v-if="courses.length > 0" style="margin-top:28px">
      <h2 class="section-title">相关课程</h2>
      <div class="grid grid-auto-lg">
        <div
          v-for="course in courses" :key="course.id"
          class="card card-hover"
          @click="router.push(`/courses/${course.id}`)"
        >
          <div class="card-body">
            <div style="font-size:15px;font-weight:600;margin-bottom:8px">{{ course.name }}</div>
            <p style="font-size:13px;color:var(--c-text-2);line-height:1.6">
              {{ course.description || '暂无描述' }}
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { subjectApi } from '@/api/course'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import type { Subject, Course, BilibiliVideo } from '@/types'

const route = useRoute()
const router = useRouter()
const { setSegments } = useBreadcrumb()
const subjectId = Number(route.params.subjectId)

const loading = ref(false)
const subject = ref<Subject | null>(null)
const courses = ref<Course[]>([])
const videos = ref<BilibiliVideo[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [subjectsRes, coursesRes, videosRes] = await Promise.all([
      subjectApi.list(),
      subjectApi.courses(subjectId),
      subjectApi.videos(subjectId),
    ])
    subject.value = subjectsRes.data.find(s => s.id === subjectId) ?? null
    courses.value = coursesRes.data
    videos.value = videosRes.data
    if (subject.value) {
      setSegments([
        { label: '课程目录', path: '/courses' },
        { label: subject.value.name },
      ])
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.subject-header {
  display: flex; align-items: center; gap: 16px;
  padding: 20px 24px; background: var(--c-surface);
  border-radius: var(--r); border: 1px solid var(--c-border); border-left-width: 5px;
}
.subject-icon { font-size: 36px; flex-shrink: 0; }

.video-list { display: flex; flex-direction: column; gap: 10px; }
.video-card {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 18px; text-decoration: none; color: inherit;
}
.video-num {
  min-width: 28px; font-size: 15px; font-weight: 600; flex-shrink: 0;
}
.video-info { flex: 1; min-width: 0; }
.video-title { font-size: 14px; font-weight: 600; color: var(--c-text); margin-bottom: 4px; }
.video-url { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--c-primary); }
.video-badge {
  flex-shrink: 0; padding: 3px 10px; border-radius: var(--r-full);
  background: #fb7299; color: #fff; font-size: 12px; font-weight: 600;
}
</style>
