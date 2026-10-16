<template>
  <div>
    <h1 class="page-title">管理后台</h1>
    <div class="grid grid-auto">
      <div v-for="item in shortcuts" :key="item.label" class="card card-hover" @click="router.push(item.path)">
        <div class="card-body flex-center" style="flex-direction:column;gap:12px;padding:32px">
          <span style="font-size:36px">{{ item.icon }}</span>
          <span style="font-size:15px;font-weight:600;color:var(--c-text)">{{ item.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
const shortcuts = [
  { label: '用户管理', path: '/admin/users', icon: '👥' },
  { label: '科目管理', path: '/admin/subjects', icon: '🗂️' },
]
</script>
