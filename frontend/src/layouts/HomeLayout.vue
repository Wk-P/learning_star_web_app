<template>
  <div class="hl-wrap">
    <!-- 顶部导航 -->
    <header class="hl-header">
      <div class="hl-header-inner">
        <router-link to="/home" class="hl-logo">
          <span class="hl-logo-icon">📚</span>
          <span>课程系统</span>
        </router-link>
        <nav class="hl-nav">
          <router-link to="/home" class="hl-nav-link">首页</router-link>
          <router-link v-if="auth.isAdmin" to="/admin/home" class="hl-nav-admin">
            管理后台
          </router-link>
          <router-link v-if="auth.user" to="/user/profile" class="hl-nav-user">
            <span class="hl-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</span>
            <span>{{ auth.user.username }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="hl-main">
      <nav v-if="breadcrumbs.length > 1" class="breadcrumb">
        <template v-for="(crumb, i) in breadcrumbs" :key="crumb.label">
          <router-link v-if="crumb.path" :to="crumb.path">{{ crumb.label }}</router-link>
          <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
          <span v-if="i < breadcrumbs.length - 1" class="breadcrumb-sep">/</span>
        </template>
      </nav>
      <RouterView />
    </main>

    <footer class="hl-footer">© {{ new Date().getFullYear() }} 课程管理系统</footer>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBreadcrumb } from '@/composables/useBreadcrumb'

const auth = useAuthStore()
const route = useRoute()
const { segments, clearSegments } = useBreadcrumb()

// 路由变化时清空动态面包屑，等新视图重新设置
watch(() => route.name, clearSegments)

const breadcrumbs = computed(() => {
  const base = [{ label: '首页', path: '/home' }]
  if (segments.value.length > 0) return [...base, ...segments.value]

  // 路由级静态后备（数据还未加载时显示）
  const name = route.name as string
  if (!name || name === 'home') return base
  if (name === 'subject-videos') return [...base, { label: '科目视频', path: '' }]
  return base
})
</script>

<style scoped>
.hl-wrap { display: flex; flex-direction: column; min-height: 100vh; }

.hl-header {
  position: sticky; top: 0; z-index: 100;
  background: var(--c-surface); border-bottom: 1px solid var(--c-border);
  box-shadow: var(--shadow-sm);
}
.hl-header-inner {
  max-width: 1200px; margin: 0 auto; padding: 0 24px;
  height: 58px; display: flex; align-items: center; justify-content: space-between;
}
.hl-logo {
  display: flex; align-items: center; gap: 8px;
  font-size: 17px; font-weight: 700; color: var(--c-text);
}
.hl-logo-icon { font-size: 22px; }
.hl-logo:hover { color: var(--c-primary); }

.hl-nav { display: flex; align-items: center; gap: 6px; }
.hl-nav-link {
  padding: 6px 14px; border-radius: var(--r-sm);
  color: var(--c-text-2); font-size: 14px; font-weight: 500;
  transition: background var(--t), color var(--t);
}
.hl-nav-link:hover, .hl-nav-link.router-link-active {
  background: var(--c-primary-light); color: var(--c-primary);
}

.hl-nav-admin {
  padding: 6px 14px; border-radius: var(--r-sm);
  background: var(--c-primary); color: #fff;
  font-size: 13px; font-weight: 500;
  transition: background var(--t);
}
.hl-nav-admin:hover { background: var(--c-primary-hover); color: #fff; }

.hl-nav-user {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 10px; border-radius: var(--r-sm);
  color: var(--c-text-2); font-size: 14px;
  transition: background var(--t);
  margin-left: 6px;
}
.hl-nav-user:hover { background: var(--c-info-light); color: var(--c-text); }
.hl-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--c-primary); color: #fff;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.hl-main { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 24px; }

.hl-footer {
  text-align: center; padding: 16px;
  font-size: 12px; color: var(--c-text-3);
  border-top: 1px solid var(--c-border);
}
</style>
