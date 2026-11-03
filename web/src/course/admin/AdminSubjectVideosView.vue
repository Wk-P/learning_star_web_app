<template>
  <div class="sv" :style="{ '--accent': subject?.color || 'var(--c-primary)' }">
    <router-link to="/admin/course/subjects" class="sv-back">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M15 6l-6 6 6 6" /></svg>
      科目管理
    </router-link>

    <header class="sv-head">
      <div v-if="subject" class="sv-id">
        <span class="sv-icon">{{ subject.icon || '📖' }}</span>
        <div>
          <h1 class="sv-title">{{ subject.name }}</h1>
          <p class="sv-sub">共 {{ videos.length }} 个视频<template v-if="unleveled"> · <span class="sv-warn">{{ unleveled }} 个未分级</span></template></p>
        </div>
      </div>
      <div v-else class="sv-id">
        <span class="skeleton sv-icon" />
        <div><div class="skeleton" style="width:120px;height:22px" /><div class="skeleton" style="width:80px;height:14px;margin-top:6px" /></div>
      </div>
      <button class="btn btn-primary sv-add" @click="openAdd">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M12 5v14M5 12h14" /></svg>
        添加视频
      </button>
    </header>

    <!-- 筛选 -->
    <div v-if="!loading && videos.length" class="sv-bar">
      <label class="sv-search">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
        <input v-model="keyword" type="search" placeholder="搜索标题、标签或 BV 号" aria-label="搜索视频" />
      </label>
      <select v-if="allTags.length" v-model="tag" class="sv-tag-select" :class="{ on: tag }" aria-label="按标签筛选">
        <option value="">全部标签</option>
        <option v-for="t in allTags" :key="t" :value="t">#{{ t }}</option>
      </select>
      <div class="sv-seg" role="tablist" aria-label="按阶段筛选">
        <button
          v-for="o in stageOptions"
          :key="o.key"
          role="tab"
          :aria-selected="stage === o.key"
          :class="['sv-seg-opt', { on: stage === o.key }]"
          :style="{ '--lv': o.color }"
          @click="stage = o.key"
        >
          <i v-if="o.key !== 'all'" class="sv-dot" />{{ o.label }}<span>{{ o.count }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="sv-list">
      <div v-for="i in 5" :key="i" class="skeleton sv-sk" />
    </div>

    <div v-else-if="videos.length === 0" class="sv-empty">
      <span class="sv-empty-icon">📹</span>
      <p>这个科目还没有视频</p>
      <button class="btn btn-primary btn-sm" @click="openAdd">添加第一个视频</button>
    </div>

    <div v-else-if="shown.length === 0" class="sv-empty">
      <span class="sv-empty-icon">🔍</span>
      <p>没有符合条件的视频</p>
      <button class="btn btn-secondary btn-sm" @click="keyword = ''; stage = 'all'; tag = ''">清除筛选</button>
    </div>

    <ol v-else class="sv-list">
      <li v-for="v in shown" :key="v.index" class="sv-item">
        <span class="sv-num">{{ String(order[v.index]! + 1).padStart(2, '0') }}</span>
        <div class="sv-info">
          <div class="sv-name" :title="v.title">{{ v.title }}</div>
          <div class="sv-meta">
            <span v-for="l in LEVELS.filter(x => v.levels.includes(x.key))" :key="l.key" class="lv-badge" :style="{ '--lv': l.color }">{{ l.key }}</span>
            <span v-if="!v.levels.length" class="lv-badge lv-none">未分级</span>
            <span v-for="t in v.tags" :key="t" class="sv-tag">#{{ t }}</span>
            <a :href="v.url" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer" class="sv-link" :title="v.url">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" /></svg>
              {{ shortLink(v.url) }}
            </a>
          </div>
        </div>
        <div class="sv-actions">
          <button class="sv-icon-btn" title="编辑" aria-label="编辑视频" @click="openEdit(v)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h4L19 9l-4-4L4 16v4z" /><path d="M13.5 6.5l4 4" /></svg>
          </button>
          <button class="sv-icon-btn danger" title="删除" aria-label="删除视频" @click="handleDelete(v)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3" /></svg>
          </button>
        </div>
      </li>
    </ol>

    <!-- 添加弹窗（粘贴一行） -->
    <Teleport to="#course-layer">
      <div v-if="showAddModal" class="modal-backdrop" @click.self="showAddModal = false">
        <div class="modal" style="max-width:560px">
          <div class="modal-header">
            <span>添加视频</span>
            <button class="modal-close" @click="showAddModal = false">✕</button>
          </div>
          <div class="modal-body" style="padding-top:20px">
            <div class="field">
              <label class="field-label">粘贴链接</label>
              <textarea
                v-model="addLine"
                class="textarea"
                rows="2"
                placeholder="【视频标题】 https://www.bilibili.com/video/…，YouTube 可只粘贴链接"
                style="resize:vertical;font-size:13px"
              />
              <p v-if="addDuplicate" class="field-hint field-warn">已存在相同视频：「{{ addDuplicate.title }}」</p>
              <p v-else-if="addLink" class="field-hint">
                识别为：<b :style="{ color: PLATFORMS[addLink.platform].color }">{{ PLATFORMS[addLink.platform].label }}</b>
                <template v-if="addLink.id"> · {{ addLink.id }}</template>
                <template v-else-if="addLink.platform !== 'other'"> · 未识别出视频 ID，查重按完整链接</template>
                <template v-else> · {{ addLink.host }}</template>
              </p>
              <p v-if="needsLineTitle" class="field-hint field-warn">缺少标题：在链接前面写上视频标题，用空格隔开</p>
              <p v-if="!addUrl" class="field-hint">标题 + 空格 + 链接；YouTube 链接可只粘贴链接，再单独填写标题</p>
            </div>
            <div v-if="isYoutube" class="field" style="margin-top:14px">
              <label class="field-label">标题 <span class="sv-required">必填</span></label>
              <input v-model="ytTitle" class="input" maxlength="200" placeholder="填写 YouTube 视频标题" />
            </div>
            <div class="field" style="margin-top:14px">
              <label class="field-label">课程阶段</label>
              <LevelPicker v-model="addLevels" />
            </div>
            <div class="field" style="margin-top:14px">
              <label class="field-label">标签 <span class="sv-optional">可选</span></label>
              <input v-model="addTags" class="input" maxlength="120" placeholder="逗号分隔，如：考研, 王道, 速成" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAddModal = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleAdd">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑弹窗（title + url） -->
    <Teleport to="#course-layer">
      <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
        <div class="modal" style="max-width:520px">
          <div class="modal-header">
            <span>编辑视频</span>
            <button class="modal-close" @click="showEditModal = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field">
              <label class="field-label">标题</label>
              <input v-model="editForm.title" class="input" placeholder="视频标题" />
            </div>
            <div class="field">
              <label class="field-label">B站链接</label>
              <input v-model="editForm.url" class="input" placeholder="https://www.bilibili.com/video/… 或 https://youtu.be/…" />
              <p v-if="editForm.url.trim()" class="field-hint">
                识别为：<b :style="{ color: PLATFORMS[parseVideoLink(editForm.url).platform].color }">{{ PLATFORMS[parseVideoLink(editForm.url).platform].label }}</b>
                · {{ shortLink(editForm.url) }}
              </p>
            </div>
            <div class="field">
              <label class="field-label">课程阶段</label>
              <LevelPicker v-model="editForm.levels" />
            </div>
            <div class="field" style="margin-top:14px">
              <label class="field-label">标签 <span class="sv-optional">可选</span></label>
              <input v-model="editForm.tags" class="input" maxlength="120" placeholder="逗号分隔，如：考研, 王道, 速成" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleEditSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminSubjectApi } from '@/course/api/admin'
import { subjectApi } from '@/course/api/course'
import { useToast } from '@/course/composables/useToast'
import { useConfirm } from '@/course/composables/useConfirm'
import type { BilibiliVideo, Subject, VideoLevel } from '@/course/types'
import LevelPicker from '@/course/components/LevelPicker.vue'
import { LEVELS } from '@/course/levels'
import { PLATFORMS, parsePaste, parseVideoLink, shortLink, videoKey } from '@/course/videoLink'

const route = useRoute()
const toast = useToast()
const { confirm } = useConfirm()

const subjectId = Number(route.params.subjectId)
const subject = ref<Subject | null>(null)
const videos = ref<BilibiliVideo[]>([])
const loading = ref(false)
const saving = ref(false)

// 添加弹窗
const showAddModal = ref(false)
const addLine = ref('')
const addLevels = ref<VideoLevel[]>([])
const addTags = ref('')

// 「a, b，c」→ ['a','b','c']；留空即无标签
function splitTags(s: string) {
  return [...new Set(s.split(/[,，、]/).map(t => t.trim()).filter(Boolean))]
}
// 粘贴时即时提示重复（后端同样会拦截）
const pasted = computed(() => parsePaste(addLine.value))
const addUrl = computed(() => pasted.value.url)
// 标题：B 站 / 其他链接沿用「标题 链接」格式；YouTube 单独填写（必填），粘贴里带了标题就预填
const isYoutube = computed(() => !!addUrl.value && parseVideoLink(addUrl.value).platform === 'youtube')
const ytTitle = ref('')
watch(isYoutube, yt => { if (yt) ytTitle.value = pasted.value.title })
const addTitle = computed(() => (isYoutube.value ? ytTitle.value : pasted.value.title).trim())
const needsLineTitle = computed(() => !!addUrl.value && !isYoutube.value && !addTitle.value && !addDuplicate.value)
const addLink = computed(() => (addUrl.value ? parseVideoLink(addUrl.value) : null))
const addDuplicate = computed(() => {
  if (!addUrl.value) return null
  const key = videoKey(addUrl.value)
  return videos.value.find(v => videoKey(v.url) === key) ?? null
})

// ── 筛选 ─────────────────────────────────────────────────
type StageKey = 'all' | VideoLevel | 'none'
const keyword = ref('')
const stage = ref<StageKey>('all')
const tag = ref('')
const allTags = computed(() => [...new Set(videos.value.flatMap(v => v.tags ?? []))])

// 显示序号按文件中的顺序，不随筛选变化
const order = computed(() => Object.fromEntries(videos.value.map((v, i) => [v.index, i])) as Record<number, number>)
const unleveled = computed(() => videos.value.filter(v => !v.levels.length).length)

const searched = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  const byTag = tag.value ? videos.value.filter(v => (v.tags ?? []).includes(tag.value)) : videos.value
  return k ? byTag.filter(v => v.title.toLowerCase().includes(k) || (v.tags ?? []).some(t => t.toLowerCase().includes(k)) || v.url.toLowerCase().includes(k)) : byTag
})
function inStage(v: BilibiliVideo, key: StageKey) {
  return key === 'all' || (key === 'none' ? !v.levels.length : v.levels.includes(key))
}
const stageOptions = computed(() => {
  const opts: { key: StageKey; label: string; color: string }[] = [
    { key: 'all', label: '全部', color: 'var(--accent)' },
    ...LEVELS.map(l => ({ key: l.key as StageKey, label: l.key as string, color: l.color })),
  ]
  if (unleveled.value) opts.push({ key: 'none', label: '未分级', color: 'var(--c-text-3)' })
  return opts.map(o => ({ ...o, count: searched.value.filter(v => inStage(v, o.key)).length }))
})
const shown = computed(() => searched.value.filter(v => inStage(v, stage.value)))

// 编辑弹窗
const showEditModal = ref(false)
const editTarget = ref<BilibiliVideo | null>(null)
const editForm = ref<{ title: string; url: string; levels: VideoLevel[]; tags: string }>({ title: '', url: '', levels: [], tags: '' })

onMounted(async () => {
  loading.value = true
  try {
    const [subjectRes, videoRes] = await Promise.all([
      subjectApi.list(),
      adminSubjectApi.listVideos(subjectId),
    ])
    subject.value = subjectRes.data.find(s => s.id === subjectId) ?? null
    videos.value = videoRes.data
  } finally {
    loading.value = false
  }
})

function openAdd() {
  addLine.value = ''
  addLevels.value = []
  addTags.value = ''
  ytTitle.value = ''
  showAddModal.value = true
}

function openEdit(v: BilibiliVideo) {
  editTarget.value = v
  editForm.value = { title: v.title, url: v.url, levels: [...v.levels], tags: (v.tags ?? []).join(', ') }
  showEditModal.value = true
}

async function handleAdd() {
  if (!addLine.value.trim()) { toast.warning('请粘贴视频链接'); return }
  if (!addUrl.value) { toast.warning('找不到链接，应包含 http:// 或 https://'); return }
  if (!addTitle.value) {
    toast.warning(isYoutube.value ? '请填写 YouTube 视频标题' : '缺少标题：在链接前面写上视频标题，用空格隔开')
    return
  }
  const line = `${addTitle.value} ${addUrl.value}`
  if (addDuplicate.value) { toast.warning(`该视频已存在：「${addDuplicate.value.title}」`); return }
  saving.value = true
  try {
    await adminSubjectApi.addVideo(subjectId, { line, levels: addLevels.value, tags: splitTags(addTags.value) })
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    showAddModal.value = false
    toast.success('已添加')
  } catch (e: any) {
    const msg = e?.response?.data?.detail || '添加失败'
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

async function handleEditSave() {
  if (!editForm.value.title.trim() || !editForm.value.url.trim()) {
    toast.warning('请填写标题和链接')
    return
  }
  saving.value = true
  try {
    await adminSubjectApi.updateVideo(subjectId, editTarget.value!.index, { ...editForm.value, tags: splitTags(editForm.value.tags) })
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    showEditModal.value = false
    toast.success('已更新')
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(v: BilibiliVideo) {
  const ok = await confirm({ title: '删除视频', message: `确认删除「${v.title}」？`, confirmText: '删除', type: 'danger' })
  if (!ok) return
  try {
    await adminSubjectApi.deleteVideo(subjectId, v.index)
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    toast.success('已删除')
  } catch {
    toast.error('删除失败')
  }
}
</script>

<style scoped>
.sv-back {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 500; color: var(--c-text-3);
  margin-bottom: 14px; transition: color var(--t);
}
.sv-back:hover { color: var(--c-text); }

.sv-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.sv-id { display: flex; align-items: center; gap: 14px; min-width: 0; }
.sv-icon {
  width: 48px; height: 48px; border-radius: 14px; flex-shrink: 0;
  display: grid; place-items: center; font-size: 24px;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 28%, transparent);
}
.sv-title { font-size: 22px; font-weight: 700; color: var(--c-text); letter-spacing: -0.01em; line-height: 1.2; }
.sv-sub { font-size: 13px; color: var(--c-text-3); margin-top: 3px; }
.sv-warn { color: var(--c-warning, #d97706); }
.sv-add { gap: 6px; flex-shrink: 0; }

/* ── 筛选栏 ───────────────────────────────────────────── */
.sv-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
.sv-tag-select {
  flex: 0 0 auto; max-width: 180px; height: 36px; padding: 0 10px;
  border: none; border-radius: var(--r); font-size: 13px;
  color: var(--c-text-2, var(--c-text)); background: var(--c-surface);
  box-shadow: inset 0 0 0 1px var(--c-border); cursor: pointer;
}
.sv-tag-select.on { color: var(--c-text); box-shadow: inset 0 0 0 1.5px var(--accent); }
.sv-search {
  flex: 1 1 240px; min-width: 0; max-width: 360px;
  display: flex; align-items: center; gap: 8px;
  height: 36px; padding: 0 12px; border-radius: var(--r);
  color: var(--c-text-3); background: var(--c-surface);
  box-shadow: inset 0 0 0 1px var(--c-border); cursor: text;
  transition: box-shadow var(--t);
}
.sv-search:focus-within { box-shadow: inset 0 0 0 1.5px var(--accent), 0 0 0 4px color-mix(in srgb, var(--accent) 16%, transparent); }
.sv-search input { flex: 1; min-width: 0; border: none; outline: none; background: transparent; color: var(--c-text); font-size: 13px; }
.sv-seg {
  display: flex; gap: 2px; padding: 3px; border-radius: var(--r);
  background: var(--c-surface); box-shadow: inset 0 0 0 1px var(--c-border);
  overflow-x: auto; scrollbar-width: none;
}
.sv-seg-opt {
  display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0;
  height: 30px; padding: 0 11px; border-radius: calc(var(--r) - 3px);
  font-size: 13px; font-weight: 600; color: var(--c-text-3); white-space: nowrap;
  transition: background var(--t), color var(--t);
}
.sv-seg-opt span { font-size: 11px; font-weight: 500; font-variant-numeric: tabular-nums; opacity: 0.75; }
.sv-seg-opt:hover { color: var(--c-text); }
.sv-seg-opt.on { color: var(--c-text); background: color-mix(in srgb, var(--lv) 16%, transparent); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--lv) 40%, transparent); }
.sv-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--lv); }

/* ── 列表 ─────────────────────────────────────────────── */
.sv-list { display: flex; flex-direction: column; gap: 8px; }
.sv-sk { height: 68px; border-radius: var(--r); }
.sv-item {
  display: flex; align-items: center; gap: 14px;
  padding: 12px 10px 12px 14px; border-radius: var(--r);
  background: var(--c-surface); border: 1px solid var(--c-border);
  transition: border-color var(--t), background var(--t);
}
.sv-item:hover { border-color: color-mix(in srgb, var(--accent) 40%, var(--c-border)); }
.sv-num {
  width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0;
  display: grid; place-items: center;
  font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums;
  color: color-mix(in srgb, var(--accent) 70%, var(--c-text));
  background: color-mix(in srgb, var(--accent) 12%, transparent);
}
.sv-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
.sv-name { font-size: 14px; font-weight: 600; color: var(--c-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sv-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.lv-badge {
  font-size: 11px; font-weight: 600; padding: 1px 8px; border-radius: var(--r-full);
  color: var(--lv); background: color-mix(in srgb, var(--lv) 14%, transparent);
}
.lv-none { --lv: var(--c-warning, #d97706); }
.sv-tag { font-size: 11px; padding: 1px 7px; border-radius: 99px; color: var(--c-text-2, var(--c-text)); background: color-mix(in srgb, var(--c-text-3) 16%, transparent); }
.sv-required { font-weight: 400; font-size: 11px; color: var(--c-danger); margin-left: 4px; }
.sv-optional { font-weight: 400; font-size: 11px; color: var(--c-text-3); margin-left: 4px; }
.sv-link {
  display: inline-flex; align-items: center; gap: 4px; margin-left: 4px;
  font: 500 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
  color: var(--c-text-3); transition: color var(--t);
}
.sv-link:hover { color: var(--c-text); }
.sv-actions { display: flex; gap: 2px; flex-shrink: 0; opacity: 0.7; transition: opacity var(--t); }
.sv-item:hover .sv-actions { opacity: 1; }
.sv-icon-btn {
  width: 32px; height: 32px; border-radius: 9px;
  display: grid; place-items: center; color: var(--c-text-3);
  transition: background var(--t), color var(--t);
}
.sv-icon-btn:hover { background: var(--c-info-light); color: var(--c-text); }
.sv-icon-btn.danger:hover { background: color-mix(in srgb, var(--c-danger) 14%, transparent); color: var(--c-danger); }

.sv-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 64px 24px; color: var(--c-text-3); }
.sv-empty-icon { font-size: 40px; }

.field-hint { font-size: 12px; color: var(--c-text-3); margin-top: 6px; }
.field-warn { color: var(--c-warning, #d97706); font-weight: 600; }

@media (max-width: 640px) {
  .sv-head { align-items: flex-start; }
  .sv-search { max-width: none; }
  .sv-actions { opacity: 1; }
}
</style>
