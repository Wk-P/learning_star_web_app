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

    <!-- display name -->
    <section class="card">
      <h2 class="section-title">显示名称</h2>
      <div class="form">
        <label class="field">
          <span class="field-label">其他人看到的名字（可留空）</span>
          <input v-model="displayName" class="field-input" maxlength="50" placeholder="例如：小明" />
        </label>
        <p v-if="nameMsg" class="msg" :class="nameOk ? 'msg--ok' : 'msg--error'">{{ nameMsg }}</p>
        <button class="btn-save" :disabled="savingName" @click="saveDisplayName">{{ savingName ? '保存中…' : '保存' }}</button>
      </div>
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
import AppIcon from '@/core/components/AppIcon.vue'
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/core/stores/auth'
import { useRouter } from 'vue-router'
import { accountsApi } from '@/core/api/accounts'
import { errorDetail } from '@/core/api/http'
import { useLanguageStore } from '@/language/stores/languages'

const auth = useAuthStore()
const router = useRouter()
const languages = useLanguageStore()

function logout() {
  auth.clearTokens()
  languages.clear()
  router.push({ name: 'login' })
}

const username = ref(auth.username)
const initial = computed(() => (username.value || '?').charAt(0).toUpperCase())

const displayName = ref('')
const savingName = ref(false)
const nameMsg = ref('')
const nameOk = ref(false)

async function saveDisplayName() {
  savingName.value = true
  nameMsg.value = ''
  try {
    const me = await accountsApi.updateMe({ display_name: displayName.value.trim() })
    displayName.value = me.display_name
    nameOk.value = true
    nameMsg.value = '已保存'
  } catch (e) {
    nameOk.value = false
    nameMsg.value = await errorDetail(e, '保存失败，请重试')
  } finally {
    savingName.value = false
  }
}

onMounted(async () => {
  try {
    const me = await accountsApi.me()
    username.value = me.username
    displayName.value = me.display_name
  } catch {
    // 读取失败时保留登录信息里的用户名
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
    const res = await accountsApi.changePassword(pwd.old, pwd.new1)
    pwdOk.value = res.detail
    pwd.old = ''
    pwd.new1 = ''
    pwd.new2 = ''
  } catch (e: unknown) {
    pwdError.value = await errorDetail(e, '修改失败，请重试')
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
