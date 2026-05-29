<template>
  <div class="tl-wrap">
    <header class="tl-header">
      <div class="tl-header-inner">
        <span class="tl-logo">🎓 教师工作台</span>
        <nav class="tl-nav">
          <router-link to="/teacher/home" class="tl-nav-link tl-hide-xs">我的课程</router-link>
          <span class="tl-user tl-hide-xs">{{ auth.user?.username }}</span>
          <button class="tl-pw-btn tl-hide-xs" @click="showPwModal = true">修改密码</button>
          <button class="tl-logout" @click="handleLogout">退出</button>
          <button class="tl-hamburger tl-show-xs" @click="mobileNavOpen = !mobileNavOpen">
            <span /><span /><span />
          </button>
        </nav>
      </div>
      <!-- 移动端下拉导航 -->
      <nav v-if="mobileNavOpen" class="tl-nav-mobile tl-show-xs" @click="mobileNavOpen = false">
        <router-link to="/teacher/home" class="tl-nav-link-m">我的课程</router-link>
        <button class="tl-nav-link-m" style="text-align:left;width:100%;cursor:pointer" @click.stop="showPwModal = true; mobileNavOpen = false">修改密码</button>
        <div class="tl-nav-link-m" style="color:#64748b;font-size:12px;pointer-events:none">
          {{ auth.user?.username }}
        </div>
      </nav>
    </header>

  <!-- 修改密码弹窗 -->
  <Teleport to="body">
    <div v-if="showPwModal" class="modal-backdrop" @click.self="showPwModal = false">
      <div class="modal" style="max-width:400px">
        <div class="modal-header">
          <span>修改密码</span>
          <button class="modal-close" @click="showPwModal = false">✕</button>
        </div>
        <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
          <div class="field"><label class="field-label">旧密码</label><input v-model="pwForm.old" type="password" class="input" placeholder="请输入旧密码" /></div>
          <div class="field"><label class="field-label">新密码</label><input v-model="pwForm.new" type="password" class="input" placeholder="至少 6 位" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPwModal = false">取消</button>
          <button class="btn btn-primary" :class="{ loading: pwLoading }" @click="submitPw">确认</button>
        </div>
      </div>
    </div>
  </Teleport>

    <main class="tl-main">
      <nav v-if="breadcrumbs.length > 0" class="breadcrumb" style="margin-bottom:16px">
        <router-link to="/teacher/home">工作台</router-link>
        <template v-for="(c, i) in breadcrumbs" :key="c.label">
          <span class="breadcrumb-sep">/</span>
          <router-link v-if="c.path" :to="c.path">{{ c.label }}</router-link>
          <span v-else class="breadcrumb-current">{{ c.label }}</span>
        </template>
      </nav>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { useToast } from '@/composables/useToast'
import { authApi } from '@/api/auth'

const auth = useAuthStore()
const enrollment = useEnrollmentStore()
const route = useRoute()
const router = useRouter()
const { segments, clearSegments } = useBreadcrumb()
const mobileNavOpen = ref(false)
const toast = useToast()
const showPwModal = ref(false)
const pwLoading = ref(false)
const pwForm = ref({ old: '', new: '' })

watch(() => route.name, () => { clearSegments(); mobileNavOpen.value = false })

function handleLogout() {
  auth.logout()
  enrollment.reset()
  router.push('/login')
}

async function submitPw() {
  if (!pwForm.value.old || !pwForm.value.new) { toast.warning('请填写完整'); return }
  pwLoading.value = true
  try {
    await authApi.changePassword(pwForm.value.old, pwForm.value.new)
    toast.success('密码修改成功')
    showPwModal.value = false
    pwForm.value = { old: '', new: '' }
  } catch {
    toast.error('旧密码错误或修改失败')
  } finally {
    pwLoading.value = false
  }
}

const breadcrumbs = computed(() => {
  const name = route.name as string
  if (!name || name === 'teacher-home') return []
  if (segments.value.length > 0) return segments.value
  return []
})
</script>

<style scoped>
.tl-wrap { display: flex; flex-direction: column; min-height: 100vh; }

.tl-header {
  background: #1a1a2e; position: sticky; top: 0; z-index: 100;
}
.tl-header-inner {
  max-width: 1200px; margin: 0 auto; padding: 0 24px;
  height: 58px; display: flex; align-items: center; justify-content: space-between;
}
.tl-logo { font-size: 16px; font-weight: 700; color: #e2e8f0; letter-spacing: 0.5px; }

.tl-nav { display: flex; align-items: center; gap: 8px; }
.tl-nav-link {
  padding: 6px 14px; border-radius: var(--r-sm);
  color: #94a3b8; font-size: 13px; font-weight: 500;
  transition: background var(--t), color var(--t);
}
.tl-nav-link:hover, .tl-nav-link.router-link-active { color: #e2e8f0; background: rgba(255,255,255,0.08); }
.tl-front { color: #818cf8 !important; }
.tl-front:hover { background: rgba(99,102,241,0.15) !important; color: #a5b4fc !important; }

.tl-user { font-size: 13px; color: #64748b; margin-left: 8px; }
.tl-pw-btn {
  padding: 5px 12px; border-radius: var(--r-sm);
  color: #94a3b8; font-size: 13px; font-weight: 500;
  transition: background var(--t), color var(--t);
}
.tl-pw-btn:hover { color: #e2e8f0; background: rgba(255,255,255,0.08); }

.tl-logout {
  padding: 5px 12px; border-radius: var(--r-sm);
  color: #f87171; font-size: 13px; font-weight: 500;
  transition: background var(--t);
}
.tl-logout:hover { background: rgba(239,68,68,0.12); }

.tl-main { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 24px; }

/* ── 汉堡 ──────────────────────────────────────────────── */
.tl-hamburger {
  display: flex; flex-direction: column; justify-content: center; gap: 5px;
  width: 36px; height: 36px; padding: 6px; border-radius: var(--r-sm);
  background: transparent; cursor: pointer; margin-left: 4px;
}
.tl-hamburger span { display: block; width: 100%; height: 2px; background: #94a3b8; border-radius: 2px; }

.tl-nav-mobile {
  display: flex; flex-direction: column;
  background: #1a1a2e; border-top: 1px solid rgba(255,255,255,0.08);
  padding: 8px 0;
}
.tl-nav-link-m {
  display: block; padding: 11px 20px;
  color: #94a3b8; font-size: 14px;
  transition: background var(--t), color var(--t);
}
.tl-nav-link-m:hover, .tl-nav-link-m.router-link-active { background: rgba(255,255,255,0.06); color: #e2e8f0; }

/* ── 响应式 ─────────────────────────────────────────────── */
.tl-show-xs { display: none; }
.tl-hide-xs { display: inline-flex; }

@media (max-width: 768px) {
  .tl-show-xs { display: flex; }
  .tl-hide-xs { display: none !important; }
  .tl-header-inner { padding: 0 16px; }
  .tl-main { padding: 16px; }
}

@media (max-width: 480px) {
  .tl-main { padding: 12px; }
}
</style>
