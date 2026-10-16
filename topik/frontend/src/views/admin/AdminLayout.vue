<template>
  <div class="admin-shell">
    <!-- sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-mark">韩途</span>
        <span class="logo-text">Admin</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/admin/dashboard" class="nav-item">
          <span class="nav-icon">▦</span>
          <span>概览</span>
        </RouterLink>
        <RouterLink to="/admin/video" class="nav-item">
          <span class="nav-icon">▶</span>
          <span>视频</span>
        </RouterLink>
        <RouterLink to="/admin/audio" class="nav-item">
          <span class="nav-icon">♫</span>
          <span>音频</span>
        </RouterLink>
        <RouterLink to="/admin/pdf" class="nav-item">
          <span class="nav-icon">↓</span>
          <span>PDF</span>
        </RouterLink>
        <RouterLink to="/admin/users" class="nav-item">
          <span class="nav-icon">⊙</span>
          <span>用户</span>
        </RouterLink>
        <RouterLink to="/admin/permissions" class="nav-item">
          <span class="nav-icon">🔑</span>
          <span>权限</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- main area -->
    <div class="admin-main">
      <header class="admin-header">
        <span class="header-path">{{ pageTitle }}</span>
        <RouterLink :to="{ name: 'home' }" class="header-link">← 返回前台</RouterLink>
      </header>
      <main class="admin-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const titleMap: Record<string, string> = {
  '/admin/dashboard': '概览',
  '/admin/video': '视频管理',
  '/admin/audio': '音频管理',
  '/admin/pdf':   'PDF 管理',
  '/admin/users': '用户管理',
  '/admin/permissions': '权限管理',
}
const pageTitle = computed(() => titleMap[route.path] ?? 'Admin')

function logout() {
  auth.clearTokens()
  router.push('/admin/login')
}
</script>

<style scoped>
/* ── shell: always dark ────────────── */
.admin-shell {
  min-height: 100dvh;
  display: flex;
  background: #07090e;
  color: #e2e8f0;

  /* element-plus dark overrides scoped to admin */
  --el-bg-color:                   #111520;
  --el-bg-color-page:              #0d1019;
  --el-bg-color-overlay:           #1a2030;
  --el-text-color-primary:         #e2e8f0;
  --el-text-color-regular:         #cbd5e1;
  --el-text-color-secondary:       #8892a4;
  --el-text-color-placeholder:     #4a5568;
  --el-border-color:               rgba(255, 255, 255, 0.10);
  --el-border-color-light:         rgba(255, 255, 255, 0.07);
  --el-border-color-lighter:       rgba(255, 255, 255, 0.05);
  --el-fill-color:                 rgba(255, 255, 255, 0.05);
  --el-fill-color-light:           rgba(255, 255, 255, 0.03);
  --el-fill-color-blank:           #111520;
  --el-color-primary:              #2dd4bf;
  --el-color-primary-light-3:      rgba(45, 212, 191, 0.30);
  --el-color-primary-light-5:      rgba(45, 212, 191, 0.20);
  --el-color-primary-light-7:      rgba(45, 212, 191, 0.14);
  --el-color-primary-light-9:      rgba(45, 212, 191, 0.08);
  --el-card-bg-color:              #111520;
  --el-table-bg-color:             #111520;
  --el-table-tr-bg-color:          #111520;
  --el-table-header-bg-color:      #161c2a;
  --el-table-row-hover-bg-color:   rgba(255, 255, 255, 0.04);
  --el-table-border-color:         rgba(255, 255, 255, 0.08);
  --el-table-fixed-box-shadow:     none;
  --el-statistic-content-font-size:2rem;

  /* table text — must be explicit or Element Plus `:root` value wins */
  --el-table-text-color:           #cbd5e1;
  --el-table-header-text-color:    #94a3b8;
  --el-table-current-row-bg-color: rgba(45, 212, 191, 0.06);
}

/* ── sidebar ─────────────────────── */
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #0a0d14;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100dvh;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  margin-bottom: 0.5rem;
}

.logo-mark {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #2dd4bf;
  color: #07090e;
  font-size: 0.7rem;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.logo-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.04em;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.85rem;
  border-radius: 0.625rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #8892a4;
  text-decoration: none;
  transition: color 0.18s ease, background 0.18s ease;
}

.nav-item:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.router-link-active {
  color: #2dd4bf;
  background: rgba(45, 212, 191, 0.10);
  font-weight: 600;
}

.nav-icon {
  font-size: 0.8rem;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
  opacity: 0.8;
}

.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.logout-btn {
  width: 100%;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: none;
  color: #8892a4;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.18s ease;
}

.logout-btn:hover {
  background: rgba(248, 113, 113, 0.08);
  border-color: rgba(248, 113, 113, 0.25);
  color: #f87171;
}

/* ── main area ───────────────────── */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #0d1019;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  position: sticky;
  top: 0;
  z-index: 30;
}

.header-path {
  font-size: 0.9rem;
  font-weight: 600;
  color: #e2e8f0;
}

.header-link {
  font-size: 0.8rem;
  color: #8892a4;
  text-decoration: none;
  transition: color 0.18s ease;
}

.header-link:hover { color: #2dd4bf; }

.admin-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

/* ── mobile: sidebar → horizontal top bar ── */
@media (max-width: 768px) {
  .admin-shell { flex-direction: column; }

  .sidebar {
    width: 100%;
    height: auto;
    position: sticky;
    top: 0;
    z-index: 40;
    flex-direction: row;
    overflow-x: auto;
    overflow-y: visible;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    scrollbar-width: none;
  }

  .sidebar::-webkit-scrollbar { display: none; }

  .sidebar-logo {
    padding: 0 1rem;
    border-bottom: none;
    margin-bottom: 0;
    flex-shrink: 0;
    height: 48px;
  }

  .sidebar-nav {
    flex-direction: row;
    gap: 0.15rem;
    padding: 0 0.25rem;
    flex: 1;
    align-items: center;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .sidebar-nav::-webkit-scrollbar { display: none; }

  .nav-item {
    flex-shrink: 0;
    padding: 0.5rem 0.75rem;
    font-size: 0.82rem;
    height: 48px;
    border-radius: 0;
    border-bottom: 2px solid transparent;
  }

  .nav-item.router-link-active {
    background: none;
    border-bottom-color: #2dd4bf;
  }

  .sidebar-footer {
    padding: 0 0.5rem;
    border-top: none;
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .logout-btn {
    width: auto;
    white-space: nowrap;
    height: 32px;
    padding: 0 0.75rem;
  }

  .admin-header { padding: 0.6rem 1rem; }

  .admin-content { padding: 0.75rem; }
}
</style>
