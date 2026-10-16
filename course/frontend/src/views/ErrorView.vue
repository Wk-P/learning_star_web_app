<template>
  <div class="flex-center" style="min-height:100vh;flex-direction:column;gap:20px">
    <div style="font-size:64px">⚠️</div>
    <h2 style="font-size:20px;color:var(--c-text)">页面出错了</h2>
    <p style="color:var(--c-text-3)">访问的页面不存在或权限不足</p>
    <button class="btn btn-primary" @click="router.push('/home')">返回首页</button>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
