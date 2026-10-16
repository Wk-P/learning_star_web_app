<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-header">
        <span class="login-logo">Player3</span>
        <h2 class="login-title">管理员登录</h2>
      </div>

      <form class="login-form" @submit.prevent="submit">
        <div class="field">
          <label class="field-label">用户名</label>
          <input
            v-model="form.username"
            type="text"
            class="field-input"
            autocomplete="username"
            placeholder="请输入用户名"
          />
        </div>
        <div class="field">
          <label class="field-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="field-input"
            autocomplete="current-password"
            placeholder="请输入密码"
          />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner" />
          {{ loading ? '登录中…' : '登 录' }}
        </button>
        <p v-if="errMsg" class="err-msg">{{ errMsg }}</p>
      </form>

      <div class="login-footer">
        <RouterLink :to="{ name: 'home' }" class="back-link">← 返回首页</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const errMsg = ref('')
const form = reactive({ username: '', password: '' })

async function submit() {
  if (!form.username || !form.password) {
    errMsg.value = '请填写用户名和密码'
    return
  }
  loading.value = true
  errMsg.value = ''
  try {
    const { access, refresh } = await api.login(form.username, form.password)
    auth.setTokens(access, refresh)
    router.push('/admin/dashboard')
  } catch {
    errMsg.value = '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* always dark, independent of user theme */
.login-wrap {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background-color: #07090e;
  background-image:
    radial-gradient(ellipse 80% 55% at 12% -8%,  rgba(45, 212, 191, 0.11) 0%, transparent 60%),
    radial-gradient(ellipse 55% 45% at 90% 110%, rgba(129, 140, 248, 0.08) 0%, transparent 55%);
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 1.25rem;
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  overflow: hidden;
}

.login-header {
  padding: 2rem 2rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.login-logo {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #2dd4bf;
}

.login-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: -0.02em;
}

.login-form {
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: #8892a4;
}

.field-input {
  width: 100%;
  padding: 0.6rem 0.85rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 0.625rem;
  color: #e2e8f0;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.18s ease, background 0.18s ease;
}

.field-input::placeholder { color: #4a5568; }

.field-input:focus {
  border-color: rgba(45, 212, 191, 0.45);
  background: rgba(255, 255, 255, 0.09);
}

.submit-btn {
  margin-top: 0.5rem;
  width: 100%;
  padding: 0.7rem;
  border-radius: 0.625rem;
  border: none;
  background: #2dd4bf;
  color: #07090e;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: opacity 0.18s ease, transform 0.18s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(7, 9, 14, 0.3);
  border-top-color: #07090e;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.err-msg {
  font-size: 0.8rem;
  color: #f87171;
  text-align: center;
  margin-top: -0.25rem;
}

.login-footer {
  padding: 1rem 2rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  text-align: center;
}

.back-link {
  font-size: 0.82rem;
  color: #8892a4;
  text-decoration: none;
  transition: color 0.18s ease;
}

.back-link:hover { color: #2dd4bf; }

@media (max-width: 480px) {
  .login-card { border-radius: 1rem; }
  .login-header, .login-form, .login-footer { padding-left: 1.25rem; padding-right: 1.25rem; }
}
</style>
