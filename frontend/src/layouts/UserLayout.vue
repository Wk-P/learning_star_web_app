<template>
  <div class="ul-wrap">
    <header class="ul-header">
      <div class="ul-header-inner">
        <router-link to="/home" class="ul-logo">
          <span>📚</span><span>课程系统</span>
        </router-link>
        <nav class="ul-top-nav">
          <router-link to="/courses" class="ul-top-link ul-hide-xs">课程列表</router-link>
          <router-link to="/home" class="ul-top-link ul-hide-xs">返回主页</router-link>
          <router-link v-if="auth.isAdmin" to="/admin/home" class="ul-top-admin ul-hide-xs">管理后台</router-link>
          <span class="ul-username ul-hide-xs">{{ auth.user?.username }}</span>
          <button class="ul-hamburger ul-show-xs" @click="sidebarOpen = !sidebarOpen">
            <span /><span /><span />
          </button>
        </nav>
      </div>
    </header>

    <div v-if="sidebarOpen" class="ul-overlay ul-show-xs" @click="sidebarOpen = false" />

    <div class="ul-body">
      <aside class="ul-sidebar" :class="{ 'ul-sidebar-open': sidebarOpen }">
        <div class="ul-sidebar-inner">
          <div class="ul-profile-box">
            <div class="ul-profile-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</div>
            <div>
              <div class="ul-profile-name">{{ auth.user?.username }}</div>
              <div class="ul-profile-uid font-mono text-sm text-muted">#{{ auth.user?.userId }}</div>
            </div>
          </div>

          <nav class="ul-nav">
            <router-link to="/user/profile" class="ul-nav-item">
              <span class="ul-nav-icon">👤</span> 个人信息
            </router-link>
          </nav>

          <div class="ul-sidebar-bottom">
            <button class="ul-nav-item ul-btn-full" @click="showPwModal = true">
              <span class="ul-nav-icon">🔒</span> 修改密码
            </button>
            <button class="ul-nav-item ul-btn-full ul-btn-danger" @click="handleLogout">
              <span class="ul-nav-icon">→</span> 退出登录
            </button>
          </div>
        </div>
      </aside>

      <main class="ul-main">
        <RouterView />
      </main>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="showPwModal" class="modal-backdrop" @click.self="showPwModal = false">
      <div class="modal">
        <div class="modal-header">
          <span>修改密码</span>
          <button class="modal-close btn-ghost" @click="showPwModal = false">✕</button>
        </div>
        <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
          <div class="field">
            <label class="field-label">旧密码</label>
            <input v-model="pwForm.old" type="password" class="input" placeholder="请输入旧密码" />
          </div>
          <div class="field">
            <label class="field-label">新密码</label>
            <input v-model="pwForm.new" type="password" class="input" placeholder="至少 6 位" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPwModal = false">取消</button>
          <button class="btn btn-primary" :class="{ loading: pwLoading }" @click="submitPw">确认</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { authApi } from '@/api/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const showPwModal = ref(false)
const pwLoading = ref(false)
const pwForm = ref({ old: '', new: '' })
const sidebarOpen = ref(false)

watch(() => route.name, () => { sidebarOpen.value = false })

async function submitPw() {
  if (!pwForm.value.old || !pwForm.value.new) { toast.warning('请填写完整'); return }
  pwLoading.value = true
  try {
    await authApi.changePassword(pwForm.value.old, pwForm.value.new)
    toast.success('密码修改成功')
    showPwModal.value = false
    pwForm.value = { old: '', new: '' }
  } finally {
    pwLoading.value = false
  }
}

function handleLogout() {
  auth.logout(); router.push('/login')
}
</script>

<style scoped>
.ul-wrap { display: flex; flex-direction: column; min-height: 100vh; }

.ul-header {
  position: sticky; top: 0; z-index: 100;
  background: var(--c-surface); border-bottom: 1px solid var(--c-border);
  box-shadow: var(--shadow-sm);
}
.ul-header-inner {
  max-width: 1400px; margin: 0 auto; padding: 0 20px;
  height: 58px; display: flex; align-items: center; justify-content: space-between;
}
.ul-logo { display: flex; align-items: center; gap: 8px; font-size: 17px; font-weight: 700; color: var(--c-text); }
.ul-logo:hover { color: var(--c-primary); }

.ul-top-nav { display: flex; align-items: center; gap: 6px; }
.ul-top-link { padding: 5px 12px; border-radius: var(--r-sm); color: var(--c-text-2); font-size: 13px; transition: background var(--t); }
.ul-top-link:hover { background: var(--c-info-light); color: var(--c-text); }
.ul-top-admin { padding: 5px 12px; border-radius: var(--r-sm); background: var(--c-primary); color: #fff; font-size: 13px; }
.ul-top-admin:hover { background: var(--c-primary-hover); color: #fff; }
.ul-username { font-size: 13px; color: var(--c-text-2); margin-left: 8px; }

.ul-body { display: flex; flex: 1; overflow: hidden; }

.ul-sidebar {
  width: 220px; flex-shrink: 0;
  background: #1e293b;
  min-height: calc(100vh - 58px);
  display: flex; flex-direction: column;
}
.ul-sidebar-inner { display: flex; flex-direction: column; height: 100%; padding: 16px 12px; }

.ul-profile-box { display: flex; align-items: center; gap: 10px; padding: 12px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.ul-profile-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--c-primary); color: #fff;
  font-size: 14px; font-weight: 700; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.ul-profile-name { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.ul-profile-uid { color: #64748b; margin-top: 2px; }

.ul-nav { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.ul-nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 12px; border-radius: var(--r-sm);
  color: #94a3b8; font-size: 13px; font-weight: 500;
  transition: background var(--t), color var(--t);
  width: 100%; text-align: left;
}
.ul-nav-item:hover, .ul-nav-item.router-link-active {
  background: rgba(99,102,241,0.15); color: #e2e8f0;
}
.ul-nav-icon { font-size: 15px; flex-shrink: 0; }

.ul-sidebar-bottom { margin-top: auto; display: flex; flex-direction: column; gap: 2px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); }
.ul-btn-full { justify-content: flex-start; }
.ul-btn-danger { color: #f87171 !important; }
.ul-btn-danger:hover { background: rgba(239,68,68,0.12) !important; }

.ul-main { flex: 1; padding: 24px; background: var(--c-bg); overflow-y: auto; min-width: 0; }

.ul-hamburger {
  display: flex; flex-direction: column; justify-content: center; gap: 5px;
  width: 36px; height: 36px; padding: 6px; border-radius: var(--r-sm);
  background: transparent; cursor: pointer;
}
.ul-hamburger span { display: block; width: 100%; height: 2px; background: var(--c-text-2); border-radius: 2px; }

.ul-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 200; }

.ul-show-xs { display: none; }
.ul-hide-xs { display: flex; }

@media (max-width: 768px) {
  .ul-show-xs { display: flex; }
  .ul-hide-xs { display: none !important; }
  .ul-header-inner { padding: 0 16px; }
  .ul-sidebar {
    position: fixed; left: -240px; top: 58px; bottom: 0;
    width: 240px; z-index: 210;
    transition: left 0.25s ease;
    min-height: unset; overflow-y: auto;
  }
  .ul-sidebar-open { left: 0; }
  .ul-main { padding: 16px; }
}

@media (max-width: 480px) {
  .ul-main { padding: 12px; }
}
</style>
