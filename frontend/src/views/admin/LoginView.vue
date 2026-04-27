<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <template #header>管理员登录</template>
      <el-form :model="form" @submit.prevent="submit" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width:100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
          <RouterLink :to="{ name: 'home'}" class="link">回首页</RouterLink>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function submit() {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const { access, refresh } = await api.login(form.username, form.password)
    auth.setTokens(access, refresh)
    router.push('/admin/dashboard')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100dvw;
  background: #f0f2f5;
}

@media (max-width: 768px) {
  .login-card {
    width: 100dvw;
    overflow-x: hidden;
  }
}

.login-card {
  width: 380px;
}

@media (max-width: 768px) {
  .login-card {
    width: 90%;
  }
}

.link {
  width: 100%;
  display: block;
  color: #555;
  text-align: center;
  margin: 0;
  padding: 0;
}

.link:hover {
  color: #3eff;
}
</style>
