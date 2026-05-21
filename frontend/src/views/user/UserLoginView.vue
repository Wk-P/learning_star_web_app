<template>
  <div class="login-wrap">
    <div class="login-card glass">
      <div class="brand">
        <span class="mark">P3</span>
        <span class="name">Player3</span>
      </div>
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" type="text" autocomplete="username" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          <span v-if="loading" class="spinner" />
          <span v-else>登录</span>
        </button>
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

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

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
</script>

<style scoped>
.login-wrap {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 380px;
  padding: 2.5rem 2rem;
  border-radius: var(--r-xl);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.mark {
  background: var(--primary);
  color: #000;
  font-weight: 800;
  font-size: 0.9rem;
  padding: 0.25rem 0.45rem;
  border-radius: 6px;
  letter-spacing: 0.05em;
}

.name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

label {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

input {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 0.65rem 0.9rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  outline: none;
  transition: border-color var(--t) var(--ease);
}

input:focus {
  border-color: var(--primary);
}

.error-msg {
  color: #f87171;
  font-size: 0.85rem;
  margin: 0;
}

.btn-primary {
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: var(--r-md);
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity var(--t) var(--ease);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0,0,0,0.3);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
