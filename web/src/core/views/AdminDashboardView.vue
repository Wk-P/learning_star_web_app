<template>
  <div class="dashboard">
    <h2 class="page-title">概览</h2>

    <div class="stat-grid">
      <div class="stat-card">
        <AppIcon name="user" :size="22" class="stat-icon" />
        <div>
          <p class="stat-label">用户</p>
          <p class="stat-value">{{ userCount ?? '–' }}</p>
        </div>
      </div>
      <div class="stat-card">
        <AppIcon name="globe" :size="22" class="stat-icon" />
        <div>
          <p class="stat-label">语言</p>
          <p class="stat-value">{{ languages.languages.length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <AppIcon name="book" :size="22" class="stat-icon" />
        <div>
          <p class="stat-label">课程科目 / 视频链接</p>
          <p class="stat-value">{{ subjectCount ?? '–' }} <span class="stat-minor">/ {{ courseVideoCount ?? '–' }}</span></p>
        </div>
      </div>
    </div>

    <h3 class="sub-title">语言学习资源</h3>
    <div v-if="!languages.languages.length" class="hint">还没有语言，去「分类与语言」添加。</div>
    <table v-else class="lang-table">
      <thead>
        <tr><th>语言</th><th v-for="k in MEDIA_KINDS" :key="k.key">{{ k.label }}</th></tr>
      </thead>
      <tbody>
        <tr v-for="lang in languages.languages" :key="lang.slug">
          <td>
            <RouterLink :to="{ name: 'admin-language-resources', query: { lang: lang.slug } }">{{ lang.name }}</RouterLink>
            <span class="slug">{{ lang.slug }}</span>
            <span v-if="!lang.is_active" class="off">未启用</span>
          </td>
          <td v-for="k in MEDIA_KINDS" :key="k.key">{{ counts[lang.slug]?.[k.key] ?? '…' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppIcon from '@/core/components/AppIcon.vue'
import { accountsApi } from '@/core/api/accounts'
import { languageApi, MEDIA_KINDS, type MediaKind } from '@/language/api'
import { useLanguageStore } from '@/language/stores/languages'
import http from '@/course/api/http'

const languages = useLanguageStore()
const userCount = ref<number | null>(null)
const subjectCount = ref<number | null>(null)
const courseVideoCount = ref<number | null>(null)
const counts = reactive<Record<string, Partial<Record<MediaKind, number>>>>({})

onMounted(async () => {
  accountsApi.listUsers().then((u) => { userCount.value = u.length }).catch(() => {})
  http.get<{ video_count: number }[]>('/admin/subjects/').then(({ data }) => {
    subjectCount.value = data.length
    courseVideoCount.value = data.reduce((s, x) => s + (x.video_count ?? 0), 0)
  }).catch(() => {})

  await languages.reload()
  for (const lang of languages.languages) {
    counts[lang.slug] = {}
    for (const k of MEDIA_KINDS) {
      languageApi.media(lang.slug, k.key)
        .then((folders) => { counts[lang.slug]![k.key] = folders.reduce((s, f) => s + f.items.length, 0) })
        .catch(() => {})
    }
  }
})
</script>

<style scoped>
.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.sub-title {
  font-size: 1rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 2rem 0 0.75rem;
}

.hint { font-size: 0.875rem; color: #8892a4; }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  transition: background 0.18s ease, border-color 0.18s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(90, 216, 207, 0.25);
}

.stat-icon { color: #5ad8cf; opacity: 0.85; flex-shrink: 0; }

.stat-label {
  font-size: 0.78rem;
  color: #8892a4;
  margin-bottom: 0.2rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1;
}
.stat-minor { font-size: 1.1rem; font-weight: 500; color: #8892a4; }

.lang-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.75rem;
  overflow: hidden;
}
.lang-table th, .lang-table td { padding: 0.65rem 1rem; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
.lang-table th { font-weight: 600; color: #8892a4; background: rgba(255, 255, 255, 0.03); }
.lang-table a { color: #5ad8cf; font-weight: 600; text-decoration: none; }
.slug { margin-left: 0.5rem; font-size: 0.75rem; color: #8892a4; }
.off { margin-left: 0.5rem; font-size: 0.72rem; color: #fb923c; }
</style>
