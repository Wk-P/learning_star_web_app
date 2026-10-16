<template>
  <div class="shell" :style="section ? { '--section': section.color } : undefined">
    <!-- ── 顶部导航 ─────────────────────────────────────────── -->
    <header class="header">
      <div class="header-inner">
        <RouterLink to="/" class="brand press" aria-label="返回首页">
          <span class="brand-mark" aria-hidden="true">
            <AppIcon name="book" :size="16" :stroke="2.2" />
          </span>
          <span class="brand-name">{{ BRAND }}</span>
        </RouterLink>

        <nav class="main-nav" aria-label="栏目">
          <RouterLink to="/" class="main-link" :class="{ active: route.name === 'home' }">首页</RouterLink>
          <RouterLink
            v-for="s in sectionList" :key="s.key" :to="s.to"
            class="main-link" :class="{ active: section?.key === s.key }"
            :style="{ '--c': s.color }"
          >
            <span class="dot" aria-hidden="true" />{{ s.label }}
          </RouterLink>
        </nav>

        <div class="actions">
          <button class="icon-btn press" :aria-label="theme.isDark ? '切换到浅色' : '切换到深色'" :title="theme.isDark ? '浅色模式' : '深色模式'" @click="theme.toggle()">
            <Transition name="spin" mode="out-in">
              <AppIcon :key="String(theme.isDark)" :name="theme.isDark ? 'moon' : 'sun'" :size="18" />
            </Transition>
          </button>

          <div v-if="auth.isLoggedIn" ref="menuRoot" class="user">
            <button class="user-btn press" :aria-expanded="menuOpen" aria-haspopup="menu" @click="menuOpen = !menuOpen">
              <span class="avatar">{{ initial }}</span>
              <span class="user-name">{{ auth.username }}</span>
              <AppIcon name="chevron" :size="14" class="caret" :class="{ open: menuOpen }" />
            </button>
            <Transition name="menu">
              <div v-if="menuOpen" class="menu" role="menu">
                <div class="menu-head">
                  <span class="avatar avatar-lg">{{ initial }}</span>
                  <div>
                    <div class="menu-name">{{ auth.username }}</div>
                    <div class="menu-sub">{{ auth.isAdmin ? '管理员' : '学员' }}</div>
                  </div>
                </div>
                <RouterLink to="/me" class="menu-item" role="menuitem"><AppIcon name="user" :size="16" />我的账户</RouterLink>
                <RouterLink v-if="auth.isAdmin" to="/admin" class="menu-item" role="menuitem"><AppIcon name="settings" :size="16" />管理后台</RouterLink>
                <button class="menu-item danger" role="menuitem" @click="logout"><AppIcon name="logout" :size="16" />退出登录</button>
              </div>
            </Transition>
          </div>
          <RouterLink v-else :to="{ name: 'login', query: { redirect: route.fullPath } }" class="login-btn press">登录</RouterLink>
        </div>
      </div>

      <!-- 栏目内二级导航 -->
      <nav v-if="section" class="subnav" :aria-label="`${section.label}导航`">
        <div class="subnav-inner">
          <span class="subnav-title">{{ section.label }}</span>
          <div class="subnav-tabs">
            <RouterLink
              v-for="t in section.tabs" :key="t.to" :to="t.to"
              class="subnav-link" :class="{ active: isActiveTab(t) }"
            >{{ t.label }}</RouterLink>
          </div>
        </div>
      </nav>
    </header>

    <!-- ── 内容 ─────────────────────────────────────────────── -->
    <main class="main" :class="{ 'main--wide': route.name === 'home' }">
      <RouterView v-slot="{ Component, route: r }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="r.matched[1]?.path ?? r.path" />
        </Transition>
      </RouterView>
    </main>

    <AppFooter class="footer" />

    <!-- ── 手机底部标签栏 ───────────────────────────────────── -->
    <nav class="tabbar" aria-label="主导航">
      <RouterLink to="/" class="tab" :class="{ active: route.name === 'home' }">
        <AppIcon name="home" :size="22" /><span>首页</span>
      </RouterLink>
      <RouterLink v-for="s in sectionList" :key="s.key" :to="s.to" class="tab" :class="{ active: section?.key === s.key }">
        <AppIcon :name="s.icon" :size="22" /><span>{{ s.short }}</span>
      </RouterLink>
      <RouterLink to="/me" class="tab" :class="{ active: route.name === 'me' }">
        <AppIcon name="user" :size="22" /><span>我的</span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/core/stores/auth'
import { useThemeStore } from '@/core/stores/theme'
import { BRAND, SECTIONS, type Section, type SectionKey } from '@/core/brand'
import AppIcon from '@/core/components/AppIcon.vue'
import AppFooter from '@/core/components/AppFooter.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const sectionList = Object.values(SECTIONS)
const section = computed<Section | null>(() => {
  const key = route.matched.map((r) => r.meta.section).find(Boolean) as SectionKey | undefined
  return key ? SECTIONS[key] : null
})

function isActiveTab(t: Section['tabs'][number]) {
  return t.exact ? route.path === t.to || route.path === `${t.to}/` : route.path.startsWith(t.to)
}

const initial = computed(() => auth.username.slice(0, 1).toUpperCase() || '?')

// ── 用户菜单：点外部 / Esc / 路由变化时关闭 ───────────────────
const menuOpen = ref(false)
const menuRoot = ref<HTMLElement | null>(null)
const onDocClick = (e: MouseEvent) => {
  if (menuRoot.value && !menuRoot.value.contains(e.target as Node)) menuOpen.value = false
}
const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') menuOpen.value = false }
onMounted(() => { document.addEventListener('click', onDocClick); document.addEventListener('keydown', onKey) })
onBeforeUnmount(() => { document.removeEventListener('click', onDocClick); document.removeEventListener('keydown', onKey) })
watch(() => route.fullPath, () => { menuOpen.value = false })

function logout() {
  auth.clearTokens()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.shell { min-height: 100dvh; display: flex; flex-direction: column; --section: var(--primary); }

/* ── header ────────────────────────────────────────────── */
.header {
  position: sticky; top: 0; z-index: 60;
  background: var(--surface-nav);
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  border-bottom: 1px solid var(--border);
}
.header-inner {
  height: var(--shell-header);
  max-width: 1280px; margin: 0 auto; padding: 0 clamp(1rem, 3vw, 2rem);
  display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 1rem;
}
.brand { justify-self: start; display: inline-flex; align-items: center; gap: 0.55rem; color: var(--text); font-weight: 750; letter-spacing: -0.01em; }
.brand-mark {
  width: 30px; height: 30px; border-radius: 9px;
  display: grid; place-items: center; color: #fff;
  background: linear-gradient(135deg, #2ec4c0, #1e4fa8);
  box-shadow: 0 4px 14px rgba(30, 79, 168, 0.3);
}

.main-nav { display: flex; gap: 2px; padding: 4px; border-radius: 999px; background: var(--surface-1); border: 1px solid var(--border); }
.main-link {
  display: inline-flex; align-items: center; gap: 0.45rem;
  padding: 0.42rem 1.05rem; border-radius: 999px;
  font-size: 0.9rem; font-weight: 500; color: var(--text-muted); white-space: nowrap;
  transition: color var(--t), background var(--t), box-shadow var(--t);
}
.main-link:hover { color: var(--text); }
.main-link.active { color: var(--text); background: var(--surface-3); box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12); }
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--c); transition: transform 0.3s var(--ease-spring); }
.main-link.active .dot { transform: scale(1.25); box-shadow: 0 0 0 3px color-mix(in srgb, var(--c) 25%, transparent); }

.actions { justify-self: end; display: flex; align-items: center; gap: 0.4rem; }
.icon-btn {
  width: 36px; height: 36px; border-radius: 999px; display: grid; place-items: center;
  color: var(--text-muted); border: 1px solid transparent; background: transparent; cursor: pointer;
  transition: color var(--t), background var(--t);
}
.icon-btn:hover { color: var(--primary); background: var(--surface-2); }
.spin-enter-active, .spin-leave-active { transition: transform 0.3s var(--ease-out), opacity 0.2s ease; }
.spin-enter-from { transform: rotate(-90deg) scale(0.6); opacity: 0; }
.spin-leave-to   { transform: rotate(90deg) scale(0.6); opacity: 0; }

.login-btn {
  padding: 0.45rem 1.1rem; border-radius: 999px; font-size: 0.875rem; font-weight: 600;
  color: #fff; background: linear-gradient(135deg, #2ec4c0, #1e4fa8);
  box-shadow: 0 4px 14px rgba(30, 79, 168, 0.3);
}

/* ── user menu ─────────────────────────────────────────── */
.user { position: relative; }
.user-btn {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 3px 10px 3px 3px; border-radius: 999px; cursor: pointer;
  color: var(--text-muted); font-size: 0.875rem;
  background: var(--surface-1); border: 1px solid var(--border);
  transition: border-color var(--t), color var(--t);
}
.user-btn:hover, .user-btn[aria-expanded="true"] { color: var(--text); border-color: var(--border-strong); }
.user-name { max-width: 8em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.caret { transition: transform var(--t); }
.caret.open { transform: rotate(180deg); }
.avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: grid; place-items: center; font-size: 0.8rem; font-weight: 700; color: #fff;
  background: linear-gradient(135deg, #2ec4c0, #1e4fa8);
}
.avatar-lg { width: 40px; height: 40px; font-size: 1rem; }
.menu {
  position: absolute; right: 0; top: calc(100% + 8px); width: 230px; padding: 6px;
  background: var(--el-bg-color-overlay, #fff); border: 1px solid var(--border-strong);
  border-radius: var(--r-md); box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
  transform-origin: top right;
}
[data-theme="light"] .menu { background: #fff; box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12); }
.menu-head { display: flex; align-items: center; gap: 0.65rem; padding: 0.6rem 0.6rem 0.75rem; margin-bottom: 4px; border-bottom: 1px solid var(--border); }
.menu-name { font-weight: 650; color: var(--text); }
.menu-sub { font-size: 0.75rem; color: var(--text-muted); }
.menu-item {
  display: flex; align-items: center; gap: 0.6rem; width: 100%;
  padding: 0.55rem 0.6rem; border-radius: var(--r-sm); border: none; background: none; cursor: pointer;
  font: inherit; font-size: 0.9rem; color: var(--text-muted); text-align: left;
  transition: background var(--t), color var(--t);
}
.menu-item:hover { background: var(--surface-2); color: var(--text); }
.menu-item.danger:hover { background: rgba(248, 113, 113, 0.12); color: #f87171; }
.menu-enter-active { transition: opacity 0.18s ease, transform 0.26s var(--ease-spring); }
.menu-leave-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.menu-enter-from, .menu-leave-to { opacity: 0; transform: translateY(-6px) scale(0.96); }

/* ── subnav ────────────────────────────────────────────── */
.subnav { border-top: 1px solid var(--border); height: var(--shell-subnav); }
.subnav-inner {
  height: 100%; max-width: 1280px; margin: 0 auto; padding: 0 clamp(1rem, 3vw, 2rem);
  display: flex; align-items: center; gap: 1.25rem;
}
.subnav-title {
  display: inline-flex; align-items: center; gap: 0.5rem;
  font-size: 0.85rem; font-weight: 700; color: var(--text); white-space: nowrap;
}
.subnav-title::before { content: ''; width: 4px; height: 16px; border-radius: 4px; background: var(--section); }
.subnav-tabs { display: flex; gap: 0.25rem; overflow-x: auto; scrollbar-width: none; height: 100%; }
.subnav-tabs::-webkit-scrollbar { display: none; }
.subnav-link {
  position: relative; display: inline-flex; align-items: center; height: 100%;
  padding: 0 0.85rem; font-size: 0.875rem; font-weight: 500; color: var(--text-muted); white-space: nowrap;
  transition: color var(--t);
}
.subnav-link:hover { color: var(--text); }
.subnav-link::after {
  content: ''; position: absolute; left: 0.85rem; right: 0.85rem; bottom: -1px; height: 2px; border-radius: 2px;
  background: var(--section); transform: scaleX(0); transition: transform 0.3s var(--ease-out);
}
.subnav-link.active { color: var(--text); font-weight: 600; }
.subnav-link.active::after { transform: scaleX(1); }

/* ── main ──────────────────────────────────────────────── */
.main { flex: 1; width: 100%; max-width: 1280px; margin: 0 auto; padding: 1.25rem clamp(1rem, 3vw, 2rem) 2rem; }
.main--wide { max-width: none; padding: 0; }
.footer { flex-shrink: 0; }
.tabbar { display: none; }

/* ── mobile ────────────────────────────────────────────── */
@media (max-width: 768px) {
  .header-inner { grid-template-columns: 1fr auto; padding: 0 1rem; }
  .main-nav, .user-name, .caret { display: none; }
  .user-btn { padding: 3px; }
  .subnav-inner { padding: 0 0.5rem 0 1rem; gap: 0.5rem; }
  .subnav-title { display: none; }
  .main { padding: 0.75rem 0.75rem calc(var(--shell-tabbar) + env(safe-area-inset-bottom, 0px) + 1rem); }
  .main--wide { padding: 0 0 calc(var(--shell-tabbar) + env(safe-area-inset-bottom, 0px)); }
  .footer { display: none; }

  .tabbar {
    display: grid; grid-template-columns: repeat(4, 1fr);
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 60;
    height: calc(var(--shell-tabbar) + env(safe-area-inset-bottom, 0px));
    padding-bottom: env(safe-area-inset-bottom, 0px);
    background: var(--surface-nav);
    backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
    border-top: 1px solid var(--border);
  }
  .tab { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; font-size: 0.68rem; font-weight: 500; color: var(--text-subtle); transition: color var(--t); }
  .tab svg { transition: transform 0.3s var(--ease-spring); }
  .tab.active { color: var(--section); }
  .tab.active svg { transform: translateY(-1px) scale(1.1); }
  .tab:active svg { transform: scale(0.88); }
}
</style>
