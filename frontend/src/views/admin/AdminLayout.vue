<template>
  <el-container style="height: 100vh">
    <el-aside width="200px">
      <div class="logo">Player3 Admin</div>
      <el-menu :router="true" :default-active="route.path" background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>概览</span>
        </el-menu-item>
        <el-menu-item index="/admin/video">
          <el-icon><VideoPlay /></el-icon>
          <span>视频</span>
        </el-menu-item>
        <el-menu-item index="/admin/audio">
          <el-icon><Headset /></el-icon>
          <span>音频</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-right">
          <el-button link @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { DataBoard, VideoPlay, Headset } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.clearTokens()
  router.push('/admin/login')
}
</script>

<style scoped>
.el-aside {
  background: #304156;
  display: flex;
  flex-direction: column;
}
.logo {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  padding: 20px 16px;
  border-bottom: 1px solid #405165;
}
.el-menu {
  border-right: none;
  flex: 1;
}
.el-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid #eee;
}
</style>
