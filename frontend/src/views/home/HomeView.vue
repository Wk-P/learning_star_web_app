<template>
  <div class="hub">

    <!-- ── 左侧栏 ────────────────────────────────────────────── -->
    <aside class="hub-sidebar">

      <!-- 科目列表 -->
      <div class="hub-section-label">科目</div>
      <div v-if="loadingSubjects" class="skeleton" style="height:120px;border-radius:8px;margin:0 8px" />
      <nav v-else class="hub-subject-list">
        <button
          v-for="s in subjects" :key="s.id"
          :class="['hub-subject-item', { active: activeId === s.id }]"
          :style="activeId === s.id ? { '--accent': s.color, borderLeftColor: s.color } : {}"
          @click="selectSubject(s)"
        >
          <span class="hub-subject-icon">{{ s.icon }}</span>
          <span class="hub-subject-name">{{ s.name }}</span>
          <span v-if="videoCountMap[s.id] !== undefined" class="hub-subject-count">
            {{ videoCountMap[s.id] }}
          </span>
        </button>
      </nav>

      <!-- 用户区 -->
      <div class="hub-user-panel">
        <div class="hub-divider" />

        <!-- 头像 + 基础信息 -->
        <div class="hub-user-header">
          <div class="hub-user-avatar">{{ auth.user?.username?.[0]?.toUpperCase() }}</div>
          <div class="hub-user-meta">
            <div class="hub-user-name">{{ auth.user?.displayName || auth.user?.username }}</div>
            <span class="badge badge-info" style="font-size:10px;padding:1px 6px">学生</span>
          </div>
        </div>

        <!-- 用户名（只读） -->
        <div class="hub-field">
          <label class="hub-field-label">用户名</label>
          <div class="hub-field-row">
            <span class="hub-field-value">{{ auth.user?.username }}</span>
          </div>
        </div>

        <!-- 昵称 -->
        <div class="hub-field">
          <label class="hub-field-label">昵称</label>
          <div class="hub-field-row">
            <input
              v-if="editingName"
              v-model="nameInput"
              class="hub-input"
              placeholder="留空则使用用户名"
              maxlength="50"
              @keydown.enter="saveName"
              @keydown.esc="editingName = false"
            />
            <span v-else class="hub-field-value">{{ auth.user?.displayName || '未设置' }}</span>
            <button v-if="!editingName" class="hub-btn-text" @click="startNameEdit">编辑</button>
            <template v-else>
              <button class="hub-btn-text primary" :class="{ loading: savingName }" @click="saveName">保存</button>
              <button class="hub-btn-text" @click="editingName = false">取消</button>
            </template>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="hub-user-actions">
          <button class="hub-btn-action" @click="showPwModal = true">修改密码</button>
          <button class="hub-btn-logout" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </aside>

    <!-- ── 右侧：视频列表 ────────────────────────────────────── -->
    <main class="hub-content">
      <div v-if="active" class="hub-content-header" :style="{ borderLeftColor: active.color }">
        <span class="hub-content-icon">{{ active.icon }}</span>
        <div>
          <h1 class="hub-content-title">{{ active.name }}</h1>
          <p class="hub-content-desc">{{ active.description || '暂无描述' }}</p>
        </div>
      </div>

      <div v-if="loadingVideos" class="skeleton" style="height:200px;border-radius:8px;margin-top:20px" />

      <div v-else-if="!active" class="hub-empty">
        <span class="empty-icon">👈</span>
        <p>从左侧选择科目</p>
      </div>
      <div v-else-if="videos.length === 0" class="hub-empty">
        <span class="empty-icon">📹</span>
        <p>该科目暂无视频</p>
      </div>

      <ol v-else class="hub-video-list">
        <li v-for="(v, i) in videos" :key="v.index" class="hub-video-item">
          <span class="hub-video-num">{{ i + 1 }}</span>
          <div class="hub-video-info">
            <a :href="v.url" target="_blank" rel="noopener" class="hub-video-title">{{ v.title }}</a>
            <span class="hub-video-url">{{ v.url }}</span>
          </div>
          <div class="hub-video-actions">
            <a :href="v.url" target="_blank" rel="noopener" class="btn-bilibili">▶ B站</a>
            <button :class="['btn-copy', copyState[v.index]]" @click="copyUrl(v)">
              {{ copyLabel(v.index) }}
            </button>
          </div>
        </li>
      </ol>
    </main>

  </div>

  <!-- 修改密码弹窗 -->
  <Teleport to="body">
    <div v-if="showPwModal" class="modal-backdrop" @click.self="closePwModal">
      <div class="modal">
        <div class="modal-header">
          <span>修改密码</span>
          <button class="modal-close" @click="closePwModal">✕</button>
        </div>
        <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
          <div class="field">
            <label class="field-label">旧密码</label>
            <input v-model="pwForm.old" type="password" class="input" placeholder="请输入旧密码" />
          </div>
          <div class="field">
            <label class="field-label">新密码</label>
            <input v-model="pwForm.new" type="password" class="input" placeholder="至少 6 位" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePwModal">取消</button>
          <button class="btn btn-primary" :class="{ loading: pwLoading }" @click="submitPw">确认</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { subjectApi } from '@/api/course'
import { authApi, updateDisplayName } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import type { Subject, BilibiliVideo } from '@/types'

const auth = useAuthStore()
const router = useRouter()
const toast = useToast()

// ── 科目 & 视频 ──────────────────────────────────────────────
const subjects = ref<Subject[]>([])
const active = ref<Subject | null>(null)
const activeId = ref<number | null>(null)
const videos = ref<BilibiliVideo[]>([])
const loadingSubjects = ref(false)
const loadingVideos = ref(false)
const videoCountMap = reactive<Record<number, number>>({})
const copyState = reactive<Record<number, string>>({})

function copyLabel(index: number) {
  const s = copyState[index]
  if (s === 'ok') return '已复制'
  if (s === 'fail') return '复制失败'
  return '复制链接'
}

async function copyUrl(v: BilibiliVideo) {
  try {
    await navigator.clipboard.writeText(v.url)
    copyState[v.index] = 'ok'
  } catch {
    copyState[v.index] = 'fail'
  }
  setTimeout(() => { copyState[v.index] = 'idle' }, 2000)
}

async function selectSubject(s: Subject) {
  if (activeId.value === s.id) return
  active.value = s
  activeId.value = s.id
  videos.value = []
  loadingVideos.value = true
  try {
    const { data } = await subjectApi.videos(s.id)
    videos.value = data
    videoCountMap[s.id] = data.length
  } finally {
    loadingVideos.value = false
  }
}

onMounted(async () => {
  loadingSubjects.value = true
  try {
    const { data } = await subjectApi.list()
    subjects.value = data
    if (data.length > 0) selectSubject(data[0]!)
  } finally {
    loadingSubjects.value = false
  }
})

// ── 昵称编辑 ──────────────────────────────────────────────────
const editingName = ref(false)
const nameInput = ref('')
const savingName = ref(false)

function startNameEdit() {
  nameInput.value = auth.user?.displayName ?? ''
  editingName.value = true
}

async function saveName() {
  savingName.value = true
  try {
    await updateDisplayName(nameInput.value.trim())
    await auth.fetchMe()
    editingName.value = false
    toast.success('别名已更新')
  } catch {
    toast.error('保存失败，请重试')
  } finally {
    savingName.value = false
  }
}

// ── 修改密码 ──────────────────────────────────────────────────
const showPwModal = ref(false)
const pwForm = ref({ old: '', new: '' })
const pwLoading = ref(false)

function closePwModal() {
  showPwModal.value = false
  pwForm.value = { old: '', new: '' }
}

async function submitPw() {
  if (!pwForm.value.old || !pwForm.value.new) { toast.warning('请填写完整'); return }
  if (pwForm.value.new.length < 6) { toast.warning('新密码至少 6 位'); return }
  pwLoading.value = true
  try {
    await authApi.changePassword(pwForm.value.old, pwForm.value.new)
    toast.success('密码修改成功')
    closePwModal()
  } catch {
    toast.error('旧密码错误或修改失败')
  } finally {
    pwLoading.value = false
  }
}

// ── 退出登录 ──────────────────────────────────────────────────
function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── 整体框架 ─────────────────────────────────────────────── */
.hub {
  display: flex;
  min-height: calc(100vh - 58px);
  background: var(--c-bg);
}

/* ── 左侧栏 ───────────────────────────────────────────────── */
.hub-sidebar {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid var(--c-border);
  background: var(--c-surface);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.hub-section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--c-text-3);
  padding: 18px 16px 8px;
}

.hub-subject-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}

.hub-subject-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border-radius: 8px;
  border-left: 3px solid transparent;
  color: var(--c-text-2);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  text-align: left;
  background: transparent;
  width: 100%;
}
.hub-subject-item:hover { background: var(--c-info-light); color: var(--c-text); }
.hub-subject-item.active {
  background: color-mix(in srgb, var(--accent, var(--c-primary)) 12%, transparent);
  color: var(--accent, var(--c-primary));
  font-weight: 600;
}
.hub-subject-icon { font-size: 15px; flex-shrink: 0; }
.hub-subject-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hub-subject-count {
  font-size: 10px;
  background: var(--c-border);
  color: var(--c-text-3);
  border-radius: 10px;
  padding: 1px 6px;
  flex-shrink: 0;
}
.hub-subject-item.active .hub-subject-count {
  background: color-mix(in srgb, var(--accent, var(--c-primary)) 20%, transparent);
  color: var(--accent, var(--c-primary));
}

/* ── 用户面板 ─────────────────────────────────────────────── */
.hub-user-panel {
  padding: 0 10px 16px;
  margin-top: auto;
}
.hub-divider {
  height: 1px;
  background: var(--c-border);
  margin: 12px 0;
}
.hub-user-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.hub-user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--c-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.hub-user-meta { min-width: 0; }
.hub-user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 3px;
}

/* ── 字段 ─────────────────────────────────────────────────── */
.hub-field { margin-bottom: 8px; }
.hub-field-label {
  display: block;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--c-text-3);
  margin-bottom: 4px;
}
.hub-field-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.hub-field-value {
  font-size: 12px;
  color: var(--c-text-2);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hub-input {
  flex: 1;
  min-width: 0;
  height: 28px;
  padding: 0 8px;
  font-size: 12px;
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  background: var(--c-bg);
  color: var(--c-text);
  outline: none;
  width: 100%;
}
.hub-input:focus { border-color: var(--c-primary); }

.hub-btn-text {
  font-size: 11px;
  color: var(--c-text-3);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: var(--r-sm);
  background: transparent;
  white-space: nowrap;
  transition: background 0.12s, color 0.12s;
  flex-shrink: 0;
}
.hub-btn-text:hover { background: var(--c-info-light); color: var(--c-text); }
.hub-btn-text.primary { color: var(--c-primary); }
.hub-btn-text.primary:hover { background: var(--c-primary-light); }

.hub-user-actions { display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }

.hub-btn-action {
  width: 100%;
  padding: 7px 0;
  border-radius: var(--r-sm);
  background: var(--c-primary);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.hub-btn-action:hover { background: var(--c-primary-hover); }

.hub-btn-logout {
  width: 100%;
  padding: 7px 0;
  border-radius: var(--r-sm);
  background: transparent;
  border: 1px solid var(--c-border);
  color: var(--c-danger);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
  margin-top: 4px;
}
.hub-btn-logout:hover { background: #fee2e2; }

/* ── 右侧内容区 ───────────────────────────────────────────── */
.hub-content {
  flex: 1;
  min-width: 0;
  padding: 24px 28px;
  overflow-y: auto;
}

.hub-content-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: var(--r);
  border: 1px solid var(--c-border);
  border-left-width: 5px;
  background: var(--c-surface);
  margin-bottom: 20px;
}
.hub-content-icon { font-size: 32px; flex-shrink: 0; }
.hub-content-title { font-size: 20px; font-weight: 700; color: var(--c-text); margin-bottom: 4px; }
.hub-content-desc { font-size: 13px; color: var(--c-text-2); line-height: 1.4; }

.hub-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 0;
  color: var(--c-text-3);
  font-size: 14px;
}
.hub-empty .empty-icon { font-size: 40px; }

/* ── 视频列表 ─────────────────────────────────────────────── */
.hub-video-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  list-style: none;
  padding: 0;
  margin: 0;
}
.hub-video-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: var(--r);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  transition: box-shadow 0.15s;
}
.hub-video-item:hover { box-shadow: var(--shadow); }

.hub-video-num {
  min-width: 24px;
  font-size: 13px;
  font-weight: 700;
  color: var(--c-text-3);
  flex-shrink: 0;
  text-align: center;
}
.hub-video-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.hub-video-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--c-text);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hub-video-title:hover { color: var(--c-primary); text-decoration: underline; }
.hub-video-url {
  font-size: 12px;
  color: var(--c-text-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hub-video-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}
.btn-bilibili {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: var(--r-sm);
  background: #fb7299;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.btn-bilibili:hover { opacity: 0.85; }

.btn-copy {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 5px 12px;
  border-radius: var(--r-sm);
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text-2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
  min-width: 72px;
}
.btn-copy:hover { background: var(--c-info-light); color: var(--c-text); }
.btn-copy.ok { background: #dcfce7; color: #16a34a; border-color: #16a34a; }
.btn-copy.fail { background: #fee2e2; color: var(--c-danger); border-color: var(--c-danger); }

/* ── 响应式 ───────────────────────────────────────────────── */
@media (max-width: 720px) {
  .hub { flex-direction: column; }
  .hub-sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--c-border); }
  .hub-subject-list { flex-direction: row; flex-wrap: wrap; }
  .hub-subject-item { width: auto; }
  .hub-content { padding: 16px; }
  .hub-video-actions { flex-direction: column; gap: 4px; }
}
</style>
