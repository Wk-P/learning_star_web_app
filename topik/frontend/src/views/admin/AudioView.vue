<template>
  <div class="admin-page">
    <h2 class="page-title">音频管理</h2>

    <div v-if="loading" class="loading-hint">加载中…</div>

    <template v-else>
      <div v-for="folder in folders" :key="folder.id" class="folder-block">
        <div class="folder-header">
          <span class="folder-sep">▸</span>
          <span class="folder-path">{{ folder.path.join(' / ') || '根目录' }}</span>
          <span class="folder-count">{{ folder.audios.length }} 个</span>
        </div>
        <el-table :data="folder.audios" class="admin-table">
          <el-table-column prop="id" label="ID" width="72" />
          <el-table-column prop="title" label="标题" min-width="160" />
          <el-table-column prop="url" label="URL" show-overflow-tooltip />
        </el-table>
      </div>
      <div v-if="!folders.length" class="empty-hint">暂无音频数据</div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'
import type { AudioItem } from '@/api'

const loading = ref(true)
const folders = ref<{ id: number; path: string[]; audios: AudioItem[] }[]>([])

onMounted(async () => {
  try { folders.value = await api.getAudioList() }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.loading-hint,
.empty-hint {
  font-size: 0.875rem;
  color: #8892a4;
  padding: 2rem 0;
  text-align: center;
}

.folder-block {
  margin-bottom: 2rem;
}

.folder-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
  padding: 0 0.25rem;
}

.folder-sep {
  color: #2dd4bf;
  font-size: 0.75rem;
}

.folder-path {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
}

.folder-count {
  font-size: 0.75rem;
  color: #8892a4;
  margin-left: auto;
}

.admin-table {
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
</style>
