<template>
  <div class="admin-page">
    <h2 class="page-title">用户管理</h2>

    <!-- create user -->
    <div class="card create-card">
      <h3>新建用户</h3>
      <div class="create-row">
        <input v-model="newUser.username" placeholder="用户名" />
        <input v-model="newUser.password" type="password" placeholder="密码" />
        <input v-model="newUser.email" placeholder="邮箱（可选）" />
        <button class="btn-primary" :disabled="creating" @click="handleCreate">
          {{ creating ? '创建中…' : '创建' }}
        </button>
      </div>
      <p v-if="createError" class="err">{{ createError }}</p>
    </div>

    <!-- user list -->
    <div v-if="loadingUsers" class="loading-hint">加载中…</div>
    <template v-else>
      <div v-for="u in users" :key="u.id" class="user-row card">
        <div class="user-info">
          <span class="user-name">{{ u.username }}</span>
          <span class="user-email">{{ u.email }}</span>
          <span class="badge" :class="u.is_staff ? 'badge-admin' : 'badge-user'">
            {{ u.is_staff ? '管理员' : '普通用户' }}
          </span>
        </div>
        <div class="user-actions">
          <button class="btn-outline" @click="handleResetPassword(u.id, u.username)">重置密码</button>
          <button v-if="!u.is_staff" class="btn-danger" @click="handleDelete(u.id)">删除</button>
        </div>
      </div>
      <div v-if="!users.length" class="empty-hint">暂无用户</div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api, type UserItem } from '@/api'

const users = ref<UserItem[]>([])
const loadingUsers = ref(true)

const newUser = reactive({ username: '', password: '', email: '' })
const creating = ref(false)
const createError = ref('')

onMounted(() => loadUsers())

async function loadUsers() {
  loadingUsers.value = true
  users.value = await api.getUserList()
  loadingUsers.value = false
}

async function handleCreate() {
  createError.value = ''
  if (!newUser.username || !newUser.password) {
    createError.value = '用户名和密码不能为空'
    return
  }
  creating.value = true
  try {
    await api.createUser({ username: newUser.username, password: newUser.password, email: newUser.email })
    newUser.username = ''
    newUser.password = ''
    newUser.email = ''
    await loadUsers()
  } catch (e: unknown) {
    const res = e as Response
    const body = await res.json().catch(() => ({}))
    createError.value = body.detail || '创建失败'
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('确认删除该用户？')) return
  await api.deleteUser(id)
  await loadUsers()
}

async function handleResetPassword(id: number, username: string) {
  const newPassword = prompt(`为用户「${username}」设置新密码（至少 6 位）：`)
  if (!newPassword) return
  if (newPassword.length < 6) {
    alert('新密码至少 6 位')
    return
  }
  try {
    await api.resetUserPassword(id, newPassword)
    alert('密码已重置')
  } catch (e: unknown) {
    const res = e as Response
    const body = await res.json().catch(() => ({}))
    alert(body.detail || '重置失败')
  }
}
</script>

<style scoped>
.card {
  background: #111520;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
}

.create-card {
  margin-bottom: 1.5rem;
}

.create-card h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #8892a4;
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.create-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.create-row input {
  flex: 1;
  min-width: 120px;
  background: #1a2030;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 0.55rem 0.8rem;
  color: #e2e8f0;
  -webkit-text-fill-color: #e2e8f0;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.18s, background 0.18s;
}

.create-row input::placeholder {
  color: #4a5568;
  -webkit-text-fill-color: #4a5568;
}

.create-row input:focus {
  border-color: #2dd4bf;
  background: #1e2640;
}

.err {
  color: #f87171;
  font-size: 0.82rem;
  margin: 0.5rem 0 0;
}

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  cursor: default;
  transition: border-color 0.2s;
}

.user-row.active {
  border-color: #2dd4bf;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #e2e8f0;
}

.user-email {
  font-size: 0.85rem;
  color: #8892a4;
}

.badge {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.badge-admin {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.badge-user {
  background: rgba(45, 212, 191, 0.12);
  color: #2dd4bf;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary {
  background: #2dd4bf;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #8892a4;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}

.btn-outline:hover {
  border-color: #2dd4bf;
  color: #2dd4bf;
}

.btn-danger {
  background: transparent;
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-danger:hover {
  background: rgba(248, 113, 113, 0.1);
}

/* permission panel */
.perm-panel {
  margin-top: 1rem;
}

.perm-panel h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 1.25rem;
}

.perm-section {
  margin-bottom: 1.25rem;
}

.perm-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8892a4;
  margin-bottom: 0.6rem;
  font-weight: 600;
}

.perm-dirs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dir-chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 0.85rem;
  color: #8892a4;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
}

.dir-chip input[type="checkbox"] {
  display: none;
}

.dir-chip.checked {
  border-color: #2dd4bf;
  color: #2dd4bf;
  background: rgba(45, 212, 191, 0.1);
}

.empty-dirs {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.3);
}

.perm-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 0.5rem;
}

.save-msg {
  color: #2dd4bf;
  font-size: 0.85rem;
  margin: 0;
}

/* transition */
.perm-enter-active, .perm-leave-active { transition: opacity 0.25s, transform 0.25s; }
.perm-enter-from, .perm-leave-to { opacity: 0; transform: translateY(-8px); }

.loading-hint, .empty-hint {
  color: #8892a4;
  font-size: 0.9rem;
  padding: 1rem 0;
}

@media (max-width: 600px) {
  .card { padding: 1rem; }
  .create-row { flex-direction: column; gap: 0.5rem; }
  .create-row input, .btn-primary { width: 100%; }
  .user-row { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .user-info { flex-wrap: wrap; }
}
</style>
