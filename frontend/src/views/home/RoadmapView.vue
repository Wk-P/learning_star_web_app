<template>
  <div class="rm-wrap">
    <div v-if="loading" class="rm-state">
      <div class="skeleton" style="height:100%;border-radius:0" />
    </div>

    <div v-else-if="error" class="rm-state rm-error">
      <span style="font-size:40px">📭</span>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="load">重新加载</button>
    </div>

    <iframe
      v-else
      ref="iframeEl"
      class="rm-frame"
      sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox"
      :srcdoc="content"
      title="学习路线图"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { roadmapApi } from '@/api/course'

const content = ref('')
const loading = ref(false)
const error = ref('')
const iframeEl = ref<HTMLIFrameElement | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await roadmapApi.get()
    content.value = data.content
  } catch {
    error.value = '路线图暂未生成，请联系管理员上传。'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.rm-wrap {
  width: 100%;
  height: calc(100vh - 58px);
  display: flex;
  flex-direction: column;
}

.rm-frame {
  flex: 1;
  width: 100%;
  border: none;
  display: block;
}

.rm-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--c-text-2);
  font-size: 15px;
}

.rm-error { color: var(--c-text-3); }
</style>
