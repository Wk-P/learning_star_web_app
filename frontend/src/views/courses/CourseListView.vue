<template>
  <div>
    <h1 class="page-title">课程目录</h1>

    <div v-if="loading" class="grid grid-auto">
      <div v-for="i in 6" :key="i" class="card" style="height:140px">
        <div class="card-body"><div class="skeleton skeleton-text" /><div class="skeleton skeleton-text" /></div>
      </div>
    </div>

    <div v-else-if="subjects.length === 0" class="empty">
      <span class="empty-icon">📚</span>
      <p>暂无科目，管理员尚未配置课程分类</p>
      <router-link v-if="auth.isAdmin" to="/admin/subjects" class="btn btn-primary mt-12" style="text-decoration:none">
        前往创建科目
      </router-link>
    </div>

    <div v-else class="grid grid-auto">
      <div
        v-for="subject in subjects"
        :key="subject.id"
        class="subject-card card card-hover"
        @click="router.push(`/courses/subject/${subject.id}`)"
      >
        <!-- 顶部色条 -->
        <div class="subject-card-bar" :style="{ background: subject.color }" />
        <div class="card-body">
          <div class="subject-icon">{{ subject.icon }}</div>
          <div style="font-size:15px;font-weight:700;margin-bottom:6px">{{ subject.name }}</div>
          <p style="font-size:13px;color:var(--c-text-2);margin-bottom:12px;line-height:1.5">
            {{ subject.description || '点击查看课程' }}
          </p>
          <div style="font-size:12px;color:var(--c-text-3)">
            {{ subject.courseCount }} 门课程
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { subjectApi } from '@/api/course'
import { useAuthStore } from '@/stores/auth'
import type { Subject } from '@/types'

const auth = useAuthStore()

const router = useRouter()
const loading = ref(false)
const subjects = ref<Subject[]>([])

onMounted(async () => {
  loading.value = true
  try {
    subjects.value = (await subjectApi.list()).data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.subject-card {
  overflow: hidden;
  padding: 0;
}
.subject-card-bar {
  height: 6px;
  border-radius: var(--r) var(--r) 0 0;
}
.subject-icon {
  font-size: 32px;
  margin-bottom: 10px;
}
</style>
