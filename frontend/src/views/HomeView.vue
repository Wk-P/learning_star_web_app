<template>
  <div class="layout">
    <nav class="top-nav">
      <span class="site-mark">Player3</span>
      <div class="nav-right">
        <RouterLink :to="{ name: 'user-dashboard' }" class="nav-link">学习内容</RouterLink>
        <RouterLink :to="{ name: 'admin-login' }" class="nav-link nav-link--ghost">管理</RouterLink>
        <button class="theme-btn" @click="theme.toggle()" :aria-label="theme.isDark ? '切换浅色' : '切换深色'">
          {{ theme.isDark ? '☾' : '☀' }}
        </button>
      </div>
    </nav>

    <main class="hero">
      <div class="hero-content">
        <div class="hero-badge">韩国语学习平台</div>
        <h1 class="hero-title">学习资源中心</h1>
        <p class="hero-sub">视频 · 音频 · 文件，一站式访问</p>

        <ul class="cards">
          <li v-for="card in cards" :key="card.url.name">
            <RouterLink :to="card.url" class="card-link">
              <span class="card-icon">{{ card.icon }}</span>
              <span class="card-name">{{ card.name }}</span>
              <span class="card-desc">{{ card.desc }}</span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
const cards = ref([
  { url: { name: 'user-video' }, name: '视频', icon: '▶', desc: 'HLS 流媒体播放' },
  { url: { name: 'user-audio' }, name: '音频', icon: '♫', desc: 'MP3 在线收听' },
  { url: { name: 'user-file' }, name: '文件', icon: '↓', desc: 'PDF 资料下载' },
])
</script>

<style scoped>
.layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

/* ── top nav ─────────────────────────── */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 1.5rem;
  background: var(--surface-nav);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.site-mark {
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link {
  padding: 0.38rem 0.9rem;
  border-radius: var(--r-xl);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
  border: 1px solid transparent;
  transition: color var(--t), background var(--t), border-color var(--t);
}

.nav-link:hover {
  color: var(--text);
  background: var(--surface-2);
}

.nav-link--ghost {
  color: var(--text-subtle);
  font-size: 0.8rem;
}

.theme-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--r-xl);
  border: 1px solid var(--border-strong);
  background: var(--surface-1);
  color: var(--text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--t);
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-btn:hover {
  background: var(--primary-dim);
  border-color: var(--border-primary);
  color: var(--primary);
}

/* ── hero ────────────────────────────── */
.hero {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 1.5rem 5rem;
}

.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
  max-width: 680px;
  width: 100%;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.28rem 0.85rem;
  border-radius: var(--r-xl);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary);
  background: var(--primary-dim);
  border: 1px solid var(--border-primary);
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.25rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.12;
  color: var(--text);
}

.hero-sub {
  font-size: 1rem;
  color: var(--text-muted);
  margin-top: -0.25rem;
}

/* ── cards ───────────────────────────── */
.cards {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
  margin-top: 1.75rem;
}

.card-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  padding: 2.25rem 1.25rem 1.75rem;
  border-radius: var(--r-lg);
  background: var(--surface-1);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border);
  transition: background var(--t), border-color var(--t), transform 0.22s var(--ease), box-shadow 0.22s var(--ease);
}

.card-link:hover {
  background: var(--surface-2);
  border-color: var(--border-primary);
  transform: translateY(-4px);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.22), 0 0 0 1px var(--border-primary);
}

[data-theme="light"] .card-link:hover {
  box-shadow: 0 12px 36px rgba(13, 148, 136, 0.12), 0 0 0 1px var(--border-primary);
}

.card-icon {
  font-size: 2.2rem;
  line-height: 1;
  color: var(--primary);
}

.card-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* ── mobile ──────────────────────────── */
@media (max-width: 600px) {
  .top-nav { padding: 0.6rem 1rem; }

  .hero { padding: 2rem 1rem 3rem; align-items: flex-start; }

  .hero-title { font-size: 2rem; }

  .cards {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .card-link {
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 1rem;
    padding: 1.25rem;
  }

  .card-icon { font-size: 1.6rem; flex-shrink: 0; }
  .card-name { font-size: 1rem; }
}
</style>
