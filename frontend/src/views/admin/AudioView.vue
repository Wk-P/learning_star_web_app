<template>
  <div>
    <h2 style="margin-bottom: 24px">音频列表</h2>
    <div v-if="loading" v-loading="true" style="height: 200px" />
    <template v-else>
      <div v-for="folder in folders" :key="folder.id" style="margin-bottom: 32px">
        <div class="folder-path">{{ folder.path.join(' / ') || '根目录' }}</div>
        <el-table :data="folder.audios" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="url" label="URL" show-overflow-tooltip />
        </el-table>
      </div>
      <el-empty v-if="!folders.length" description="暂无音频" />
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
  try {
    folders.value = await api.getAudioList()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.folder-path {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
  padding-left: 4px;
  border-left: 3px solid #409eff;
}
</style>
