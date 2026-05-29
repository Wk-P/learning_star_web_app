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
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const router = useRouter(); const auth = useAuthStore()
const shortcuts = computed(() => {
  const base = [
    { label: '课程管理', path: '/admin/courses', icon: '📖' },
    { label: '作业管理', path: '/admin/homework', icon: '📄' },
  ]
  if (auth.isAdmin) {
    return [
      { label: '用户管理', path: '/admin/users', icon: '👥' },
      { label: '科目管理', path: '/admin/subjects', icon: '🗂️' },
      ...base,
    ]
  }
  return base
})
</script>
