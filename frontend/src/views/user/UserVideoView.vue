<template>
  <div class="user-video">
    <Transition name="nav-fade">
      <nav v-if="currentPath.length > 0">
        <button @click="currentPath = []">全部</button>
        <TransitionGroup name="crumb" tag="span" class="crumb-group">
          <span class="crumb-item" v-for="(segment, i) in currentPath" :key="segment">
            <span class="sep">/</span>
            <button @click="currentPath = currentPath.slice(0, i + 1)">{{ segment }}</button>
          </span>
        </TransitionGroup>
      </nav>
    </Transition>

    <Transition name="content" mode="out-in">
      <ul v-if="subCategories.length > 0" :key="'cat-' + currentPath.join('/')">
        <li v-for="category in subCategories" :key="category">
          <button @click="currentPath = [...currentPath, category]">{{ category }}</button>
        </li>
      </ul>
    </Transition>

    <Transition name="content" mode="out-in">
      <ul v-if="currentVideos.length > 0" :key="'vid-' + currentPath.join('/')">
        <li v-for="video in currentVideos" :key="video.url">
          <button @click="playVideo(video)">{{ video.title }}</button>
        </li>
      </ul>
    </Transition>

    <Transition name="player-fade">
      <div v-if="activeVideo" class="player-wrap">
        <div class="player-header">
          <span class="player-title">{{ activeVideo.title }}</span>
          <button class="player-close" @click="activeVideo = null">✕</button>
        </div>
        <VideoPlayer :src="activeVideo.url" />
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import VideoPlayer from '@/components/VIdeoComponent.vue'

interface Video {
  url: string
  title: string
  path: string[]
}

const videos = ref<Video[]>([
  { path: ['topik韩语', 'l1', 'l2'], title: 'topik直播1', url: 'https://www.google.com' },
  { path: ['小梁韩语', 'l1', 'l2', 'l3'], title: 'topik回放', url: 'https://www.google.com' },
  { path: ['一墨私塾', '三级班'], title: 'topik直播', url: 'https://www.google.com' },
  { path: ['一墨私塾', '四级班'], title: 'topik直播2', url: 'https://www.google.com' },
])

const currentPath = ref<string[]>([])
const activeVideo = ref<Video | null>(null)

const subCategories = computed(() => {
  const depth = currentPath.value.length
  const matched = videos.value.filter((video) =>
    video.path.length > depth + 1 &&
    currentPath.value.every((segment, i) => video.path[i] === segment)
  )
  return [...new Set(matched.map((video) => video.path[depth] as string))]
})

const currentVideos = computed(() => {
  return videos.value.filter((video) => {
    const parentPath = video.path.slice(0, -1)
    return (
      parentPath.length === currentPath.value.length &&
      currentPath.value.every((segment, i) => parentPath[i] === segment)
    )
  })
})

function playVideo(video: Video): void {
  activeVideo.value = video
}
</script>

<style scoped>
.user-video {
  padding: 1rem;
}

ul {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

li {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

li:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-1px);
}

nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
  color: var(--text-muted);
  font-size: 14px;
}

.crumb-group {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.crumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.sep {
  color: var(--text-muted);
}

nav button,
ul button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0.5rem 0.75rem;
  color: var(--text);
}

.player-wrap {
  margin-top: 1rem;
  border: 1px solid var(--glass-border);
  border-radius: 0.75rem;
  overflow: hidden;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--glass-border);
}

.player-title {
  font-size: 14px;
  color: var(--text);
}

.player-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 16px;
  line-height: 1;
  padding: 0.25rem;
}

.player-close:hover {
  color: var(--text);
}

/* 面包屑整体出现 */
.nav-fade-enter-active,
.nav-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.nav-fade-enter-from,
.nav-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 面包屑每个 item 滑入 */
.crumb-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.crumb-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.crumb-enter-from {
  opacity: 0;
  transform: translateX(12px);
}
.crumb-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

/* 内容列表切换 */
.content-enter-active,
.content-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.content-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.content-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 播放器出现 */
.player-fade-enter-active,
.player-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.player-fade-enter-from,
.player-fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
