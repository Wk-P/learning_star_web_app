<template>
  <div class="login-wrap">
    <div class="login-card glass">

      <!-- brand -->
      <div class="brand">
        <RouterLink to="/" class="brand-link">
          <span class="mark">한</span>
          <span class="name">韩途</span>
        </RouterLink>
        <span class="back-link-top">
          <RouterLink to="/">← 返回首页</RouterLink>
        </span>
      </div>

      <!-- tab switcher -->
      <div class="tabs">
        <button :class="['tab', { active: mode === 'login' }]" @click="switchMode('login')">登录</button>
        <button :class="['tab', { active: mode === 'register' }]" @click="switchMode('register')">注册</button>
      </div>

      <!-- login form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" type="text" autocomplete="username" placeholder="请输入用户名" required />
        </div>
        <div class="field">
          <label>密码</label>
          <div class="input-wrap">
            <input v-model="password" :type="showPwd ? 'text' : 'password'" autocomplete="current-password" placeholder="请输入密码" required />
            <button type="button" class="eye-btn" @click="showPwd = !showPwd" :aria-label="showPwd ? '隐藏密码' : '显示密码'">
              <svg v-if="showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading" class="spinner" />
          <span v-else>登录</span>
        </button>
        <p class="switch-hint">没有账号？<button type="button" class="text-btn" @click="switchMode('register')">立即注册</button></p>
      </form>

      <!-- register form -->
      <form v-else @submit.prevent="handleRegister">
        <div class="field">
          <label>用户名</label>
          <input v-model="regUsername" type="text" autocomplete="username" placeholder="请输入用户名" required />
        </div>
        <div class="field">
          <label>密码 <span class="hint-inline">（至少 6 位）</span></label>
          <div class="input-wrap">
            <input v-model="regPassword" :type="showRegPwd ? 'text' : 'password'" autocomplete="new-password" placeholder="请设置密码" required />
            <button type="button" class="eye-btn" @click="showRegPwd = !showRegPwd" :aria-label="showRegPwd ? '隐藏密码' : '显示密码'">
              <svg v-if="showRegPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>
        <div class="field">
          <label>确认密码</label>
          <div class="input-wrap">
            <input v-model="regConfirm" :type="showRegConfirm ? 'text' : 'password'" autocomplete="new-password" placeholder="再次输入密码" required />
            <button type="button" class="eye-btn" @click="showRegConfirm = !showRegConfirm" :aria-label="showRegConfirm ? '隐藏密码' : '显示密码'">
              <svg v-if="showRegConfirm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>
        <div class="field">
          <label>邮箱 <span class="hint-inline">（可选）</span></label>
          <input v-model="regEmail" type="email" autocomplete="email" placeholder="your@email.com" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <p v-if="success" class="success-msg">{{ success }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading" class="spinner" />
          <span v-else>注册</span>
        </button>
        <p class="switch-hint">已有账号？<button type="button" class="text-btn" @click="switchMode('login')">直接登录</button></p>
      </form>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api'

const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')

const username = ref('')
const password = ref('')
const showPwd  = ref(false)

const regUsername   = ref('')
const regPassword   = ref('')
const regConfirm    = ref('')
const regEmail      = ref('')
const showRegPwd    = ref(false)
const showRegConfirm = ref(false)

const error   = ref('')
const success = ref('')
const loading = ref(false)

function switchMode(m: 'login' | 'register') {
  mode.value = m
  error.value = ''
  success.value = ''
  showPwd.value = false
  showRegPwd.value = false
  showRegConfirm.value = false
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await api.login(username.value, password.value)
    auth.setTokens(res.access, res.refresh)
    router.push('/user')
  } catch {
    error.value = '用户名或密码错误'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  success.value = ''

  if (regPassword.value !== regConfirm.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (regPassword.value.length < 6) {
    error.value = '密码至少 6 位'
    return
  }

  loading.value = true
  try {
    await api.register(regUsername.value, regPassword.value, regEmail.value || undefined)
    success.value = '注册成功，正在登录…'
    const res = await api.login(regUsername.value, regPassword.value)
    auth.setTokens(res.access, res.refresh)
    router.push('/user')
  } catch (e: unknown) {
    const res = e as Response
    const body = await res.json().catch(() => ({}))
    error.value = body.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2rem 2rem 2.25rem;
  border-radius: var(--r-xl);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* brand row */
.brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  text-decoration: none !important;
}

.mark {
  background: var(--primary);
  color: #000;
  font-weight: 800;
  font-size: 0.85rem;
  padding: 0.22rem 0.42rem;
  border-radius: 6px;
  letter-spacing: 0.05em;
}

.name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}

.back-link-top a {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color var(--t);
}
.back-link-top a:hover { color: var(--primary); text-decoration: none; }

/* tabs */
.tabs {
  display: flex;
  gap: 0;
  background: var(--surface-2);
  border-radius: var(--r-md);
  padding: 3px;
}

.tab {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: calc(var(--r-md) - 2px);
  background: transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--t), color var(--t);
}

.tab.active {
  background: var(--primary);
  color: #000;
  font-weight: 700;
}

/* form */
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label {
  font-size: 0.82rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.hint-inline {
  font-size: 0.75rem;
  color: var(--text-subtle);
}

input {
  background: var(--surface-2);
  border: 1px solid var(--border-strong);
  border-radius: var(--r-md);
  padding: 0.62rem 0.9rem;
  color: var(--text);
  font-size: 0.92rem;
  outline: none;
  transition: border-color var(--t), background var(--t);
  width: 100%;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrap input {
  padding-right: 2.5rem;
}

.eye-btn {
  position: absolute;
  right: 0.7rem;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--text-subtle);
  display: flex;
  align-items: center;
  transition: color var(--t);
  line-height: 0;
}

.eye-btn:hover { color: var(--text-muted); }

.eye-btn svg {
  width: 16px;
  height: 16px;
}

input::placeholder { color: var(--text-subtle); }
input:focus {
  border-color: var(--primary);
  background: var(--surface-3);
}

.error-msg {
  color: #f87171;
  font-size: 0.83rem;
  margin: 0;
}

.success-msg {
  color: var(--primary);
  font-size: 0.83rem;
  margin: 0;
}

.btn-primary {
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: var(--r-md);
  padding: 0.72rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity var(--t);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  margin-top: 0.25rem;
}

.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0,0,0,0.25);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.switch-hint {
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-muted);
  margin: 0;
}

.text-btn {
  background: none;
  border: none;
  color: var(--primary);
  font-size: inherit;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-decoration-color: transparent;
  transition: text-decoration-color var(--t);
}
.text-btn:hover { text-decoration-color: var(--primary); }
</style>
