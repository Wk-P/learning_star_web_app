<template>
  <div style="display:flex;flex-direction:column;gap:28px">

    <!-- 用户信息卡 -->
    <div class="home-profile card">
      <div class="home-profile-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</div>
      <div class="home-profile-info">
        <div class="home-profile-name">{{ auth.user?.displayName || auth.user?.username }}</div>
        <div class="home-profile-meta">
          <span class="font-mono text-sm text-muted">#{{ auth.user?.userId }}</span>
          <span class="badge badge-info">学生</span>
        </div>
      </div>
      <router-link to="/user/profile" class="btn btn-secondary btn-sm home-profile-edit">编辑信息</router-link>
    </div>

    <!-- 科目列表 -->
    <section>
      <h2 class="section-title">全部科目</h2>
      <div v-if="loading" class="skeleton" style="height:120px" />
      <div v-else-if="subjects.length === 0" class="empty">
        <span class="empty-icon">📭</span><p>暂无科目</p>
      </div>
      <div v-else class="grid grid-auto">
        <router-link
          v-for="s in subjects" :key="s.id"
          :to="`/subjects/${s.id}`"
          class="subject-card card card-hover"
          :style="{ '--subject-color': s.color }"
        >
          <div class="subject-icon">{{ s.icon }}</div>
          <div class="subject-name">{{ s.name }}</div>
          <div class="subject-desc text-secondary text-sm">{{ s.description || '暂无描述' }}</div>
        </router-link>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { subjectApi } from '@/api/course'
import type { Subject } from '@/types'

const auth = useAuthStore()
const subjects = ref<Subject[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await subjectApi.list()
    subjects.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-profile {
  display: flex; align-items: center; gap: 16px; padding: 20px 24px;
}
.home-profile-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--c-primary); color: #fff;
  font-size: 18px; font-weight: 700; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.home-profile-info { flex: 1; min-width: 0; }
.home-profile-name { font-size: 17px; font-weight: 700; color: var(--c-text); margin-bottom: 6px; }
.home-profile-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.home-profile-edit { flex-shrink: 0; }

.subject-card {
  display: flex; flex-direction: column; gap: 8px; padding: 20px;
  border-top: 3px solid var(--subject-color, var(--c-primary));
  text-decoration: none; color: inherit;
}
.subject-icon { font-size: 28px; }
.subject-name { font-size: 16px; font-weight: 700; color: var(--c-text); }
.subject-desc { line-height: 1.4; }
.subject-count { color: var(--subject-color, var(--c-primary)); font-weight: 600; margin-top: 4px; }
</style>
