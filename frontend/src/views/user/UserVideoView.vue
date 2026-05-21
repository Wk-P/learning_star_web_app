<template>
  <div class="content-view">

    <!-- breadcrumb -->
    <Transition name="crumb-bar">
      <nav v-if="currentPath.length > 0" class="breadcrumb">
        <button class="crumb-btn crumb-root" @click="currentPath = []">全部</button>
        <TransitionGroup name="crumb" tag="span" class="crumb-trail">
          <span class="crumb-item" v-for="(seg, i) in currentPath" :key="seg">
            <span class="crumb-sep">›</span>
            <button class="crumb-btn" @click="currentPath = currentPath.slice(0, i + 1)">{{ seg }}</button>
          </span>
        </TransitionGroup>
      </nav>
    </Transition>

    <!-- status -->
    <p v-if="loading" class="hint">加载中…</p>
    <p v-else-if="error" class="hint hint--error">{{ error }}</p>

    <!-- categories -->
    <Transition name="fade-up" mode="out-in">
      <ul v-if="subCategories.length > 0" class="chips" :key="'cat-' + currentPath.join('/')">
        <li v-for="cat in subCategories" :key="cat">
          <button class="chip" @click="currentPath = [...currentPath, cat]">{{ cat }}</button>
        </li>
      </ul>
    </Transition>

    <!-- video list -->
    <Transition name="fade-up" mode="out-in">
      <ul v-if="currentVideos.length > 0" class="item-list" :key="'vid-' + currentPath.join('/')">
        <li v-for="video in currentVideos" :key="video.url" class="item">
          <button class="item-btn" @click="playVideo(video)">
            <span class="item-play">▶</span>
            <span class="item-title">{{ video.title }}</span>
          </button>
        </li>
      </ul>
    </Transition>

    <!-- player -->
    <Transition name="player-in">
      <div v-if="activeVideo" class="player-wrap">
        <div class="player-header">
          <span class="player-title">{{ activeVideo.title }}</span>
          <button class="player-close" @click="activeVideo = null" aria-label="关闭">✕</button>
        </div>
        <VideoPlayer :src="activeVideo.url" />
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VideoPlayer from '@/components/VIdeoComponent.vue'
import { api } from '@/api'

interface Video {
  id: number
  url: string
  title: string
  path: string[]
}

const videos = ref<Video[]>([])
const currentPath = ref<string[]>([])
const activeVideo = ref<Video | null>(null)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getVideoList()
    videos.value = data.flatMap((folder) =>
      folder.videos.map((v) => ({
        id: v.id,
        title: v.title,
        url: v.url,
        path: [...folder.path, v.title],
      }))
    )
  } catch {
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})

const subCategories = computed(() => {
  const depth = currentPath.value.length
  const matched = videos.value.filter((v) =>
    v.path.length > depth + 1 &&
    currentPath.value.every((seg, i) => v.path[i] === seg)
  )
  return [...new Set(matched.map((v) => v.path[depth]))]
})

const currentVideos = computed(() =>
  videos.value.filter((v) => {
    const parent = v.path.slice(0, -1)
    return (
      parent.length === currentPath.value.length &&
      currentPath.value.every((seg, i) => parent[i] === seg)
    )
  })
)

function playVideo(video: Video) {
  activeVideo.value = video
}
</script>

<style scoped>
/* ── shell ──────────────────────────── */
.content-view {
  padding: 1.25rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* ── breadcrumb ─────────────────────── */
.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.1rem;
  padding: 0.5rem 0.75rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-size: 0.8rem;
}

.crumb-trail {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.1rem;
}

.crumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.1rem;
}

.crumb-sep {
  color: var(--text-subtle);
  font-size: 0.75rem;
  padding: 0 0.1rem;
}

.crumb-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: var(--r-sm);
  transition: color var(--t), background var(--t);
}

.crumb-btn:hover {
  color: var(--text);
  background: var(--surface-2);
}

.crumb-root {
  color: var(--primary);
  font-weight: 600;
}

.crumb-root:hover {
  background: var(--primary-dim);
}

/* ── chips (categories) ─────────────── */
.chips {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  background: var(--primary-dim);
  border: 1px solid rgba(45, 212, 191, 0.2);
  border-radius: 999px;
  color: var(--primary);
  font-size: 0.85rem;
  font-weight: 500;
  padding: 0.375rem 1rem;
  cursor: pointer;
  transition: background var(--t), border-color var(--t), transform var(--t);
}

.chip:hover {
  background: rgba(45, 212, 191, 0.18);
  border-color: var(--border-primary);
  transform: translateY(-1px);
}

/* ── item list ──────────────────────── */
.item-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.item-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  cursor: pointer;
  text-align: left;
  color: var(--text);
  font-size: 0.9rem;
  transition: background var(--t), border-color var(--t), transform var(--t);
}

.item-btn:hover {
  background: var(--surface-2);
  border-color: var(--border-strong);
  transform: translateX(2px);
}

.item-play {
  color: var(--primary);
  font-size: 0.75rem;
  flex-shrink: 0;
  opacity: 0.75;
}

.item-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── player ─────────────────────────── */
.player-wrap {
  border: 1px solid var(--border-primary);
  border-radius: var(--r-lg);
  overflow: hidden;
  background: var(--surface-1);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: 0 0 40px var(--primary-glow), 0 8px 32px rgba(0,0,0,0.5);
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border);
}

.player-title {
  font-size: 0.875rem;
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  margin-right: 1rem;
}

.player-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-subtle);
  font-size: 1rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--r-sm);
  transition: color var(--t), background var(--t);
  flex-shrink: 0;
}

.player-close:hover {
  color: var(--text);
  background: var(--surface-3);
}

/* ── hints ──────────────────────────── */
.hint {
  font-size: 0.875rem;
  color: var(--text-muted);
  padding: 0.5rem 0;
}

.hint--error { color: #f87171; }

/* ── transitions ─────────────────────── */
.crumb-bar-enter-active,
.crumb-bar-leave-active {
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}
.crumb-bar-enter-from,
.crumb-bar-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.crumb-enter-active { transition: opacity 0.18s var(--ease), transform 0.18s var(--ease); }
.crumb-leave-active { transition: opacity 0.14s var(--ease), transform 0.14s var(--ease); }
.crumb-enter-from   { opacity: 0; transform: translateX(10px); }
.crumb-leave-to     { opacity: 0; transform: translateX(-6px); }

.fade-up-enter-active,
.fade-up-leave-active {
  transition: opacity 0.18s var(--ease), transform 0.18s var(--ease);
}
.fade-up-enter-from { opacity: 0; transform: translateY(8px); }
.fade-up-leave-to   { opacity: 0; transform: translateY(-5px); }

.player-in-enter-active,
.player-in-leave-active {
  transition: opacity 0.28s var(--ease), transform 0.28s var(--ease);
}
.player-in-enter-from,
.player-in-leave-to {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}
</style>
