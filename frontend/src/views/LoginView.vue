<template>
  <div class="login-page">
    <div class="login-box">
      <div class="login-left">
        <div class="brand-icon">📚</div>
        <h1 class="brand-name">课程管理系统</h1>
        <p class="brand-desc">在线学习 · 视频课程 · 科目分类</p>
      </div>
      <div class="login-right">
        <h2 class="form-title">欢迎登录</h2>
        <form class="form" @submit.prevent="handleLogin">
          <div class="field">
            <label class="field-label">用户名</label>
            <input v-model="form.username" class="input" placeholder="请输入用户名" autocomplete="username" />
          </div>
          <div class="field">
            <label class="field-label">密码</label>
            <input v-model="form.password" type="password" class="input" placeholder="请输入密码" autocomplete="current-password" />
          </div>
          <button type="submit" class="btn btn-primary btn-lg login-btn" :class="{ loading }">
            {{ loading ? '' : '登 录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()

const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    toast.warning('请输入用户名和密码'); return
  }
  loading.value = true
  try {
    await auth.login(form.value)
    const defaultRedirect = auth.isAdmin ? '/admin/home' : '/home'
    const redirect = (route.query.redirect as string) || defaultRedirect
    router.push(redirect)
  } catch {
    toast.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #1e3a5f 100%);
}

.login-box {
  display: flex; width: 820px; min-height: 460px;
  border-radius: var(--r-xl); overflow: hidden;
  box-shadow: 0 32px 80px rgba(0,0,0,0.5);
}

.login-left {
  flex: 1; padding: 48px;
  background: linear-gradient(145deg, #6366f1, #4f46e5);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center; gap: 16px;
}
.brand-icon { font-size: 60px; filter: drop-shadow(0 4px 16px rgba(0,0,0,0.25)); }
.brand-name { font-size: 26px; font-weight: 700; color: #fff; letter-spacing: 1px; }
.brand-desc  { font-size: 14px; color: rgba(255,255,255,0.75); letter-spacing: 3px; line-height: 2; }

.login-right {
  width: 360px; flex-shrink: 0;
  background: var(--c-surface);
  padding: 48px 40px;
  display: flex; flex-direction: column; justify-content: center;
}
.form-title { font-size: 22px; font-weight: 700; color: var(--c-text); margin-bottom: 28px; text-align: center; }
.form { display: flex; flex-direction: column; gap: 16px; }
.login-btn { width: 100%; margin-top: 8px; font-size: 15px; letter-spacing: 2px; }

@media (max-width: 640px) {
  .login-box { flex-direction: column; width: 95vw; min-height: unset; }
  .login-left { padding: 32px; }
  .brand-icon { font-size: 40px; }
  .brand-name { font-size: 20px; }
  .login-right { width: 100%; padding: 32px 24px; }
}
</style>
