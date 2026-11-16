<template>
  <div class="perm-page">

    <!-- left: user list -->
    <aside class="user-panel">
      <div class="panel-head">
        <span class="panel-title">用户</span>
        <input v-model="search" class="search-input" placeholder="搜索…" />
      </div>
      <div v-if="loadingUsers" class="hint">加载中…</div>
      <ul v-else class="user-list">
        <li
          v-for="u in filteredUsers"
          :key="u.id"
          class="user-item"
          :class="{ active: selectedUser?.id === u.id }"
          @click="selectUser(u)"
        >
          <div class="u-info">
            <span class="u-name">{{ u.username }}</span>
            <span v-if="!u.is_staff && userPermCounts[u.id] !== undefined" class="u-perm-count">
              {{ userPermCounts[u.id] }} 项权限
            </span>
          </div>
          <span class="u-badge" :class="u.is_staff ? 'badge-admin' : 'badge-user'">
            {{ u.is_staff ? '管理员' : '用户' }}
          </span>
        </li>
      </ul>
    </aside>

    <!-- right: permission editor -->
    <div class="perm-panel">
      <template v-if="!selectedUser">
        <div class="empty-state">← 选择左侧用户进行权限配置</div>
      </template>
      <template v-else>

        <!-- header -->
        <div class="perm-header">
          <span class="perm-user">{{ selectedUser.username }}</span>
          <span class="perm-subtitle">的访问权限</span>
          <el-select v-model="activeLang" class="lang-select" size="small" placeholder="选择语言">
            <el-option v-for="l in store.languages" :key="l.slug" :label="`${l.name}（${langCount(l.slug)}）`" :value="l.slug" />
          </el-select>
          <div class="header-actions">
            <Transition name="fade">
              <span v-if="saveMsg" class="save-msg">{{ saveMsg }}</span>
            </Transition>
            <button class="btn-save" :disabled="saving" @click="savePerms">
              {{ saving ? '保存中…' : '保存' }}
            </button>
          </div>
        </div>

        <!-- tabs + quick actions -->
        <div class="tab-bar">
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              <AppIcon :name="tab.icon" :size="14" class="tab-icon" />
              {{ tab.label }}
              <span class="tab-count" :class="{ 'count-active': permCount(tab.key) > 0 }">
                {{ permCount(tab.key) }}
              </span>
            </button>
          </div>
          <div class="quick-actions">
            <button class="qa-btn" @click="selectAll">全选</button>
            <button class="qa-btn qa-btn--danger" @click="clearAll">清空</button>
          </div>
        </div>

        <!-- body: tree + summary -->
        <div v-if="loadingPerms" class="hint">加载中…</div>
        <div v-else class="perm-body">

          <!-- tree -->
          <div class="tree-col">
            <div v-if="!currentTree.length" class="empty-state">暂无内容</div>
            <TreeNodeRow
              v-for="node in currentTree"
              :key="node.path"
              :node="node"
              :perms="currentPerms"
              :depth="0"
              @toggle="togglePath"
            />
          </div>

          <!-- summary -->
          <div class="summary-col">
            <div class="summary-head">
              <span class="summary-title">已授权</span>
              <span class="summary-count">{{ permCount(activeTab) }} 项</span>
            </div>
            <div v-if="permCount(activeTab) === 0" class="summary-empty">暂未授权任何目录</div>
            <ul v-else class="summary-list">
              <li
                v-for="p in sortedPerms"
                :key="p"
                class="summary-item"
              >
                <span class="summary-path">{{ p }}</span>
                <button class="summary-remove" @click="togglePath(p)" title="撤销">✕</button>
              </li>
            </ul>
          </div>

        </div>
      </template>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import AppIcon from '@/core/components/AppIcon.vue'
import { accountsApi } from '@/core/api/accounts'
import type { UserItem } from '@/core/api/accounts'
import { languageApi, MEDIA_KINDS, emptyKindDirs, type MediaKind, type PermissionMap, type TreeNode } from '@/language/api'
import { useLanguageStore } from '@/language/stores/languages'
import TreeNodeRow from './PermTreeNode.vue'

const store = useLanguageStore()
const tabs = MEDIA_KINDS

const users = ref<UserItem[]>([])
const loadingUsers = ref(true)
const search = ref('')
const selectedUser = ref<UserItem | null>(null)
const activeLang = ref('')
const activeTab = ref<MediaKind>('video')
const userPermCounts = reactive<Record<number, number>>({})

/** {语言: {类型: 目录树}} */
const tree = ref<Record<string, Record<MediaKind, TreeNode[]>>>({})
/** 当前用户的全部权限（所有语言），保存时整体提交 */
const perms = ref<PermissionMap>({})
const loadingPerms = ref(false)
const saving = ref(false)
const saveMsg = ref('')

const total = (m: PermissionMap) => Object.values(m).reduce((s, k) => s + k.video.length + k.audio.length + k.file.length, 0)

const filteredUsers = computed(() =>
  users.value.filter(u => u.username.toLowerCase().includes(search.value.toLowerCase()))
)
const currentTree = computed(() => tree.value[activeLang.value]?.[activeTab.value] ?? [])
const currentPerms = computed(() => perms.value[activeLang.value]?.[activeTab.value] ?? [])
const sortedPerms = computed(() => [...currentPerms.value].sort())

function permCount(key: MediaKind) {
  return perms.value[activeLang.value]?.[key].length ?? 0
}
function langCount(slug: string) {
  const k = perms.value[slug]
  return k ? k.video.length + k.audio.length + k.file.length : 0
}

function setCurrent(list: string[]) {
  const lang = activeLang.value
  if (!lang) return
  perms.value[lang] ??= emptyKindDirs()
  perms.value[lang][activeTab.value] = list
}

function selectAll() {
  // 授权全部第一层目录（前缀匹配覆盖子目录）
  setCurrent(currentTree.value.map(n => n.path))
}

function clearAll() {
  setCurrent([])
}

onMounted(async () => {
  const [userList, treeData] = await Promise.all([
    accountsApi.listUsers(),
    languageApi.permissionTree(),
    store.reload(),
  ])
  users.value = userList
  loadingUsers.value = false
  tree.value = treeData
  activeLang.value = store.languages[0]?.slug ?? ''

  // 侧栏显示每个普通用户的权限数
  await Promise.all(
    userList.filter(u => !u.is_staff).map(async u => {
      userPermCounts[u.id] = total(await languageApi.userPermissions(u.id))
    })
  )
})

async function selectUser(u: UserItem) {
  selectedUser.value = u
  loadingPerms.value = true
  perms.value = await languageApi.userPermissions(u.id)
  loadingPerms.value = false
}

function togglePath(path: string) {
  const list = currentPerms.value
  if (list.includes(path)) {
    setCurrent(list.filter(p => !p.startsWith(path + '/') && p !== path))
  } else {
    setCurrent([...list.filter(p => !p.startsWith(path + '/')), path])
  }
}

async function savePerms() {
  if (!selectedUser.value) return
  saving.value = true
  saveMsg.value = ''
  try {
    perms.value = await languageApi.setUserPermissions(selectedUser.value.id, perms.value)
    userPermCounts[selectedUser.value.id] = total(perms.value)
    saveMsg.value = '已保存 ✓'
  } catch {
    saveMsg.value = '保存失败'
  } finally {
    saving.value = false
    setTimeout(() => { saveMsg.value = '' }, 2000)
  }
}
</script>

<style scoped>
.perm-page {
  display: flex;
  gap: 1.25rem;
  height: calc(100dvh - 60px - 3rem);
  min-height: 0;
}

.lang-select { width: 150px; margin-left: 0.75rem; }

/* ── user panel ── */
.user-panel {
  width: 210px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #112042;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
}

.panel-head {
  padding: 0.85rem 0.9rem 0.6rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.panel-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8892a4;
}

.search-input {
  background: #18294d;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.82rem;
  color: #e2e8f0;
  outline: none;
  transition: border-color 0.18s;
}
.search-input:focus { border-color: #5ad8cf; }
.search-input::placeholder { color: #4a5568; }

.user-list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0.4rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.user-item:hover  { background: rgba(255,255,255,0.04); }
.user-item.active { background: rgba(45,212,191,0.1); border-left: 2px solid #5ad8cf; }

.u-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  overflow: hidden;
}

.u-name {
  font-size: 0.875rem;
  color: #e2e8f0;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.u-perm-count {
  font-size: 0.7rem;
  color: #8892a4;
}

.u-badge {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-weight: 700;
  flex-shrink: 0;
  margin-left: 0.4rem;
  align-self: flex-start;
}
.badge-admin { background: rgba(245,158,11,0.15); color: #f59e0b; }
.badge-user  { background: rgba(45,212,191,0.1);  color: #5ad8cf; }

/* ── perm panel ── */
.perm-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #112042;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
}

.perm-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}

.perm-user   { font-size: 1rem; font-weight: 700; color: #5ad8cf; }
.perm-subtitle { font-size: 0.9rem; color: #8892a4; flex: 1; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-save {
  background: #5ad8cf;
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 1.1rem;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.save-msg { font-size: 0.82rem; color: #5ad8cf; }

/* ── tabs + quick actions ── */
.tab-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}

.tabs {
  display: flex;
  padding-top: 0.6rem;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #8892a4;
  font-size: 0.875rem;
  cursor: pointer;
  transition: color 0.18s, border-color 0.18s;
  margin-bottom: -1px;
}
.tab-btn:hover  { color: #e2e8f0; }
.tab-btn.active { color: #5ad8cf; border-bottom-color: #5ad8cf; }

.tab-icon { font-size: 0.8rem; opacity: 0.8; }

.tab-count {
  font-size: 0.7rem;
  padding: 0.05rem 0.4rem;
  border-radius: 999px;
  background: rgba(255,255,255,0.07);
  color: #8892a4;
  font-weight: 700;
  transition: background 0.18s, color 0.18s;
}
.tab-count.count-active { background: rgba(45,212,191,0.15); color: #5ad8cf; }

.quick-actions { display: flex; gap: 0.4rem; }

.qa-btn {
  font-size: 0.75rem;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.12);
  background: none;
  color: #8892a4;
  cursor: pointer;
  transition: all 0.15s;
}
.qa-btn:hover { border-color: #5ad8cf; color: #5ad8cf; }
.qa-btn--danger:hover { border-color: #f87171; color: #f87171; }

/* ── body: tree + summary ── */
.perm-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 0;
}

.tree-col {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 1rem;
  border-right: 1px solid rgba(255,255,255,0.06);
}

.summary-col {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.summary-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem 0.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.summary-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #8892a4;
}

.summary-count {
  font-size: 0.72rem;
  color: #5ad8cf;
  font-weight: 700;
}

.summary-empty {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.2);
  padding: 1.25rem 1rem;
  text-align: center;
}

.summary-list {
  flex: 1;
  overflow-y: auto;
  list-style: none;
  padding: 0.4rem 0.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  background: rgba(45,212,191,0.06);
  border: 1px solid rgba(45,212,191,0.15);
}

.summary-path {
  font-size: 0.78rem;
  color: #a7f3d0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.summary-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255,255,255,0.25);
  font-size: 0.65rem;
  padding: 0.1rem 0.2rem;
  border-radius: 3px;
  flex-shrink: 0;
  transition: color 0.15s;
  line-height: 1;
}
.summary-remove:hover { color: #f87171; }

.empty-state { color: #8892a4; font-size: 0.9rem; padding: 2rem; text-align: center; margin: auto; }
.hint { color: #8892a4; font-size: 0.875rem; padding: 1rem; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── mobile ── */
@media (max-width: 768px) {
  .perm-page {
    flex-direction: column;
    height: auto;
    overflow: visible;
    gap: 0.75rem;
  }

  .user-panel {
    width: 100%;
    max-height: 180px;
    flex-shrink: 0;
  }

  .user-list {
    flex-direction: row;
    overflow-x: auto;
    overflow-y: hidden;
    flex-wrap: nowrap;
    padding: 0.4rem;
    scrollbar-width: none;
  }
  .user-list::-webkit-scrollbar { display: none; }

  .user-item {
    flex-shrink: 0;
    min-width: 100px;
    max-width: 140px;
  }

  .perm-panel {
    min-height: 50vh;
  }

  .perm-header {
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.7rem 0.9rem;
  }

  .perm-subtitle { display: none; }

  .tab-bar {
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.5rem 0.75rem;
  }

  .tabs { padding-top: 0; }

  .tab-btn { padding: 0.4rem 0.65rem; font-size: 0.82rem; }

  .summary-col { display: none; }

  .tree-col { border-right: none; padding: 0.5rem 0.75rem; }
}
</style>
