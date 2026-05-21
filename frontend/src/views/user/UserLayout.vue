<template>
  <div class="user-layout">
    <!-- desktop top nav -->
    <nav class="top-nav">
      <RouterLink :to="{ name: 'home' }" class="nav-link nav-link--back">← 首页</RouterLink>
      <div class="nav-tabs">
        <RouterLink :to="{ name: 'user-video' }" class="nav-link">视频</RouterLink>
        <RouterLink :to="{ name: 'user-audio' }" class="nav-link">音频</RouterLink>
        <RouterLink :to="{ name: 'user-file' }" class="nav-link">文件</RouterLink>
      </div>
      <div class="nav-right-group">
        <button class="theme-btn" @click="theme.toggle()" :aria-label="theme.isDark ? '切换浅色' : '切换深色'">
          <span class="theme-icon">{{ theme.isDark ? '☾' : '☀' }}</span>
          <span class="theme-label">{{ theme.isDark ? '浅色' : '深色' }}</span>
        </button>
        <button class="logout-btn" @click="logout">退出</button>
      </div>
    </nav>

    <!-- page content -->
    <div class="page-content">
      <RouterView v-slot="{ Component }">
        <Transition name="opacity" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>

    <!-- mobile bottom tab bar -->
    <nav class="bottom-nav" aria-label="底部导航">
      <RouterLink :to="{ name: 'home' }" class="tab-item">
        <span class="tab-icon">⌂</span>
        <span class="tab-label">首页</span>
      </RouterLink>
      <RouterLink :to="{ name: 'user-video' }" class="tab-item">
        <span class="tab-icon">▶</span>
        <span class="tab-label">视频</span>
      </RouterLink>
      <RouterLink :to="{ name: 'user-audio' }" class="tab-item">
        <span class="tab-icon">♫</span>
        <span class="tab-label">音频</span>
      </RouterLink>
      <RouterLink :to="{ name: 'user-file' }" class="tab-item">
        <span class="tab-icon">↓</span>
        <span class="tab-label">文件</span>
      </RouterLink>
      <button class="tab-item tab-theme-btn" @click="theme.toggle()">
        <span class="tab-icon">{{ theme.isDark ? '☾' : '☀' }}</span>
        <span class="tab-label">主题</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const theme = useThemeStore()
const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.clearTokens()
  router.push('/login')
}
</script>

<style scoped>
/* ── shell ───────────────────────────── */
.user-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

/* ── desktop top nav ─────────────────── */
.top-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  background: var(--surface-nav);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-tabs {
  display: flex;
  gap: 0.25rem;
  margin-left: 0.5rem;
  flex: 1;
}

.nav-link {
  padding: 0.4rem 1rem;
  border-radius: var(--r-xl);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-muted);
  border: 1px solid transparent;
  transition: color var(--t), background var(--t), border-color var(--t);
  white-space: nowrap;
}

.nav-link:hover {
  color: var(--text);
  background: var(--surface-2);
}

.nav-link.router-link-active {
  color: var(--primary);
  background: var(--primary-dim);
  border-color: var(--border-primary);
  font-weight: 600;
}

.nav-link--back {
  font-size: 0.8rem;
  color: var(--text-subtle);
  padding: 0.4rem 0.75rem;
}

.nav-link--back:hover {
  color: var(--text-muted);
  background: none;
}

.nav-right-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.logout-btn {
  padding: 0.38rem 0.85rem;
  border-radius: var(--r-xl);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--t);
}

.logout-btn:hover {
  border-color: rgba(248, 113, 113, 0.4);
  color: #f87171;
}

/* ── theme toggle (desktop) ──────────── */
.theme-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.38rem 0.85rem;
  border-radius: var(--r-xl);
  border: 1px solid var(--border-strong);
  background: var(--surface-1);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--t);
  white-space: nowrap;
  flex-shrink: 0;
}

.theme-btn:hover {
  background: var(--surface-2);
  border-color: var(--border-primary);
  color: var(--primary);
}

.theme-icon {
  font-size: 0.85rem;
  line-height: 1;
}

/* ── page content ─────────────────────── */
.page-content {
  flex: 1;
  padding: 0 1rem 1rem;
  max-width: 960px;
  width: 100%;
  margin: 0 auto;
}

/* ── mobile bottom nav ────────────────── */
.bottom-nav {
  display: none;
}

/* ── page transition ──────────────────── */
.opacity-enter-active,
.opacity-leave-active {
  transition: opacity 0.22s var(--ease), transform 0.22s var(--ease);
}
.opacity-enter-from { opacity: 0; transform: translateY(-10px); }
.opacity-leave-to   { opacity: 0; transform: translateY(8px); }
.opacity-enter-to,
.opacity-leave-from { opacity: 1; transform: none; }

/* ── mobile ──────────────────────────── */
@media (max-width: 768px) {
  .top-nav { display: none; }

  .page-content {
    padding: 0.75rem 0.75rem calc(68px + env(safe-area-inset-bottom, 0px));
  }

  .bottom-nav {
    display: flex;
    align-items: stretch;
    justify-content: space-around;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--surface-nav);
    backdrop-filter: var(--blur);
    -webkit-backdrop-filter: var(--blur);
    border-top: 1px solid var(--border);
    padding-bottom: env(safe-area-inset-bottom, 0px);
    z-index: 100;
  }

  .tab-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
    padding: 0.55rem 0.25rem;
    color: var(--text-subtle);
    text-decoration: none;
    transition: color var(--t);
    min-height: 54px;
    border: none;
    background: none;
    cursor: pointer;
  }

  .tab-item:hover,
  .tab-item.router-link-active {
    color: var(--primary);
  }

  .tab-theme-btn {
    color: var(--text-subtle);
  }

  .tab-theme-btn:hover {
    color: var(--primary);
  }

  .tab-icon {
    font-size: 1.15rem;
    line-height: 1;
  }

  .tab-label {
    font-size: 0.66rem;
    font-weight: 500;
    letter-spacing: 0.01em;
  }
}
</style>
