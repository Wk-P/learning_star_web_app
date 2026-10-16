<template>
  <div class="account-view">

    <!-- profile card -->
    <section class="card profile-card">
      <div class="avatar">{{ initial }}</div>
      <div class="profile-info">
        <span class="profile-name">{{ username }}</span>
        <div class="profile-meta">
          <span class="profile-role" :class="auth.isAdmin ? 'role-admin' : 'role-user'">
            {{ auth.isAdmin ? '管理员账户' : '普通用户' }}
          </span>
        </div>
      </div>
      <button class="logout-btn" @click="logout">退出登录</button>
    </section>

    <!-- permissions -->
    <section class="card">
      <h2 class="section-title">我的访问权限</h2>
      <div v-if="loadingPerms" class="hint">加载中…</div>
      <template v-else>
        <div v-for="tab in permTabs" :key="tab.key" class="perm-group">
          <div class="perm-label">
            <span class="perm-icon">{{ tab.icon }}</span>
            {{ tab.label }}
            <span class="perm-count" :class="{ active: perms[tab.key].length > 0 }">
              {{ perms[tab.key].length }}
            </span>
          </div>
          <div v-if="perms[tab.key].length === 0" class="perm-empty">暂无权限</div>
          <ul v-else class="perm-list">
            <li v-for="p in perms[tab.key]" :key="p" class="perm-chip">{{ p }}</li>
          </ul>
        </div>
      </template>
    </section>

    <!-- change password -->
    <section class="card">
      <h2 class="section-title">修改密码</h2>
      <div class="form">
        <label class="field">
          <span class="field-label">原密码</span>
          <input
            v-model="pwd.old"
            type="password"
            class="field-input"
            placeholder="输入当前密码"
            autocomplete="current-password"
          />
        </label>
        <label class="field">
          <span class="field-label">新密码</span>
          <input
            v-model="pwd.new1"
            type="password"
            class="field-input"
            placeholder="至少 6 位"
            autocomplete="new-password"
          />
        </label>
        <label class="field">
          <span class="field-label">确认新密码</span>
          <input
            v-model="pwd.new2"
            type="password"
            class="field-input"
            placeholder="再次输入新密码"
            autocomplete="new-password"
          />
        </label>
        <p v-if="pwdError" class="msg msg--error">{{ pwdError }}</p>
        <p v-if="pwdOk" class="msg msg--ok">{{ pwdOk }}</p>
        <button class="btn-save" :disabled="saving" @click="handleChangePassword">
          {{ saving ? '提交中…' : '修改密码' }}
        </button>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { api } from '@/api'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.clearTokens()
  router.push('/login')
}

const username = ref(auth.username)
const initial = computed(() => (username.value || '?').charAt(0).toUpperCase())

const permTabs = [
  { key: 'video' as const, label: '视频', icon: '▶' },
  { key: 'audio' as const, label: '音频', icon: '♫' },
  { key: 'pdf'   as const, label: '文件', icon: '↓' },
]

const perms = reactive({ video: [] as string[], audio: [] as string[], pdf: [] as string[] })
const loadingPerms = ref(true)

onMounted(async () => {
  try {
    const [me, data] = await Promise.all([
      api.getMe(),
      api.getMyPermissions(),
    ])
    username.value = me.username
    perms.video = data.video
    perms.audio = data.audio
    perms.pdf   = data.pdf
  } finally {
    loadingPerms.value = false
  }
})

const pwd = reactive({ old: '', new1: '', new2: '' })
const saving = ref(false)
const pwdError = ref('')
const pwdOk = ref('')

async function handleChangePassword() {
  pwdError.value = ''
  pwdOk.value = ''
  if (!pwd.old || !pwd.new1 || !pwd.new2) {
    pwdError.value = '请填写所有字段'
    return
  }
  if (pwd.new1 !== pwd.new2) {
    pwdError.value = '两次密码不一致'
    return
  }
  if (pwd.new1.length < 6) {
    pwdError.value = '新密码至少 6 位'
    return
  }
  saving.value = true
  try {
    const res = await api.changePassword(pwd.old, pwd.new1)
    pwdOk.value = res.detail
    pwd.old = ''
    pwd.new1 = ''
    pwd.new2 = ''
  } catch (e: unknown) {
    const body = await (e as Response).json().catch(() => ({}))
    pwdError.value = body.detail || '修改失败，请重试'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.account-view {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-top: 1.5rem;
}

.card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.25rem 1.5rem;
}

/* ── profile ── */
.profile-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--primary-dim);
  border: 2px solid var(--border-primary);
  color: var(--primary);
  font-size: 1.4rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.profile-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-role {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
}

.role-user  { background: var(--primary-dim);              color: var(--primary); }
.role-admin { background: rgba(245, 158, 11, 0.12); color: #f59e0b; }

/* ── section title ── */
.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-subtle);
  margin-bottom: 1rem;
}

/* ── permissions ── */
.perm-group {
  margin-bottom: 1rem;
}

.perm-group:last-child { margin-bottom: 0; }

.perm-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.perm-icon { opacity: 0.7; }

.perm-count {
  font-size: 0.7rem;
  padding: 0.05rem 0.4rem;
  border-radius: 999px;
  background: var(--surface-2);
  color: var(--text-subtle);
  font-weight: 700;
}

.perm-count.active {
  background: var(--primary-dim);
  color: var(--primary);
}

.perm-empty {
  font-size: 0.82rem;
  color: var(--text-subtle);
  padding-left: 0.1rem;
}

.perm-list {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.perm-chip {
  font-size: 0.8rem;
  padding: 0.25rem 0.7rem;
  border-radius: var(--r-xl);
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-muted);
}

/* ── password form ── */
.form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  max-width: 400px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 500;
}

.field-input {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 0.55rem 0.85rem;
  color: var(--text);
  font-size: 1rem;
  outline: none;
  transition: border-color var(--t);
}

.field-input:focus { border-color: var(--primary); }
.field-input::placeholder { color: var(--text-subtle); }

.msg { font-size: 0.82rem; margin: 0; }
.msg--error { color: #f87171; }
.msg--ok    { color: var(--primary); }

.btn-save {
  align-self: flex-start;
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: var(--r-md);
  padding: 0.55rem 1.4rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity var(--t);
}

.btn-save:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-save:hover:not(:disabled) { opacity: 0.85; }

.hint { font-size: 0.875rem; color: var(--text-muted); }

.logout-btn {
  margin-left: auto;
  padding: 0.45rem 1rem;
  border-radius: var(--r-xl);
  border: 1px solid rgba(248, 113, 113, 0.35);
  background: transparent;
  color: #f87171;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--t);
  white-space: nowrap;
  flex-shrink: 0;
}

.logout-btn:hover {
  background: rgba(248, 113, 113, 0.1);
  border-color: #f87171;
}
</style>
