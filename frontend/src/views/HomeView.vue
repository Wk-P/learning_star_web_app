<template>
  <div class="layout">

    <!-- sticky nav -->
    <nav class="top-nav">
      <span class="site-mark">韩途</span>
      <div class="nav-right">
        <RouterLink :to="{ name: 'user-dashboard' }" class="nav-link">学习内容</RouterLink>
        <RouterLink :to="{ name: 'admin-login' }" class="nav-link nav-link--ghost">管理</RouterLink>
        <button class="theme-btn" @click="theme.toggle()" :aria-label="theme.isDark ? '切换浅色' : '切换深色'">
          {{ theme.isDark ? '☾' : '☀' }}
        </button>
      </div>
    </nav>

    <!-- scroll container -->
    <div class="scroll-wrap">

      <!-- screen 1: hero -->
      <section class="screen screen-hero">
        <div class="hero-logo-wrap">
          <img src="/home-logo.png" class="hero-logo-img" />
        </div>
        <div class="hero-content">
          <div class="hero-badge">韩国语学习平台</div>
          <h1 class="hero-title">学习资源中心</h1>
          <p class="hero-sub">视频 · 音频 · 文件，一站式访问</p>
          <div class="scroll-hint" aria-hidden="true">
            <span class="scroll-arrow">↓</span>
          </div>
        </div>
      </section>

      <!-- screen 2: cards -->
      <section class="screen screen-cards">
        <div class="cards-content">
          <p class="cards-eyebrow">开始学习</p>
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
        <AppFooter class="home-footer" />
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import AppFooter from '@/components/AppFooter.vue'

const theme = useThemeStore()
const cards = ref([
  { url: { name: 'user-video' }, name: '视频', icon: '▶', desc: 'HLS 流媒体播放' },
  { url: { name: 'user-audio' }, name: '音频', icon: '♫', desc: 'MP3 在线收听' },
  { url: { name: 'user-file' }, name: '文件', icon: '↓', desc: 'PDF 资料下载' },
])
</script>

<style scoped>
/* ── shell ──────────────────────── */
.layout {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── nav ────────────────────────── */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 1.5rem;
  background: var(--surface-nav);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
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

/* ── scroll container ───────────── */
.scroll-wrap {
  flex: 1;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  overscroll-behavior: none;
}

/* ── screen base ────────────────── */
.screen {
  height: 100%;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* screen 1: 从深蓝渐变到 bg，底部与 screen 2 顶部完全一致 */
.screen-hero {
  background: linear-gradient(to bottom, #0b1929 0%, #07090e 100%);
}

/* screen 2: 顶部从 bg 开始，向深色渐变 */
.screen-cards {
  background: linear-gradient(to bottom, #07090e 0%, #060810 100%);
}

[data-theme="light"] .screen-hero {
  background: linear-gradient(to bottom, #cceae7 0%, #e6f5f4 100%);
}

[data-theme="light"] .screen-cards {
  background: linear-gradient(to bottom, #e6f5f4 0%, #ddf0ee 100%);
}

/* ── screen 1: hero ─────────────── */
.screen-hero {
  flex-direction: column;
  gap: 0;
}

.hero-logo-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  min-height: 0;
  position: relative;
}

.hero-logo-wrap::before {
  content: '';
  position: absolute;
  width: min(500px, 90vw);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%);
  filter: blur(40px);
  opacity: 0.6;
  pointer-events: none;
  animation: pulse-glow 3s ease-in-out infinite;
}

.hero-logo-img {
  max-height: 100%;
  max-width: min(420px, 75vw);
  width: auto;
  height: auto;
  object-fit: contain;
  position: relative;
  z-index: 1;
  animation: float 4s ease-in-out infinite;
  filter: drop-shadow(0 8px 32px var(--primary-glow));
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-12px); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50%       { opacity: 0.7; transform: scale(1.1); }
}

.hero-content {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
  padding: 1.5rem 1.5rem 2rem;
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

.scroll-hint {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
}

.scroll-arrow {
  font-size: 1.1rem;
  color: var(--text-subtle);
  animation: bob 1.6s ease-in-out infinite;
}

@keyframes bob {
  0%, 100% { transform: translateY(0); opacity: 0.5; }
  50%       { transform: translateY(6px); opacity: 1; }
}

/* ── footer ─────────────────────── */
.home-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

/* ── screen 2: cards ────────────── */

.cards-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
  max-width: 720px;
  padding: 0 1.5rem;
}

.cards-eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-subtle);
}

.cards {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  width: 100%;
}

.card-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  padding: 2.5rem 1.25rem 2rem;
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
  box-shadow: 0 12px 36px rgba(0,0,0,0.22), 0 0 0 1px var(--border-primary);
}

[data-theme="light"] .card-link:hover {
  box-shadow: 0 12px 36px rgba(13,148,136,0.12), 0 0 0 1px var(--border-primary);
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

/* ── mobile ─────────────────────── */
@media (max-width: 600px) {
  .top-nav { padding: 0.6rem 1rem; }

  .hero-title { font-size: 2rem; }

  .hero-content {
    padding: 1rem 1rem 1.5rem;
    gap: 0.55rem;
  }

  .scroll-hint { margin-top: 1rem; }

  .hero-logo-wrap { padding: 1rem; }

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

@media (max-height: 600px) and (max-width: 900px) {
  .hero-content { padding: 0.75rem 1rem 1rem; gap: 0.4rem; }
  .scroll-hint { margin-top: 0.5rem; }
  .hero-title { font-size: clamp(1.5rem, 4vw, 2rem); }
}
</style>
