<template>
  <div class="hub">

    <!-- ── 左侧：科目栏 ─────────────────────────────────────── -->
    <aside class="hub-sidebar">
      <div class="hub-sidebar-title">科目</div>
      <div v-if="loadingSubjects" class="skeleton" style="height:160px;border-radius:8px" />
      <nav v-else class="hub-subject-list">
        <button
          v-for="s in subjects" :key="s.id"
          :class="['hub-subject-item', { active: activeId === s.id }]"
          :style="activeId === s.id ? { '--accent': s.color, borderLeftColor: s.color } : {}"
          @click="selectSubject(s)"
        >
          <span class="hub-subject-icon">{{ s.icon }}</span>
          <span class="hub-subject-name">{{ s.name }}</span>
          <span v-if="videoCountMap[s.id] !== undefined" class="hub-subject-count">
            {{ videoCountMap[s.id] }}
          </span>
        </button>
      </nav>
    </aside>

    <!-- ── 右侧：视频列表 ────────────────────────────────────── -->
    <main class="hub-content">
      <!-- 标题 -->
      <div v-if="active" class="hub-content-header" :style="{ borderLeftColor: active.color }">
        <span class="hub-content-icon">{{ active.icon }}</span>
        <div>
          <h1 class="hub-content-title">{{ active.name }}</h1>
          <p class="hub-content-desc">{{ active.description || '暂无描述' }}</p>
        </div>
      </div>

      <!-- 加载骨架 -->
      <div v-if="loadingVideos" class="skeleton" style="height:200px;border-radius:8px;margin-top:20px" />

      <!-- 空状态 -->
      <div v-else-if="!active" class="hub-empty">
        <span class="empty-icon">👈</span>
        <p>从左侧选择科目</p>
      </div>
      <div v-else-if="videos.length === 0" class="hub-empty">
        <span class="empty-icon">📹</span>
        <p>该科目暂无视频</p>
      </div>

      <!-- 视频列表 -->
      <ol v-else class="hub-video-list">
        <li v-for="(v, i) in videos" :key="v.index" class="hub-video-item">
          <span class="hub-video-num">{{ i + 1 }}</span>
          <div class="hub-video-info">
            <a :href="v.url" target="_blank" rel="noopener" class="hub-video-title">
              {{ v.title }}
            </a>
            <span class="hub-video-url">{{ v.url }}</span>
          </div>
          <div class="hub-video-actions">
            <a :href="v.url" target="_blank" rel="noopener" class="btn-bilibili">▶ B站</a>
            <button
              :class="['btn-copy', copyState[v.index]]"
              @click="copyUrl(v)"
            >
              {{ copyLabel(v.index) }}
            </button>
          </div>
        </li>
      </ol>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { subjectApi } from '@/api/course'
import type { Subject, BilibiliVideo } from '@/types'

const subjects = ref<Subject[]>([])
const active = ref<Subject | null>(null)
const activeId = ref<number | null>(null)
const videos = ref<BilibiliVideo[]>([])
const loadingSubjects = ref(false)
const loadingVideos = ref(false)
const videoCountMap = reactive<Record<number, number>>({})

// 'idle' | 'ok' | 'fail'
const copyState = reactive<Record<number, string>>({})

function copyLabel(index: number) {
  const s = copyState[index]
  if (s === 'ok') return '已复制'
  if (s === 'fail') return '复制失败'
  return '复制链接'
}

async function copyUrl(v: BilibiliVideo) {
  try {
    await navigator.clipboard.writeText(v.url)
    copyState[v.index] = 'ok'
  } catch {
    copyState[v.index] = 'fail'
  }
  setTimeout(() => { copyState[v.index] = 'idle' }, 2000)
}

async function selectSubject(s: Subject) {
  if (activeId.value === s.id) return
  active.value = s
  activeId.value = s.id
  videos.value = []
  loadingVideos.value = true
  try {
    const { data } = await subjectApi.videos(s.id)
    videos.value = data
    videoCountMap[s.id] = data.length
  } finally {
    loadingVideos.value = false
  }
}

onMounted(async () => {
  loadingSubjects.value = true
  try {
    const { data } = await subjectApi.list()
    subjects.value = data
    if (data.length > 0) selectSubject(data[0]!)
  } finally {
    loadingSubjects.value = false
  }
})
</script>

<style scoped>
/* ── 整体框架 ─────────────────────────────────────────────── */
.hub {
  display: flex;
  gap: 0;
  min-height: calc(100vh - 100px);
  background: var(--c-bg);
}

/* ── 左侧科目栏 ───────────────────────────────────────────── */
.hub-sidebar {
  width: 200px;
  flex-shrink: 0;
  border-right: 1px solid var(--c-border);
  padding: 0 0 24px;
  background: var(--c-surface);
}
.hub-sidebar-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-text-3);
  padding: 20px 16px 10px;
}
.hub-subject-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}
.hub-subject-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  border-left: 3px solid transparent;
  color: var(--c-text-2);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  text-align: left;
  background: transparent;
  width: 100%;
}
.hub-subject-item:hover {
  background: var(--c-info-light);
  color: var(--c-text);
}
.hub-subject-item.active {
  background: color-mix(in srgb, var(--accent, var(--c-primary)) 12%, transparent);
  color: var(--accent, var(--c-primary));
  font-weight: 600;
}
.hub-subject-icon { font-size: 16px; flex-shrink: 0; }
.hub-subject-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hub-subject-count {
  font-size: 11px;
  background: var(--c-border);
  color: var(--c-text-3);
  border-radius: 10px;
  padding: 1px 7px;
  flex-shrink: 0;
}
.hub-subject-item.active .hub-subject-count {
  background: color-mix(in srgb, var(--accent, var(--c-primary)) 20%, transparent);
  color: var(--accent, var(--c-primary));
}

/* ── 右侧内容区 ───────────────────────────────────────────── */
.hub-content {
  flex: 1;
  min-width: 0;
  padding: 24px 28px;
}

.hub-content-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: var(--r);
  border: 1px solid var(--c-border);
  border-left-width: 5px;
  background: var(--c-surface);
  margin-bottom: 20px;
}
.hub-content-icon { font-size: 32px; flex-shrink: 0; }
.hub-content-title { font-size: 20px; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.hub-content-desc { font-size: 13px; color: var(--c-text-2); line-height: 1.4; }

.hub-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--c-text-3);
  font-size: 14px;
}
.hub-empty .empty-icon { font-size: 40px; }

/* ── 视频列表 ─────────────────────────────────────────────── */
.hub-video-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  list-style: none;
  padding: 0;
  margin: 0;
}
.hub-video-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: var(--r);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  transition: box-shadow 0.15s;
}
.hub-video-item:hover { box-shadow: var(--shadow); }

.hub-video-num {
  min-width: 26px;
  font-size: 14px;
  font-weight: 700;
  color: var(--c-text-3);
  flex-shrink: 0;
  text-align: center;
}
.hub-video-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.hub-video-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hub-video-title:hover { color: var(--c-primary); text-decoration: underline; }
.hub-video-url {
  font-size: 12px;
  color: var(--c-text-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hub-video-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.btn-bilibili {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: var(--r-sm);
  background: #fb7299;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn-bilibili:hover { opacity: 0.85; }

.btn-copy {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: var(--r-sm);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text-2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
  min-width: 72px;
  justify-content: center;
}
.btn-copy:hover { background: var(--c-info-light); color: var(--c-text); }
.btn-copy.ok {
  background: var(--c-success-light, #dcfce7);
  color: var(--c-success, #16a34a);
  border-color: var(--c-success, #16a34a);
}
.btn-copy.fail {
  background: #fee2e2;
  color: var(--c-danger);
  border-color: var(--c-danger);
}

/* ── 响应式 ───────────────────────────────────────────────── */
@media (max-width: 680px) {
  .hub { flex-direction: column; }
  .hub-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--c-border);
    padding-bottom: 12px;
  }
  .hub-subject-list { flex-direction: row; flex-wrap: wrap; padding: 0 12px; }
  .hub-subject-item { width: auto; }
  .hub-content { padding: 16px; }
  .hub-video-actions { flex-direction: column; gap: 4px; }
}
</style>
