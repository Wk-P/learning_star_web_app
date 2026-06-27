<template>
  <div>
    <div v-if="subject" class="subject-header" :style="{ borderLeftColor: subject.color }">
      <span class="subject-icon">{{ subject.icon }}</span>
      <div>
        <h1 style="font-size:22px;font-weight:700;margin-bottom:4px">{{ subject.name }}</h1>
        <p style="color:var(--c-text-2);font-size:14px">{{ subject.description || '暂无描述' }}</p>
      </div>
    </div>

    <div v-if="loading" class="skeleton" style="height:160px;margin-top:24px" />

    <div v-else-if="videos.length === 0" class="empty" style="margin-top:32px">
      <span class="empty-icon">📹</span><p>该科目暂无视频</p>
    </div>

    <div v-else class="video-list" style="margin-top:24px">
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
        <span class="bilibili-badge">▶ B站</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { subjectApi } from '@/api/course'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import type { Subject, BilibiliVideo } from '@/types'

const route = useRoute()
const { setSegments } = useBreadcrumb()
const subjectId = Number(route.params.subjectId)

const loading = ref(false)
const subject = ref<Subject | null>(null)
const videos = ref<BilibiliVideo[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [subjectsRes, videosRes] = await Promise.all([
      subjectApi.list(),
      subjectApi.videos(subjectId),
    ])
    subject.value = subjectsRes.data.find(s => s.id === subjectId) ?? null
    videos.value = videosRes.data
    if (subject.value) {
      setSegments([{ label: subject.value.name }])
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
.video-num { min-width: 28px; font-size: 15px; font-weight: 600; flex-shrink: 0; }
.video-info { flex: 1; min-width: 0; }
.video-title { font-size: 14px; font-weight: 600; color: var(--c-text); margin-bottom: 4px; }
.video-url { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--c-primary); }
.bilibili-badge {
  flex-shrink: 0; padding: 3px 10px; border-radius: var(--r-full);
  background: #fb7299; color: #fff; font-size: 12px; font-weight: 600;
}
</style>
