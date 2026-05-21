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

    <!-- file list -->
    <Transition name="fade-up" mode="out-in">
      <ul v-if="currentFiles.length > 0" class="item-list" :key="'file-' + currentPath.join('/')">
        <li v-for="file in currentFiles" :key="file.url" class="item">
          <a class="item-btn" :href="file.url" target="_blank" download>
            <span class="item-icon">↓</span>
            <span class="item-title">{{ file.title }}</span>
            <span class="item-ext">pdf</span>
          </a>
        </li>
      </ul>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

interface PdfFile {
  id: number
  url: string
  title: string
  path: string[]
}

const files = ref<PdfFile[]>([])
const currentPath = ref<string[]>([])
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getPdfList()
    files.value = data.flatMap((folder) =>
      folder.pdfs.map((p) => ({
        id: p.id,
        title: p.title,
        url: p.url,
        path: [...folder.path, p.title],
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
  const matched = files.value.filter((f) =>
    f.path.length > depth + 1 &&
    currentPath.value.every((seg, i) => f.path[i] === seg)
  )
  return [...new Set(matched.map((f) => f.path[depth]))]
})

const currentFiles = computed(() =>
  files.value.filter((f) => {
    const parent = f.path.slice(0, -1)
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
  color: var(--accent);
  font-size: 0.95rem;
  flex-shrink: 0;
  opacity: 0.85;
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
</style>
