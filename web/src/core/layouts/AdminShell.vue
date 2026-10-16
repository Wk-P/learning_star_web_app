<template>
  <!-- 管理后台固定使用深色工作台风格（原后台样式按深色设计） -->
  <div class="admin-shell" data-theme="dark">
    <!-- sidebar -->
    <aside class="sidebar">
      <RouterLink to="/" class="sidebar-logo">
        <span class="logo-mark"><AppIcon name="book" :size="14" :stroke="2.2" /></span>
        <span class="logo-text">管理后台</span>
      </RouterLink>

      <nav class="sidebar-nav">
        <template v-for="g in groups" :key="g.title">
          <span class="nav-group" :style="g.color ? { '--c': g.color } : undefined">{{ g.title }}</span>
          <RouterLink
            v-for="item in g.items" :key="item.to" :to="item.to"
            class="nav-item" :class="{ active: isActive(item.to) }"
          >
            <AppIcon :name="item.icon" :size="17" class="nav-icon" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </template>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- main area -->
    <div class="admin-main">
      <header class="admin-header">
        <span class="header-path">{{ route.meta.title ?? '管理后台' }}</span>
        <RouterLink :to="{ name: 'home' }" class="header-link">← 返回前台</RouterLink>
      </header>
      <main class="admin-content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { BRAND, SECTIONS } from '@/core/brand'
import AppIcon from '@/core/components/AppIcon.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const groups = [
  { title: '通用', color: '', items: [
    { to: '/admin', label: '概览', icon: 'grid' },
    { to: '/admin/users', label: '用户', icon: 'user' },
  ] },
  { title: SECTIONS.topik.label, color: SECTIONS.topik.color, items: [
    { to: '/admin/topik/video', label: '视频', icon: 'video' },
    { to: '/admin/topik/audio', label: '音频', icon: 'audio' },
    { to: '/admin/topik/pdf', label: '资料', icon: 'file' },
    { to: '/admin/permissions', label: '学习权限', icon: 'shield' },
  ] },
  { title: SECTIONS.course.label, color: SECTIONS.course.color, items: [
    { to: '/admin/course/subjects', label: '科目与视频', icon: 'book' },
    { to: '/admin/course/roadmap', label: '学习路线图', icon: 'file' },
  ] },
] as const

// 课程管理的弹窗挂在 #course-layer（页面根部），也切到深色
function setLayerTheme(theme: string | null) {
  const layer = document.getElementById('course-layer')
  if (!layer) return
  if (theme) layer.setAttribute('data-theme', theme)
  else layer.removeAttribute('data-theme')
}
onMounted(() => setLayerTheme('dark'))
onBeforeUnmount(() => setLayerTheme(null))

function isActive(to: string) {
  return to === '/admin' ? route.path === '/admin' || route.path === '/admin/' : route.path.startsWith(to)
}

function logout() {
  auth.clearTokens()
  router.push({ name: 'login' })
}
</script>

<style scoped>
/* ── shell: always dark ────────────── */
.admin-shell {
  min-height: 100dvh;
  display: flex;
  background: #0a1428;
  color: #e2e8f0;

  /* element-plus dark overrides scoped to admin */
  --el-bg-color:                   #112042;
  --el-bg-color-page:              #0d1a35;
  --el-bg-color-overlay:           #18294d;
  --el-text-color-primary:         #e2e8f0;
  --el-text-color-regular:         #cbd5e1;
  --el-text-color-secondary:       #8892a4;
  --el-text-color-placeholder:     #4a5568;
  --el-border-color:               rgba(255, 255, 255, 0.10);
  --el-border-color-light:         rgba(255, 255, 255, 0.07);
  --el-border-color-lighter:       rgba(255, 255, 255, 0.05);
  --el-fill-color:                 rgba(255, 255, 255, 0.05);
  --el-fill-color-light:           rgba(255, 255, 255, 0.03);
  --el-fill-color-blank:           #112042;
  --el-color-primary:              #5ad8cf;
  --el-color-primary-light-3:      rgba(90, 216, 207, 0.30);
  --el-color-primary-light-5:      rgba(90, 216, 207, 0.20);
  --el-color-primary-light-7:      rgba(90, 216, 207, 0.14);
  --el-color-primary-light-9:      rgba(90, 216, 207, 0.08);
  --el-card-bg-color:              #112042;
  --el-table-bg-color:             #112042;
  --el-table-tr-bg-color:          #112042;
  --el-table-header-bg-color:      #15284f;
  --el-table-row-hover-bg-color:   rgba(255, 255, 255, 0.04);
  --el-table-border-color:         rgba(255, 255, 255, 0.08);
  --el-table-fixed-box-shadow:     none;
  --el-statistic-content-font-size:2rem;

  /* table text — must be explicit or Element Plus `:root` value wins */
  --el-table-text-color:           #cbd5e1;
  --el-table-header-text-color:    #94a3b8;
  --el-table-current-row-bg-color: rgba(90, 216, 207, 0.06);
}

/* ── sidebar ─────────────────────── */
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #0b1630;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100dvh;
  overflow-y: auto;
}

.sidebar-logo {
  text-decoration: none; color: var(--text);
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.25rem 1rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  margin-bottom: 0.5rem;
}

.logo-mark {
  width: 24px; height: 24px; border-radius: 7px;
  display: grid; place-items: center; color: #fff;
  background: linear-gradient(135deg, #2ec4c0, #1e4fa8);
}
.nav-group {
  display: flex; align-items: center; gap: 0.45rem;
  margin: 0.9rem 0.75rem 0.3rem; font-size: 0.7rem; font-weight: 700;
  letter-spacing: 0.06em; color: var(--text-subtle);
}
.nav-group::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--c, var(--text-subtle)); }

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

.nav-item.active {
  color: #5ad8cf;
  background: rgba(90, 216, 207, 0.10);
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
  background: #0d1a35;
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

.header-link:hover { color: #5ad8cf; }

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
  .nav-group { display: none; }

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

  .nav-item.active {
    background: none;
    border-bottom-color: #5ad8cf;
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
