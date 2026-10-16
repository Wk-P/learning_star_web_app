<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">学习路线图管理</h1>
        <p class="page-desc">上传新的 HTML 文件来替换当前展示给用户的学习路线图。</p>
      </div>
    </div>

    <!-- 当前文件状态 -->
    <div class="card status-card">
      <div class="status-label">当前路线图</div>
      <div v-if="metaLoading" class="skeleton" style="height:48px;border-radius:8px" />
      <div v-else-if="meta?.exists" class="status-info">
        <span class="status-dot status-dot--ok" />
        <div>
          <div class="status-title">template.html</div>
          <div class="status-sub">
            大小：{{ formatSize(meta.size!) }}
            &nbsp;·&nbsp;
            最后更新：{{ formatDate(meta.updatedAt!) }}
          </div>
        </div>
        <a href="/roadmap" target="_blank" class="btn btn-secondary btn-sm" style="margin-left:auto">预览</a>
      </div>
      <div v-else class="status-info">
        <span class="status-dot status-dot--empty" />
        <div>
          <div class="status-title">暂无路线图文件</div>
          <div class="status-sub">上传 HTML 文件后，用户即可在"学习路线图"页面查看。</div>
        </div>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="card upload-card">
      <div class="upload-label">上传新文件（替换当前）</div>

      <div
        class="drop-zone"
        :class="{ 'drop-zone--over': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".html"
          style="display:none"
          @change="onFileChange"
        />
        <span class="drop-icon">📄</span>
        <p class="drop-hint">
          <strong>点击选择</strong> 或拖拽 HTML 文件到此处
        </p>
        <p class="drop-sub">仅支持 .html 文件，最大 5MB</p>
      </div>

      <!-- 已选文件预览 -->
      <div v-if="selectedFile" class="selected-file">
        <span class="selected-name">{{ selectedFile.name }}</span>
        <span class="selected-size">{{ formatSize(selectedFile.size) }}</span>
        <button class="btn-remove" @click="selectedFile = null">✕</button>
      </div>

      <div class="upload-actions">
        <button
          class="btn btn-primary"
          :class="{ loading: uploading }"
          :disabled="!selectedFile || uploading"
          @click="handleUpload"
        >
          {{ uploading ? '上传中…' : '确认上传替换' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { roadmapApi, type RoadmapMeta } from '@/course/api/course'
import { useToast } from '@/course/composables/useToast'

const toast = useToast()

const meta = ref<RoadmapMeta | null>(null)
const metaLoading = ref(false)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

async function loadMeta() {
  metaLoading.value = true
  try {
    const { data } = await roadmapApi.adminMeta()
    meta.value = data
  } finally {
    metaLoading.value = false
  }
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) selectedFile.value = f
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const f = e.dataTransfer?.files[0]
  if (!f) return
  if (!f.name.toLowerCase().endsWith('.html')) {
    toast.error('只支持 .html 文件')
    return
  }
  selectedFile.value = f
}

async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const { data } = await roadmapApi.adminUpload(selectedFile.value)
    meta.value = data
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    toast.success('路线图已更新')
  } catch {
    // toast handled by http interceptor
  } finally {
    uploading.value = false
  }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function formatDate(ts: number) {
  return new Date(ts * 1000).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadMeta)
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}
.page-title { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: var(--c-text-2); margin: 0; }

.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  padding: 24px;
  margin-bottom: 16px;
}

.status-label, .upload-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-text-3);
  margin-bottom: 14px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot--ok { background: var(--c-success, #16a34a); }
.status-dot--empty { background: var(--c-text-3); }

.status-title { font-size: 15px; font-weight: 600; color: var(--c-text); }
.status-sub { font-size: 13px; color: var(--c-text-2); margin-top: 2px; }

/* 拖拽上传区 */
.drop-zone {
  border: 2px dashed var(--c-border);
  border-radius: var(--r);
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}
.drop-zone:hover, .drop-zone--over {
  border-color: var(--c-primary);
  background: var(--c-primary-light);
}
.drop-icon { font-size: 36px; }
.drop-hint { margin: 0; font-size: 14px; color: var(--c-text-2); }
.drop-hint strong { color: var(--c-primary); }
.drop-sub { margin: 0; font-size: 12px; color: var(--c-text-3); }

/* 已选文件 */
.selected-file {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: var(--r-sm);
  background: var(--c-info-light, #eff6ff);
  border: 1px solid var(--c-primary-light, #bfdbfe);
}
.selected-name { flex: 1; font-size: 14px; font-weight: 500; color: var(--c-text); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.selected-size { font-size: 12px; color: var(--c-text-3); flex-shrink: 0; }
.btn-remove {
  flex-shrink: 0;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: transparent;
  color: var(--c-text-3);
  font-size: 12px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.12s;
}
.btn-remove:hover { background: var(--c-border); color: var(--c-text); }

.upload-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
