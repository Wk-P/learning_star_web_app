<template>
  <div class="dashboard">

    <!-- 1. 欢迎语 -->
    <section class="welcome-section">
      <div class="welcome-text">
        <span class="welcome-hi">你好，</span>
        <span class="welcome-name">{{ auth.isAdmin ? '同学' : (auth.username || '同学') }}</span>
        <span class="welcome-emoji">👋</span>
      </div>
      <p class="welcome-sub">今天也要好好学习哦</p>
    </section>

    <!-- 2. 快捷入口 -->
    <section class="section">
      <h2 class="section-title">快捷入口</h2>
      <div class="quick-grid">
        <RouterLink v-for="q in quickLinks" :key="q.name" :to="q.to" class="quick-card">
          <span class="quick-icon">{{ q.icon }}</span>
          <div class="quick-info">
            <span class="quick-name">{{ q.name }}</span>
            <span class="quick-desc">{{ q.desc }}</span>
          </div>
          <span class="quick-arrow">→</span>
        </RouterLink>
      </div>
    </section>

    <!-- 3. 最近内容 -->
    <section class="section">
      <h2 class="section-title">最近访问</h2>
      <div v-if="!history.length" class="empty-recent">
        暂无记录，开始浏览内容后会显示在这里
      </div>
      <ul v-else class="recent-list">
        <li v-for="item in history" :key="item.url + item.ts" class="recent-item">
          <span class="recent-type-icon">{{ typeIcon[item.type] }}</span>
          <div class="recent-info">
            <span class="recent-title">{{ item.title }}</span>
            <span class="recent-path">{{ item.path.join(' › ') }}</span>
          </div>
          <span class="recent-time">{{ relativeTime(item.ts) }}</span>
          <a
            v-if="item.type !== 'video'"
            :href="item.url"
            target="_blank"
            class="recent-action"
          >打开</a>
          <RouterLink
            v-else
            :to="{ name: 'user-video' }"
            class="recent-action"
          >播放</RouterLink>
        </li>
      </ul>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getHistory, type HistoryItem } from '@/composables/useHistory'

const auth = useAuthStore()
const history = ref<HistoryItem[]>([])

const quickLinks = [
  { to: { name: 'user-video' }, icon: '▶', name: '视频课程', desc: 'HLS 流媒体播放' },
  { to: { name: 'user-audio' }, icon: '♫', name: '音频资料', desc: 'MP3 在线收听' },
  { to: { name: 'user-file' },  icon: '↓', name: '文件下载', desc: 'PDF 资料下载' },
]

const typeIcon: Record<string, string> = {
  video: '▶',
  audio: '♫',
  file:  '↓',
}

function relativeTime(ts: number): string {
  const diff = Date.now() - ts
  const m = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const d = Math.floor(diff / 86400000)
  if (m < 1)  return '刚刚'
  if (m < 60) return `${m} 分钟前`
  if (h < 24) return `${h} 小时前`
  return `${d} 天前`
}

onMounted(() => {
  history.value = getHistory().slice(0, 10)
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-top: 1.5rem;
}

/* ── welcome ── */
.welcome-section {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.welcome-text {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.welcome-hi   { font-size: 1.75rem; font-weight: 300; color: var(--text-muted); }
.welcome-name { font-size: 1.75rem; font-weight: 800; color: var(--text); }
.welcome-emoji { font-size: 1.5rem; }
.welcome-sub  { font-size: 0.9rem; color: var(--text-subtle); padding-left: 0.1rem; }

/* ── section ── */
.section { display: flex; flex-direction: column; gap: 0.75rem; }

.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-subtle);
}

/* ── quick cards ── */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  text-decoration: none;
  transition: background var(--t), border-color var(--t), transform 0.18s var(--ease);
}

.quick-card:hover {
  background: var(--surface-2);
  border-color: var(--border-primary);
  transform: translateY(-2px);
}

.quick-icon {
  font-size: 1.3rem;
  color: var(--primary);
  flex-shrink: 0;
  width: 2rem;
  text-align: center;
}

.quick-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.quick-name { font-size: 0.9rem; font-weight: 600; color: var(--text); }
.quick-desc { font-size: 0.75rem; color: var(--text-subtle); }

.quick-arrow {
  font-size: 0.85rem;
  color: var(--text-subtle);
  flex-shrink: 0;
  transition: transform 0.18s, color 0.18s;
}

.quick-card:hover .quick-arrow {
  transform: translateX(3px);
  color: var(--primary);
}

/* ── recent list ── */
.empty-recent {
  font-size: 0.85rem;
  color: var(--text-subtle);
  padding: 1.5rem 0;
}

.recent-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  transition: background var(--t);
}

.recent-item:hover { background: var(--surface-2); }

.recent-type-icon {
  font-size: 0.8rem;
  color: var(--primary);
  opacity: 0.8;
  flex-shrink: 0;
  width: 1rem;
  text-align: center;
}

.recent-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.recent-title {
  font-size: 0.875rem;
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-path {
  font-size: 0.72rem;
  color: var(--text-subtle);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-time {
  font-size: 0.72rem;
  color: var(--text-subtle);
  flex-shrink: 0;
  white-space: nowrap;
}

.recent-action {
  font-size: 0.78rem;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  flex-shrink: 0;
  padding: 0.2rem 0.6rem;
  border-radius: var(--r-sm);
  border: 1px solid var(--border-primary);
  transition: background var(--t);
}

.recent-action:hover { background: var(--primary-dim); }

/* ── mobile ── */
@media (max-width: 600px) {
  .quick-grid { grid-template-columns: 1fr; }
  .quick-card { padding: 0.85rem 1rem; }
  .welcome-hi, .welcome-name { font-size: 1.4rem; }
}

@media (max-width: 480px) {
  .recent-item { gap: 0.5rem; padding: 0.6rem 0.75rem; }
  .recent-time { display: none; }
  .recent-title { font-size: 0.82rem; }
  .recent-path { display: none; }
}
</style>
