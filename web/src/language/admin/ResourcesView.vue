<template>
  <div class="admin-page">
    <div class="toolbar">
      <h2 class="page-title">学习资源</h2>
      <el-select v-model="slug" placeholder="选择语言" style="width: 180px" @change="syncQuery">
        <el-option v-for="l in store.languages" :key="l.slug" :label="`${l.name}（${l.slug}）`" :value="l.slug" />
      </el-select>
      <el-radio-group v-model="kind" @change="syncQuery">
        <el-radio-button v-for="k in MEDIA_KINDS" :key="k.key" :value="k.key">{{ k.label }}</el-radio-button>
      </el-radio-group>
    </div>

    <p v-if="slug" class="dir-hint">
      服务器目录：<code>media/languages/{{ slug }}/{{ KIND_DIR[kind] }}/</code>
      —— 登录用户都能看到这里的全部内容。{{ KIND_HINT[kind] }}
    </p>

    <div v-if="!store.languages.length" class="empty-hint">还没有语言，请先在「分类与语言」中添加</div>
    <div v-else-if="loading" class="loading-hint">加载中…</div>
    <template v-else>
      <div v-for="folder in folders" :key="folder.id" class="folder-block">
        <div class="folder-header">
          <span class="folder-sep">▸</span>
          <span class="folder-path">{{ folder.path.join(' / ') || '根目录' }}</span>
          <span class="folder-count">{{ folder.items.length }} 个</span>
        </div>
        <el-table :data="folder.items" class="admin-table">
          <el-table-column prop="title" label="标题" min-width="160" />
          <el-table-column prop="ext" label="类型" width="80" />
          <el-table-column prop="url" label="URL" show-overflow-tooltip />
        </el-table>
      </div>
      <div v-if="!folders.length" class="empty-hint">暂无{{ MEDIA_KINDS.find((k) => k.key === kind)?.label }}</div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { languageApi, MEDIA_KINDS, type MediaFolder, type MediaKind } from '@/language/api'
import { useLanguageStore } from '@/language/stores/languages'

const KIND_DIR: Record<MediaKind, string> = { video: 'videos', audio: 'audios', file: 'files' }
const KIND_HINT: Record<MediaKind, string> = {
  video: '每个视频一个文件夹（文件夹名即标题），内含 m3u8 与 ts 切片。',
  audio: 'mp3 文件，文件名即标题。',
  file: 'pdf、Word、Excel、PPT、hwp 等文件，文件名即标题。',
}

const route = useRoute()
const router = useRouter()
const store = useLanguageStore()

const slug = ref(typeof route.query.lang === 'string' ? route.query.lang : '')
const kind = ref<MediaKind>(MEDIA_KINDS.some((k) => k.key === route.query.kind) ? (route.query.kind as MediaKind) : 'video')
const folders = ref<MediaFolder[]>([])
const loading = ref(false)

function syncQuery() {
  router.replace({ query: { lang: slug.value, kind: kind.value } })
}

async function load() {
  if (!slug.value) return
  loading.value = true
  try { folders.value = await languageApi.media(slug.value, kind.value) }
  catch { folders.value = [] }
  finally { loading.value = false }
}

watch([slug, kind], load)

onMounted(async () => {
  await store.reload()
  if (!store.bySlug(slug.value)) slug.value = store.languages[0]?.slug ?? ''
  else load()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-right: auto;
}

.dir-hint {
  font-size: 0.8rem;
  color: #8892a4;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}
.dir-hint code { color: #5ad8cf; }

.loading-hint,
.empty-hint {
  font-size: 0.875rem;
  color: #8892a4;
  padding: 2rem 0;
  text-align: center;
}

.folder-block { margin-bottom: 2rem; }

.folder-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
  padding: 0 0.25rem;
}

.folder-sep { color: #5ad8cf; font-size: 0.75rem; }
.folder-path { font-size: 0.875rem; font-weight: 600; color: #e2e8f0; }
.folder-count { font-size: 0.75rem; color: #8892a4; margin-left: auto; }

.admin-table {
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
</style>
