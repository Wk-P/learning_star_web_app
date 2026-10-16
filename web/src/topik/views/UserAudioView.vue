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
    <div v-if="loading" class="sk-grid" aria-label="加载中">
      <div v-for="i in 6" :key="i" class="sk sk-card" />
    </div>
    <EmptyState v-else-if="error" icon="shield" title="加载失败" :desc="error" />
    <EmptyState
      v-else-if="subCategories.length === 0 && currentAudios.length === 0"
      icon="audio"
      title="这里还没有可访问的音频"
      desc="如果你刚注册，可能需要管理员为你开通学习权限，开通后刷新页面即可看到。"
    />

    <!-- category cards -->
    <Transition name="fade-up" mode="out-in">
      <div v-if="subCategories.length > 0" class="cards-grid" :key="'cards-' + currentPath.join('/')">
        <button
          v-for="cat in subCategories"
          :key="cat"
          class="category-card"
          @click="currentPath = [...currentPath, cat]"
        >
          <span class="card-icon">🎵</span>
          <span class="card-name">{{ cat }}</span>
        </button>
      </div>
    </Transition>

    <!-- audio list -->
    <Transition name="fade-up" mode="out-in">
      <ul v-if="currentAudios.length > 0" class="item-list" :key="'aud-' + currentPath.join('/')">
        <li v-for="audio in currentAudios" :key="audio.url" class="item">
          <a class="item-btn" :href="audio.url" target="_blank" @click="addHistory({ type: 'audio', title: audio.title, url: audio.url, path: audio.path })">
            <span class="item-icon"><AppIcon name="audio" :size="16" /></span>
            <span class="item-title">{{ audio.title }}</span>
            <span class="item-ext">mp3</span>
          </a>
        </li>
      </ul>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import EmptyState from '@/core/components/EmptyState.vue'
import AppIcon from '@/core/components/AppIcon.vue'
import { ref, computed, onMounted } from 'vue'
import { api } from '@/topik/api'
import { addHistory } from '@/topik/composables/useHistory'

interface Audio {
  id: number
  url: string
  title: string
  path: string[]
}

const audios = ref<Audio[]>([])
const currentPath = ref<string[]>([])
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getAudioList()
    audios.value = data.flatMap((folder) =>
      folder.audios.map((a) => ({
        id: a.id,
        title: a.title,
        url: a.url,
        path: [...folder.path, a.title],
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
  const matched = audios.value.filter((a) =>
    a.path.length > depth + 1 &&
    currentPath.value.every((seg, i) => a.path[i] === seg)
  )
  return [...new Set(matched.map((a) => a.path[depth]).filter((s): s is string => s !== undefined))]
})

const currentAudios = computed(() =>
  audios.value.filter((a) => {
    const parent = a.path.slice(0, -1)
    return (
      parent.length === currentPath.value.length &&
      currentPath.value.every((seg, i) => parent[i] === seg)
    )
  })
)
</script>

<style scoped>
.content-view {
  padding: 1.25rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 1.1rem 1.1rem 0.9rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  cursor: pointer;
  text-align: left;
  transition: background var(--t), border-color var(--t), transform var(--t), box-shadow var(--t);
}

.category-card:hover {
  background: var(--surface-2);
  border-color: var(--border-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--primary-glow);
}

.card-icon { font-size: 1.5rem; line-height: 1; }
.card-name { font-size: 0.9rem; font-weight: 600; color: var(--text); line-height: 1.3; word-break: break-all; }
.card-count { font-size: 0.75rem; color: var(--text-muted); }

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
  text-decoration: none;
  color: var(--text);
  font-size: 0.9rem;
  transition: background var(--t), border-color var(--t), transform var(--t);
}

.item-btn:hover {
  background: var(--surface-2);
  border-color: var(--border-strong);
  transform: translateX(2px);
}

.item-icon {
  color: var(--secondary);
  font-size: 0.85rem;
  flex-shrink: 0;
  opacity: 0.8;
}

.item-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-ext {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-subtle);
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.hint { font-size: 0.875rem; color: var(--text-muted); padding: 0.5rem 0; }
.hint--error { color: #f87171; }

.sk-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem; margin-top: 1rem; }
.sk-card { height: 96px; border-radius: var(--r-lg); }

.crumb-bar-enter-active, .crumb-bar-leave-active {
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}
.crumb-bar-enter-from, .crumb-bar-leave-to { opacity: 0; transform: translateY(-6px); }

.crumb-enter-active { transition: opacity 0.18s var(--ease), transform 0.18s var(--ease); }
.crumb-leave-active { transition: opacity 0.14s var(--ease), transform 0.14s var(--ease); }
.crumb-enter-from   { opacity: 0; transform: translateX(10px); }
.crumb-leave-to     { opacity: 0; transform: translateX(-6px); }

.fade-up-enter-active, .fade-up-leave-active {
  transition: opacity 0.18s var(--ease), transform 0.18s var(--ease);
}
.fade-up-enter-from { opacity: 0; transform: translateY(8px); }
.fade-up-leave-to   { opacity: 0; transform: translateY(-5px); }

@media (max-width: 480px) {
  .cards-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
  .item-btn { padding: 0.65rem 0.85rem; font-size: 0.85rem; }
}
</style>
