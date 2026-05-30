<template>
  <div class="al-wrap">
    <header class="al-header">
      <div class="al-header-inner">
        <div class="al-left">
          <span class="al-logo">⚙ 管理后台</span>
          <nav class="al-nav al-nav-desktop">
            <router-link v-if="auth.isAdmin" to="/admin/users" class="al-nav-link">用户管理</router-link>
            <router-link to="/admin/subjects" class="al-nav-link">科目管理</router-link>
            <router-link to="/admin/courses" class="al-nav-link">课程管理</router-link>
            <router-link to="/admin/homework" class="al-nav-link">作业管理</router-link>
          </nav>
        </div>
        <div class="al-right">
          <span class="al-role-badge al-hide-xs">{{ auth.isAdmin ? 'Admin' : 'Teacher' }}</span>
          <span class="al-username al-hide-xs">{{ auth.user?.username }}</span>
          <button class="al-pw-btn al-hide-xs" @click="showPwModal = true">修改密码</button>
          <button class="al-logout" @click="handleLogout">退出</button>
          <button class="al-hamburger al-show-xs" @click="mobileNavOpen = !mobileNavOpen">
            <span /><span /><span />
          </button>
        </div>
      </div>
    </header>

  <!-- 移动端侧边抽屉 -->
  <Teleport to="body">
    <Transition name="al-drawer">
      <div v-if="mobileNavOpen" class="al-drawer-backdrop" @click="mobileNavOpen = false">
        <nav class="al-drawer" @click.stop>
          <div class="al-drawer-user">
            <span class="al-role-badge" style="font-size:12px">{{ auth.isAdmin ? 'Admin' : 'Teacher' }}</span>
            <span style="font-size:14px;color:#f8fafc;font-weight:600">{{ auth.user?.username }}</span>
          </div>
          <router-link v-if="auth.isAdmin" to="/admin/users" class="al-nav-link-m">用户管理</router-link>
          <router-link to="/admin/subjects" class="al-nav-link-m">科目管理</router-link>
          <router-link to="/admin/courses" class="al-nav-link-m">课程管理</router-link>
          <router-link to="/admin/homework" class="al-nav-link-m">作业管理</router-link>
          <div style="flex:1" />
          <button class="al-nav-link-m" style="text-align:left;width:100%;cursor:pointer;color:#94a3b8"
            @click="showPwModal = true; mobileNavOpen = false">修改密码</button>
          <button class="al-nav-link-m" style="text-align:left;width:100%;cursor:pointer;color:#f87171"
            @click="handleLogout">退出登录</button>
        </nav>
      </div>
    </Transition>
  </Teleport>

  <!-- 修改密码弹窗 -->
  <Teleport to="body">
    <div v-if="showPwModal" class="modal-backdrop" @click.self="showPwModal = false">
      <div class="modal" style="max-width:400px">
        <div class="modal-header">
          <span>账户设置</span>
          <button class="modal-close" @click="showPwModal = false">✕</button>
        </div>
        <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
          <div v-if="!auth.isAdmin" class="field">
            <label class="field-label">修改用户名</label>
            <input v-model="unForm.username" class="input" :placeholder="auth.user?.username ?? '新用户名'" maxlength="50" />
          </div>
          <div v-if="!auth.isAdmin" style="border-top:1px solid var(--c-border);margin:4px 0" />
          <div class="field"><label class="field-label">旧密码</label><input v-model="pwForm.old" type="password" class="input" placeholder="请输入旧密码" /></div>
          <div class="field"><label class="field-label">新密码</label><input v-model="pwForm.new" type="password" class="input" placeholder="至少 6 位" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPwModal = false">取消</button>
          <button v-if="!auth.isAdmin && unForm.username" class="btn btn-secondary" :class="{ loading: unLoading }" @click="submitUsername">改用户名</button>
          <button class="btn btn-primary" :class="{ loading: pwLoading }" @click="submitPw">改密码</button>
        </div>
      </div>
    </div>
  </Teleport>

    <main class="al-main">
      <nav v-if="breadcrumbs.length > 0" class="breadcrumb">
        <router-link :to="auth.isAdmin ? '/admin/home' : '/admin/courses'">{{ auth.isAdmin ? '管理首页' : '课程管理' }}</router-link>
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
import { authApi, updateUsername } from '@/api/auth'

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
const unLoading = ref(false)
const unForm = ref({ username: '' })

watch(() => route.name, () => { clearSegments(); mobileNavOpen.value = false })

function handleLogout() {
  auth.logout(); enrollment.reset(); router.push('/login')
}

async function submitUsername() {
  const val = unForm.value.username.trim()
  if (!val) return
  unLoading.value = true
  try {
    await updateUsername(val)
    await auth.fetchMe()
    unForm.value.username = ''
    toast.success('用户名已更新')
  } catch {
    toast.error('修改失败，用户名可能已被占用')
  } finally {
    unLoading.value = false
  }
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

const LABELS: Record<string, string> = {
  'admin-subjects': '科目管理',
  'admin-users': '用户管理', 'admin-user-courses': '用户课程',
  'admin-user-course': '课程详情', 'admin-user-class': '课节详情',
  'admin-user-homework-list': '用户作业', 'admin-user-homework': '作业详情',
  'admin-courses': '课程管理', 'admin-course-classes': '课节列表', 'admin-class': '课节编辑',
  'admin-homework-list': '作业管理', 'admin-homework': '作业详情',
}

const breadcrumbs = computed(() => {
  const name = route.name as string
  if (!name || name === 'admin-home') return []
  if (segments.value.length > 0) return segments.value
  return [{ label: LABELS[name] ?? name, path: '' }]
})
</script>

<style scoped>
.al-wrap { display: flex; flex-direction: column; min-height: 100vh; }

.al-header { background: #0f172a; position: sticky; top: 0; z-index: 100; }
.al-header-inner {
  max-width: 1400px; margin: 0 auto; padding: 0 24px;
  height: 58px; display: flex; align-items: center; justify-content: space-between;
}
.al-logo { font-size: 16px; font-weight: 700; color: #f8fafc; margin-right: 24px; letter-spacing: 0.5px; white-space: nowrap; flex-shrink: 0; }

.al-left { display: flex; align-items: center; gap: 6px; min-width: 0; overflow: hidden; }
.al-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }

.al-nav { display: flex; gap: 2px; }
.al-nav-link {
  padding: 6px 14px; border-radius: var(--r-sm);
  color: #94a3b8; font-size: 13px; font-weight: 500;
  white-space: nowrap;
  transition: background var(--t), color var(--t);
}
.al-nav-link:hover { color: #f8fafc; background: rgba(255,255,255,0.08); }
.al-nav-link.router-link-active { color: #818cf8; background: rgba(99,102,241,0.15); }

.al-role-badge {
  padding: 2px 8px; border-radius: var(--r-full);
  background: rgba(99,102,241,0.25); color: #818cf8;
  font-size: 11px; font-weight: 600;
}
.al-username { font-size: 13px; color: #94a3b8; margin-left: 4px; }
.al-front-link { padding: 5px 12px; border-radius: var(--r-sm); color: #64748b; font-size: 13px; transition: color var(--t); margin-left: 8px; }
.al-front-link:hover { color: #94a3b8; }
.al-pw-btn {
  padding: 5px 12px; border-radius: var(--r-sm);
  color: #94a3b8; font-size: 13px; font-weight: 500;
  transition: background var(--t), color var(--t);
}
.al-pw-btn:hover { color: #f8fafc; background: rgba(255,255,255,0.08); }

.al-logout {
  padding: 5px 12px; border-radius: var(--r-sm);
  color: #f87171; font-size: 13px; font-weight: 500;
  transition: background var(--t);
}
.al-logout:hover { background: rgba(239,68,68,0.12); }

.al-main { flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 24px; }

/* ── 汉堡 ──────────────────────────────────────────────── */
.al-hamburger {
  display: flex; flex-direction: column; justify-content: center; gap: 5px;
  width: 36px; height: 36px; padding: 6px; border-radius: var(--r-sm);
  background: transparent; cursor: pointer; margin-left: 4px;
}
.al-hamburger span { display: block; width: 100%; height: 2px; background: #94a3b8; border-radius: 2px; }

/* ── 侧边抽屉 ───────────────────────────────────────────── */
.al-drawer-backdrop {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0, 0, 0, 0.55);
}
.al-drawer {
  position: absolute; top: 0; left: 0;
  width: 260px; height: 100%;
  background: #0f172a;
  display: flex; flex-direction: column;
  padding-top: 8px; padding-bottom: 16px;
  overflow-y: auto;
  box-shadow: 4px 0 24px rgba(0,0,0,0.4);
}
.al-drawer-user {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 8px;
}
.al-nav-link-m {
  display: block; padding: 12px 20px;
  color: #94a3b8; font-size: 14px;
  transition: background var(--t), color var(--t);
  border: none; background: transparent;
}
.al-nav-link-m:hover, .al-nav-link-m.router-link-active {
  background: rgba(255,255,255,0.06); color: #f8fafc;
}

/* 抽屉动画 */
.al-drawer-enter-active { transition: opacity 0.22s ease; }
.al-drawer-leave-active { transition: opacity 0.18s ease; }
.al-drawer-enter-from, .al-drawer-leave-to { opacity: 0; }
.al-drawer-enter-active .al-drawer { transition: transform 0.22s ease; }
.al-drawer-leave-active .al-drawer { transition: transform 0.18s ease; }
.al-drawer-enter-from .al-drawer, .al-drawer-leave-to .al-drawer { transform: translateX(-100%); }

/* ── 响应式 ─────────────────────────────────────────────── */
.al-show-xs { display: none; }
.al-hide-xs { display: inline-flex; }
.al-username, .al-role-badge, .al-pw-btn { white-space: nowrap; }

@media (max-width: 900px) {
  .al-show-xs { display: flex; }
  .al-hide-xs { display: none !important; }
  .al-nav-desktop { display: none; }
  .al-header-inner { padding: 0 16px; }
  .al-main { padding: 16px; }
}

@media (max-width: 480px) {
  .al-main { padding: 12px; }
}
</style>
