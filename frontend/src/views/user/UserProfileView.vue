<template>
  <div>
    <h1 class="page-title">个人信息</h1>
    <div class="card" style="max-width:560px">
      <div class="card-body">
        <div v-if="!auth.user" class="empty"><span class="empty-icon">👤</span><p>用户信息为空...</p></div>
        <div v-else class="desc-list">
          <div class="desc-row"><span class="desc-label">用户 ID</span><span class="desc-value font-mono">{{ auth.user.userId }}</span></div>
          <div class="desc-row"><span class="desc-label">用户名</span><span class="desc-value">{{ auth.user.username }}</span></div>
          <div class="desc-row"><span class="desc-label">邮箱</span><span class="desc-value">{{ auth.user.email || '未设置' }}</span></div>
          <div class="desc-row">
            <span class="desc-label">角色</span>
            <span class="desc-value">
              <span :class="['badge', roleClass(auth.user.role)]">{{ roleLabel(auth.user.role) }}</span>
            </span>
          </div>
          <div class="desc-row"><span class="desc-label">已申请课程</span><span class="desc-value">{{ enrollment.enrollments.size }} 门</span></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useEnrollmentStore } from '@/stores/enrollment'
import type { UserRole } from '@/types'
const auth = useAuthStore(); const enrollment = useEnrollmentStore()
const roleLabel = (r: UserRole) => ({ user: '学生', staff: '教师', admin: '管理员' }[r])
const roleClass = (r: UserRole) => ({ user: 'badge-info', staff: 'badge-warning', admin: 'badge-danger' }[r])
</script>
