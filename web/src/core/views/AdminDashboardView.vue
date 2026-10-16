<template>
  <div class="dashboard">
    <h2 class="page-title">概览</h2>

    <div class="stat-grid">
      <div class="stat-card">
        <span class="stat-icon">▶</span>
        <div>
          <p class="stat-label">视频总数</p>
          <p class="stat-value">{{ videoCount }}</p>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">♫</span>
        <div>
          <p class="stat-label">音频总数</p>
          <p class="stat-value">{{ audioCount }}</p>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon">↓</span>
        <div>
          <p class="stat-label">PDF 总数</p>
          <p class="stat-value">{{ pdfCount }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/topik/api'

const videoCount = ref(0)
const audioCount = ref(0)
const pdfCount = ref(0)

onMounted(async () => {
  const [videos, audios, pdfs] = await Promise.all([
    api.getVideoList(),
    api.getAudioList(),
    api.getPdfList(),
  ])
  videoCount.value = videos.reduce((s, f) => s + f.videos.length, 0)
  audioCount.value = audios.reduce((s, f) => s + f.audios.length, 0)
  pdfCount.value   = pdfs.reduce((s, f) => s + f.pdfs.length, 0)
})
</script>

<style scoped>
.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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

.stat-icon {
  font-size: 1.4rem;
  color: #5ad8cf;
  opacity: 0.8;
  flex-shrink: 0;
}

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
</style>
