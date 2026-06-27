<template>
  <div>
    <h1 class="page-title">个人信息</h1>
    <div class="card" style="max-width:560px">
      <div class="card-body">
        <div v-if="!auth.user" class="empty"><span class="empty-icon">👤</span><p>用户信息为空...</p></div>
        <div v-else class="desc-list">
          <div class="desc-row"><span class="desc-label">用户 ID</span><span class="desc-value font-mono">{{ auth.user.userId }}</span></div>
          <div class="desc-row">
            <span class="desc-label">用户名</span>
            <span class="desc-value" style="display:flex;align-items:center;gap:10px">
              <span v-if="!editingUsername">{{ auth.user.username }}</span>
              <input
                v-else
                v-model="usernameInput"
                class="input"
                style="height:32px;padding:0 10px;max-width:220px"
                placeholder="新用户名"
                maxlength="50"
                @keydown.enter="saveUsername"
                @keydown.esc="cancelUsernameEdit"
              />
              <template v-if="!editingUsername">
                <button class="btn btn-secondary btn-sm" @click="startUsernameEdit">编辑</button>
              </template>
              <template v-else>
                <button class="btn btn-primary btn-sm" :class="{ loading: savingUsername }" @click="saveUsername">保存</button>
                <button class="btn btn-secondary btn-sm" @click="cancelUsernameEdit">取消</button>
              </template>
            </span>
          </div>
          <div class="desc-row">
            <span class="desc-label">别名</span>
            <span class="desc-value" style="display:flex;align-items:center;gap:10px">
              <span v-if="!editingName">{{ auth.user.displayName || '未设置' }}</span>
              <input
                v-else
                v-model="nameInput"
                class="input"
                style="height:32px;padding:0 10px;max-width:220px"
                placeholder="留空则使用用户名"
                maxlength="50"
                @keydown.enter="saveName"
                @keydown.esc="cancelEdit"
              />
              <template v-if="!editingName">
                <button class="btn btn-secondary btn-sm" @click="startEdit">编辑</button>
              </template>
              <template v-else>
                <button class="btn btn-primary btn-sm" :class="{ loading: saving }" @click="saveName">保存</button>
                <button class="btn btn-secondary btn-sm" @click="cancelEdit">取消</button>
              </template>
            </span>
          </div>
          <div class="desc-row"><span class="desc-label">邮箱</span><span class="desc-value">{{ auth.user.email || '未设置' }}</span></div>
          <div class="desc-row">
            <span class="desc-label">角色</span>
            <span class="desc-value">
              <span :class="['badge', roleClass(auth.user.role)]">{{ roleLabel(auth.user.role) }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { updateDisplayName, updateUsername } from '@/api/auth'
import type { UserRole } from '@/types'

const auth = useAuthStore()
const toast = useToast()

const editingName = ref(false)
const nameInput = ref('')
const saving = ref(false)

const editingUsername = ref(false)
const usernameInput = ref('')
const savingUsername = ref(false)

function startEdit() {
  nameInput.value = auth.user?.displayName ?? ''
  editingName.value = true
}

function cancelEdit() {
  editingName.value = false
}

async function saveName() {
  saving.value = true
  try {
    await updateDisplayName(nameInput.value.trim())
    await auth.fetchMe()
    editingName.value = false
    toast.success('别名已更新')
  } catch {
    toast.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function startUsernameEdit() {
  usernameInput.value = auth.user?.username ?? ''
  editingUsername.value = true
}

function cancelUsernameEdit() {
  editingUsername.value = false
}

async function saveUsername() {
  const val = usernameInput.value.trim()
  if (!val) { toast.warning('用户名不能为空'); return }
  savingUsername.value = true
  try {
    await updateUsername(val)
    await auth.fetchMe()
    editingUsername.value = false
    toast.success('用户名已更新')
  } catch {
    toast.error('保存失败，用户名可能已被占用')
  } finally {
    savingUsername.value = false
  }
}

const roleLabel = (r: UserRole) => ({ user: '学生', admin: '管理员' }[r] ?? r)
const roleClass = (r: UserRole) => ({ user: 'badge-info', admin: 'badge-danger' }[r] ?? 'badge-info')
</script>
