<template>
  <div class="dashboard">

    <!-- 1. 欢迎语 -->
    <section class="welcome-section">
      <div class="welcome-text">
        <span class="welcome-hi">{{ greeting }}，</span>
        <span class="welcome-name">{{ auth.isAdmin ? '同学' : (auth.username || '同学') }}</span>
        <span class="welcome-emoji">👋</span>
      </div>
      <p class="welcome-sub">{{ history.length ? '接着上次的内容继续吧' : '选一个开始今天的学习吧' }}</p>
    </section>

    <!-- 2. 快捷入口 -->
    <section class="section">
      <h2 class="section-title">快捷入口</h2>
      <div class="quick-grid">
        <RouterLink v-for="(q, i) in quickLinks" :key="q.name" v-reveal="i" :to="q.to" class="quick-card lift" :style="{ '--c': q.color }">
          <span class="quick-icon"><AppIcon :name="q.icon" :size="22" /></span>
          <div class="quick-info">
            <span class="quick-name">{{ q.name }}</span>
            <span class="quick-desc">{{ q.desc }}</span>
          </div>
          <AppIcon name="arrow" :size="16" class="quick-arrow" />
        </RouterLink>
      </div>
    </section>

    <!-- 3. 最近内容 -->
    <section class="section">
      <h2 class="section-title">最近访问</h2>
      <div v-if="!history.length" v-reveal class="empty-recent">
        <AppIcon name="clock" :size="28" :stroke="1.5" />
        <p>还没有学习记录</p>
        <span>看过的视频、听过的音频会出现在这里，方便下次继续</span>
        <RouterLink :to="{ name: 'topik-video' }" class="empty-cta press">去看第一个视频</RouterLink>
      </div>
      <ul v-else class="recent-list">
        <li v-for="(item, i) in history" :key="item.url + item.ts" v-reveal="i" class="recent-item">
          <span class="recent-type-icon"><AppIcon :name="typeIcon[item.type] ?? 'file'" :size="16" /></span>
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
            :to="{ name: 'topik-video' }"
            class="recent-action"
          >播放</RouterLink>
        </li>
      </ul>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/core/stores/auth'
import { getHistory, type HistoryItem } from '@/topik/composables/useHistory'
import AppIcon from '@/core/components/AppIcon.vue'

const auth = useAuthStore()
const history = ref<HistoryItem[]>([])

const quickLinks = [
  { to: { name: 'topik-video' }, icon: 'video', name: '视频课程', desc: '在线观看课程视频', color: '#5ad8cf' },
  { to: { name: 'topik-audio' }, icon: 'audio', name: '听力音频', desc: 'MP3 在线收听', color: '#6f9be8' },
  { to: { name: 'topik-file' },  icon: 'file',  name: '学习资料', desc: 'PDF 资料下载', color: '#fb923c' },
] as const

const greeting = (() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})()

const typeIcon: Record<string, 'video' | 'audio' | 'file'> = {
  video: 'video',
  audio: 'audio',
  file:  'file',
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
  text-decoration: none;
  background: var(--surface-2);
  border-color: color-mix(in srgb, var(--c) 45%, transparent);
}

.quick-icon {
  flex-shrink: 0;
  width: 44px; height: 44px; border-radius: 12px;
  display: grid; place-items: center;
  color: var(--c); background: color-mix(in srgb, var(--c) 14%, transparent);
  transition: transform 0.35s var(--ease-spring);
}
.quick-card:hover .quick-icon { transform: scale(1.08) rotate(-4deg); }

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
  display: flex; flex-direction: column; align-items: center; gap: 0.35rem;
  padding: 2.25rem 1.25rem; text-align: center;
  border: 1px dashed var(--border-strong); border-radius: var(--r-lg);
  color: var(--text-subtle);
}
.empty-recent p { font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0.35rem; }
.empty-recent span { font-size: 0.82rem; }
.empty-cta {
  margin-top: 0.9rem; padding: 0.5rem 1.1rem; border-radius: 999px;
  font-size: 0.85rem; font-weight: 600;
  color: var(--primary); background: var(--primary-dim); border: 1px solid var(--border-primary);
}
.empty-cta:hover { text-decoration: none; background: var(--primary-glow); }

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
  flex-shrink: 0;
  width: 32px; height: 32px; border-radius: 9px;
  display: grid; place-items: center;
  color: var(--primary); background: var(--primary-dim);
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
