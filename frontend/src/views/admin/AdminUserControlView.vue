<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">用户管理</h1>
      <div class="toolbar-spacer" />
      <input v-model="search" class="input" placeholder="搜索用户名" style="width:200px" />
      <button class="btn btn-primary" @click="openCreate">＋ 新增用户</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />
    <div v-else-if="filtered.length === 0" class="empty"><span class="empty-icon">👥</span><p>用户列表为空...</p></div>
    <div v-else class="table-wrap">
      <table class="table">
        <thead><tr><th>用户ID</th><th>用户名</th><th>别名</th><th>邮箱</th><th>角色</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td class="font-mono text-sm text-muted">{{ u.userId }}</td>
            <td style="font-weight:500">{{ u.username }}</td>
            <td class="text-secondary">{{ u.displayName || '—' }}</td>
            <td class="text-secondary">{{ u.email || '—' }}</td>
            <td>
              <select
                :value="u.role"
                class="role-select"
                :class="`role-${u.role}`"
                @change="handleRoleChange(u, ($event.target as HTMLSelectElement).value as UserRole)"
              >
                <option value="user">学生</option>
                <option value="staff">教师</option>
                <option value="admin">管理员</option>
              </select>
            </td>
            <td>
              <div class="table-actions">
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/users/${u.id}/courses`)">课程</button>
                <button class="btn btn-secondary btn-sm" @click="router.push(`/admin/users/${u.id}/homework`)">作业</button>
                <button class="btn btn-secondary btn-sm" @click="openEditName(u)">别名</button>
                <button class="btn btn-secondary btn-sm" @click="handleReset(u.id)">重置密码</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(u.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 重置密码结果弹窗 -->
    <Teleport to="body">
      <div v-if="resetResult.show" class="modal-backdrop" @click.self="resetResult.show = false">
        <div class="modal" style="max-width:400px">
          <div class="modal-header">
            <span>密码重置成功</span>
            <button class="modal-close" @click="resetResult.show = false">✕</button>
          </div>
          <div class="modal-body" style="padding-top:20px;display:flex;flex-direction:column;gap:16px">
            <p style="font-size:13px;color:var(--c-text-2)">新密码已生成，请妥善保管并告知用户。</p>
            <div class="reset-pw-box">
              <span class="reset-pw-value font-mono">{{ resetResult.password }}</span>
              <button class="btn btn-secondary btn-sm" @click="copyPassword">
                {{ copied ? '✓ 已复制' : '复制' }}
              </button>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" @click="resetResult.show = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 新增弹窗 -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header"><span>新增用户</span><button class="modal-close" @click="showCreate = false">✕</button></div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field"><label class="field-label">用户名</label><input v-model="form.username" class="input" /></div>
            <div class="field"><label class="field-label">别名（可选）</label><input v-model="form.displayName" class="input" placeholder="留空则显示用户名" maxlength="50" /></div>
            <div class="field"><label class="field-label">邮箱</label><input v-model="form.email" type="email" class="input" /></div>
            <div class="field">
              <label class="field-label">角色</label>
              <select v-model="form.role" class="select">
                <option value="user">学生</option>
                <option value="staff">教师</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            <div class="field"><label class="field-label">密码</label><input v-model="form.password" type="password" class="input" /></div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCreate = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleCreate">创建</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑别名弹窗 -->
    <Teleport to="body">
      <div v-if="editNameTarget" class="modal-backdrop" @click.self="editNameTarget = null">
        <div class="modal" style="max-width:400px">
          <div class="modal-header">
            <span>编辑别名 — {{ editNameTarget.username }}</span>
            <button class="modal-close" @click="editNameTarget = null">✕</button>
          </div>
          <div class="modal-body" style="padding-top:20px">
            <div class="field">
              <label class="field-label">别名（留空则显示用户名）</label>
              <input v-model="editNameInput" class="input" maxlength="50" placeholder="输入别名" @keydown.enter="handleSaveName" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="editNameTarget = null">取消</button>
            <button class="btn btn-primary" :class="{ loading: savingName }" @click="handleSaveName">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { adminUserApi } from '@/api/admin'
import type { AdminUserDetail, UserRole } from '@/types'

const router = useRouter(); const toast = useToast(); const { confirm } = useConfirm()
const loading = ref(false); const saving = ref(false); const showCreate = ref(false)
const search = ref(''); const users = ref<AdminUserDetail[]>([])
const resetResult = ref({ show: false, password: '' })
const copied = ref(false)
const editNameTarget = ref<AdminUserDetail | null>(null)
const editNameInput = ref('')
const savingName = ref(false)

function copyPassword() {
  const text = resetResult.value.password
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      copied.value = true
      setTimeout(() => { copied.value = false }, 2000)
    })
    return
  }
  // HTTP 环境回退方案
  const el = document.createElement('textarea')
  el.value = text
  el.style.position = 'fixed'
  el.style.opacity = '0'
  document.body.appendChild(el)
  el.select()
  document.execCommand('copy')
  document.body.removeChild(el)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
const form = ref({ username: '', email: '', role: 'user' as UserRole, password: '', displayName: '' })

const filtered = computed(() => users.value.filter(u => u.username.includes(search.value)))

onMounted(async () => { loading.value = true; try { users.value = (await adminUserApi.list()).data } finally { loading.value = false } })

function openCreate() { form.value = { username: '', email: '', role: 'user', password: '', displayName: '' }; showCreate.value = true }

function openEditName(u: AdminUserDetail) {
  editNameTarget.value = u
  editNameInput.value = u.displayName ?? ''
}

async function handleSaveName() {
  if (!editNameTarget.value) return
  savingName.value = true
  try {
    await adminUserApi.update(editNameTarget.value.id, { displayName: editNameInput.value.trim() })
    editNameTarget.value.displayName = editNameInput.value.trim()
    editNameTarget.value = null
    toast.success('别名已更新')
  } catch {
    toast.error('保存失败')
  } finally {
    savingName.value = false
  }
}

async function handleRoleChange(user: AdminUserDetail, newRole: UserRole) {
  try {
    await adminUserApi.update(user.id, { role: newRole })
    user.role = newRole
    toast.success(`已将 ${user.username} 设为${roleLabel(newRole)}`)
  } catch {
    toast.error('角色修改失败')
  }
}

async function handleCreate() {
  saving.value = true
  try { const { data } = await adminUserApi.create(form.value); users.value.unshift(data); showCreate.value = false; toast.success('创建成功') }
  finally { saving.value = false }
}
async function handleReset(id: number) {
  const ok = await confirm({ title: '重置密码', message: '确认重置该用户密码？新密码将随机生成。', type: 'warning' })
  if (!ok) return
  const { data } = await adminUserApi.resetPassword(id)
  copied.value = false
  resetResult.value = { show: true, password: data.newPassword }
}
async function handleDelete(id: number) {
  const ok = await confirm({ title: '删除用户', message: '确认删除该用户？此操作不可撤销。', confirmText: '删除', type: 'danger' })
  if (!ok) return
  await adminUserApi.delete(id); users.value = users.value.filter(u => u.id !== id); toast.success('删除成功')
}
const roleLabel = (r: UserRole) => ({ user: '学生', staff: '教师', admin: '管理员' }[r])
const roleClass = (r: UserRole) => ({ user: 'badge-info', staff: 'badge-warning', admin: 'badge-danger' }[r])
</script>

<style scoped>
.role-select {
  height: 28px; padding: 0 24px 0 8px; border-radius: var(--r-sm);
  border: 1.5px solid var(--c-border); font-size: 12px; font-weight: 500;
  cursor: pointer; appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 6px center;
  transition: border-color var(--t);
}
.role-select:focus { outline: none; border-color: var(--c-primary); }
.role-user   { background-color: var(--c-info-light);    color: var(--c-info); }
.role-staff  { background-color: var(--c-warning-light); color: #92400e; }
.role-admin  { background-color: var(--c-danger-light);  color: #991b1b; }

.reset-pw-box {
  display: flex; align-items: center; gap: 12px;
  background: var(--c-info-light); border: 1.5px solid var(--c-border);
  border-radius: var(--r-sm); padding: 12px 16px;
}
.reset-pw-value {
  flex: 1; font-size: 18px; font-weight: 700; letter-spacing: 2px;
  color: var(--c-primary);
}
</style>
