<template>
  <div class="sc">
    <header class="sc-head">
      <div>
        <h1 class="sc-title">科目管理</h1>
        <p class="sc-sub">
          <template v-if="loading">加载中…</template>
          <template v-else>共 {{ subjects.length }} 个科目 · {{ totalVideos }} 个视频</template>
        </p>
      </div>
      <button class="btn btn-primary" @click="openCreate">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M12 5v14M5 12h14" /></svg>
        新增科目
      </button>
    </header>

    <div v-if="loading" class="sc-grid">
      <div v-for="i in 6" :key="i" class="skeleton sc-sk" />
    </div>

    <div v-else-if="subjects.length === 0" class="sc-empty">
      <span class="sc-empty-icon">🗂️</span>
      <p>还没有科目</p>
      <button class="btn btn-primary btn-sm" @click="openCreate">创建第一个科目</button>
    </div>

    <div v-else class="sc-grid">
      <article
        v-for="s in subjects"
        :key="s.id"
        class="sc-card"
        :style="{ '--accent': s.color || 'var(--c-primary)' }"
      >
        <router-link :to="videosLink(s)" class="sc-main">
          <div class="sc-row">
            <span class="sc-icon">{{ s.icon || '📖' }}</span>
            <div class="sc-name-wrap">
              <h2 class="sc-name">{{ s.name }}</h2>
              <p :class="['sc-desc', { muted: !s.description }]">{{ s.description || '暂无描述' }}</p>
            </div>
          </div>

          <div class="sc-stats">
            <div class="sc-count">
              <strong>{{ counts[s.id]?.total ?? '–' }}</strong>
              <span>个视频</span>
            </div>
            <div v-if="counts[s.id]?.total" class="sc-dist" :aria-label="distLabel(s.id)">
              <div class="sc-bar">
                <span
                  v-for="l in LEVELS"
                  :key="l.key"
                  :style="{ flexGrow: counts[s.id]!.levels[l.key], background: l.color }"
                />
              </div>
              <div class="sc-legend">
                <span v-for="l in LEVELS.filter(x => counts[s.id]!.levels[x.key])" :key="l.key" :style="{ '--lv': l.color }">
                  {{ l.key }} {{ counts[s.id]!.levels[l.key] }}
                </span>
                <span v-if="counts[s.id]!.none" class="sc-none">未分级 {{ counts[s.id]!.none }}</span>
              </div>
            </div>
            <p v-else-if="counts[s.id]" class="sc-dist-empty">还没有视频</p>
          </div>
        </router-link>

        <footer class="sc-foot">
          <router-link :to="videosLink(s)" class="sc-manage">
            管理视频
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M9 6l6 6-6 6" /></svg>
          </router-link>
          <div class="sc-actions">
            <button class="sc-icon-btn" title="编辑科目" aria-label="编辑科目" @click="openEdit(s)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20h4L19 9l-4-4L4 16v4z" /><path d="M13.5 6.5l4 4" /></svg>
            </button>
            <button class="sc-icon-btn danger" title="删除科目" aria-label="删除科目" @click="handleDelete(s)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3" /></svg>
            </button>
          </div>
        </footer>
      </article>
    </div>

    <!-- 新增 / 编辑 -->
    <Teleport to="#course-layer">
      <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
        <div class="modal" style="max-width:520px">
          <div class="modal-header">
            <span>{{ editTarget ? '编辑科目' : '新增科目' }}</span>
            <button class="modal-close" @click="showForm = false">✕</button>
          </div>
          <div class="modal-body sc-form">
            <!-- 实时预览 -->
            <div class="sc-preview" :style="{ '--accent': form.color || 'var(--c-primary)' }">
              <span class="sc-icon">{{ form.icon || '📖' }}</span>
              <div class="sc-name-wrap">
                <div class="sc-name">{{ form.name || '科目名称' }}</div>
                <p :class="['sc-desc', { muted: !form.description }]">{{ form.description || '一句话介绍这个科目' }}</p>
              </div>
            </div>

            <div class="field">
              <label class="field-label">科目名称</label>
              <input v-model="form.name" class="input" maxlength="20" placeholder="如：计算机" />
            </div>
            <div class="field">
              <label class="field-label">描述</label>
              <textarea v-model="form.description" class="textarea" rows="2" maxlength="60" placeholder="一句话介绍，显示在学生端科目页顶部" />
            </div>
            <div class="field">
              <label class="field-label">搜索关键词</label>
              <input v-model="form.keywords" class="input" maxlength="200" placeholder="逗号分隔，如：数据结构, 算法入门, 王道考研" />
              <p class="field-hint">学生端可一键复制，用于在 B 站搜索相关教学视频</p>
            </div>
            <div class="sc-form-grid">
              <div class="field">
                <label class="field-label">图标</label>
                <div class="sc-emoji-row">
                  <input v-model="form.icon" class="input sc-emoji-input" maxlength="2" aria-label="自定义图标" />
                  <button
                    v-for="e in EMOJIS"
                    :key="e"
                    type="button"
                    :class="['sc-emoji', { on: form.icon === e }]"
                    @click="form.icon = e"
                  >{{ e }}</button>
                </div>
              </div>
              <div class="field">
                <label class="field-label">主题色</label>
                <div class="sc-swatches">
                  <button
                    v-for="c in COLORS"
                    :key="c"
                    type="button"
                    :class="['sc-swatch', { on: form.color.toLowerCase() === c }]"
                    :style="{ background: c }"
                    :aria-label="`主题色 ${c}`"
                    @click="form.color = c"
                  />
                  <label class="sc-swatch sc-swatch-custom" title="自定义颜色">
                    <input v-model="form.color" type="color" />
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showForm = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" :disabled="!form.name.trim()" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { useToast } from '@/course/composables/useToast'
import { useConfirm } from '@/course/composables/useConfirm'
import { adminSubjectApi } from '@/course/api/admin'
import { LEVELS } from '@/course/levels'
import type { Subject, VideoLevel } from '@/course/types'

const EMOJIS = ['📐', '🔤', '💻', '📈', '📜', '🎨', '🔬', '🎵']
const COLORS = ['#4f46e5', '#2563eb', '#0891b2', '#16a34a', '#ca8a04', '#ea580c', '#dc2626', '#db2777']

const toast = useToast()
const { confirm } = useConfirm()
const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const subjects = ref<Subject[]>([])
const editTarget = ref<Subject | null>(null)
const blank = () => ({ name: '', description: '', icon: '📖', color: COLORS[1]!, keywords: '' })
const form = ref(blank())

interface Count { total: number; none: number; levels: Record<VideoLevel, number> }
const counts = reactive<Record<number, Count>>({})
const totalVideos = computed(() => Object.values(counts).reduce((n, c) => n + c.total, 0))

function videosLink(s: Subject) {
  return `/admin/course/subjects/${s.id}/videos`
}

function distLabel(id: number) {
  const c = counts[id]!
  return LEVELS.map(l => `${l.key} ${c.levels[l.key]}`).join('，')
}

async function loadCount(id: number) {
  const { data } = await adminSubjectApi.listVideos(id)
  const levels = { 入门: 0, 基础: 0, 进阶: 0 } as Record<VideoLevel, number>
  data.forEach(v => v.levels.forEach(l => { levels[l]++ }))
  counts[id] = { total: data.length, none: data.filter(v => !v.levels.length).length, levels }
}

onMounted(async () => {
  loading.value = true
  try {
    subjects.value = (await adminSubjectApi.list()).data
  } finally {
    loading.value = false
  }
  subjects.value.forEach(s => loadCount(s.id).catch(() => {}))
})

function openCreate() {
  editTarget.value = null
  form.value = blank()
  showForm.value = true
}

function openEdit(s: Subject) {
  editTarget.value = s
  form.value = { name: s.name, description: s.description, icon: s.icon || '📖', color: s.color || COLORS[1]!, keywords: s.keywords ?? '' }
  showForm.value = true
}

async function handleSave() {
  if (!form.value.name.trim()) return
  saving.value = true
  try {
    if (editTarget.value) {
      const { data } = await adminSubjectApi.update(editTarget.value.id, form.value)
      const i = subjects.value.findIndex(s => s.id === editTarget.value!.id)
      if (i !== -1) subjects.value[i] = data
    } else {
      const { data } = await adminSubjectApi.create(form.value)
      subjects.value.push(data)
      counts[data.id] = { total: 0, none: 0, levels: { 入门: 0, 基础: 0, 进阶: 0 } }
    }
    showForm.value = false
    toast.success('保存成功')
  } finally {
    saving.value = false
  }
}

async function handleDelete(s: Subject) {
  const n = counts[s.id]?.total ?? 0
  const ok = await confirm({
    title: `删除「${s.name}」`,
    message: n ? `该科目下有 ${n} 个视频，删除后学生端将无法再看到它们。确认删除？` : '确认删除这个科目？',
    confirmText: '删除',
    type: 'danger',
  })
  if (!ok) return
  await adminSubjectApi.delete(s.id)
  subjects.value = subjects.value.filter(x => x.id !== s.id)
  delete counts[s.id]
  toast.success('已删除')
}
</script>

<style scoped>
.sc-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.sc-title { font-size: 22px; font-weight: 700; color: var(--c-text); letter-spacing: -0.01em; }
.sc-sub { font-size: 13px; color: var(--c-text-3); margin-top: 2px; }
.sc-head .btn { gap: 6px; }

.sc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.sc-sk { height: 206px; border-radius: var(--r-lg); }

/* ── 卡片 ───────────────────────────────────────────────── */
.sc-card {
  position: relative;
  display: flex; flex-direction: column;
  border-radius: var(--r-lg);
  background:
    radial-gradient(120% 90% at 0% 0%, color-mix(in srgb, var(--accent) 14%, transparent) 0%, transparent 60%),
    var(--c-surface);
  border: 1px solid var(--c-border);
  overflow: hidden;
  transition: border-color var(--t), box-shadow var(--t), transform var(--t);
}
.sc-card::before {
  content: ''; position: absolute; inset: 0 0 auto 0; height: 3px;
  background: var(--accent);
}
.sc-card:hover {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--c-border));
  box-shadow: 0 10px 28px color-mix(in srgb, var(--accent) 14%, transparent);
  transform: translateY(-2px);
}

.sc-main { flex: 1; display: flex; flex-direction: column; gap: 16px; padding: 20px 18px 16px; color: inherit; }
.sc-main:hover { color: inherit; }
.sc-row { display: flex; gap: 12px; align-items: flex-start; }
.sc-icon {
  width: 44px; height: 44px; border-radius: 13px; flex-shrink: 0;
  display: grid; place-items: center; font-size: 22px;
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 25%, transparent);
}
.sc-name-wrap { min-width: 0; flex: 1; }
.sc-name { font-size: 16px; font-weight: 700; color: var(--c-text); line-height: 1.3; }
.sc-desc {
  font-size: 13px; color: var(--c-text-2); margin-top: 3px; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.sc-desc.muted { color: var(--c-text-3); font-style: italic; }

.sc-stats { display: flex; align-items: flex-end; gap: 16px; margin-top: auto; }
.sc-count { display: flex; flex-direction: column; line-height: 1.1; flex-shrink: 0; }
.sc-count strong { font-size: 26px; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--c-text); }
.sc-count span { font-size: 12px; color: var(--c-text-3); }
.sc-dist { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; padding-bottom: 2px; }
.sc-bar { display: flex; gap: 2px; height: 6px; border-radius: 99px; overflow: hidden; background: color-mix(in srgb, var(--c-text-3) 18%, transparent); }
.sc-bar span { flex-basis: 0; min-width: 0; }
.sc-legend { display: flex; flex-wrap: wrap; gap: 4px 10px; font-size: 11px; color: var(--c-text-3); font-variant-numeric: tabular-nums; }
.sc-legend span::before {
  content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  margin-right: 4px; vertical-align: 1px; background: var(--lv);
}
.sc-legend .sc-none::before { background: var(--c-text-3); }
.sc-dist-empty { font-size: 12px; color: var(--c-text-3); padding-bottom: 4px; }

.sc-foot {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 10px 10px 18px;
  border-top: 1px solid var(--c-border);
}
.sc-manage {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 600;
  color: color-mix(in srgb, var(--accent) 65%, var(--c-text));
}
.sc-manage svg { transition: transform var(--t); }
.sc-manage:hover { color: var(--c-text); }
.sc-manage:hover svg { transform: translateX(3px); }
.sc-actions { display: flex; gap: 4px; }
.sc-icon-btn {
  width: 32px; height: 32px; border-radius: 9px;
  display: grid; place-items: center; color: var(--c-text-3);
  transition: background var(--t), color var(--t);
}
.sc-icon-btn:hover { background: var(--c-info-light); color: var(--c-text); }
.sc-icon-btn.danger:hover { background: color-mix(in srgb, var(--c-danger) 14%, transparent); color: var(--c-danger); }

.sc-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 72px 24px; color: var(--c-text-3); }
.sc-empty-icon { font-size: 40px; }

/* ── 表单 ───────────────────────────────────────────────── */
.sc-form { display: flex; flex-direction: column; gap: 14px; padding-top: 20px; }
.sc-preview {
  display: flex; gap: 12px; align-items: center;
  padding: 14px; border-radius: var(--r);
  background: radial-gradient(120% 140% at 0% 0%, color-mix(in srgb, var(--accent) 18%, transparent) 0%, transparent 60%), var(--c-bg, transparent);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 30%, var(--c-border)), inset 3px 0 0 var(--accent);
}
.sc-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.sc-emoji-row, .sc-swatches { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.sc-emoji-input { width: 44px; height: 34px; padding: 0; text-align: center; font-size: 18px; }
.sc-emoji {
  width: 34px; height: 34px; border-radius: 9px; font-size: 17px;
  display: grid; place-items: center;
  transition: background var(--t), box-shadow var(--t);
}
.sc-emoji:hover { background: var(--c-info-light); }
.sc-emoji.on { background: var(--c-info-light); box-shadow: inset 0 0 0 1.5px var(--c-primary); }
.sc-swatch {
  position: relative; width: 26px; height: 26px; border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.15);
  transition: transform var(--t), box-shadow var(--t);
}
.sc-swatch:hover { transform: scale(1.1); }
.sc-swatch.on { box-shadow: 0 0 0 2px var(--c-surface), 0 0 0 4px currentColor; color: var(--c-text-2); }
.sc-swatch-custom {
  cursor: pointer; overflow: hidden;
  background: conic-gradient(#ef4444, #eab308, #22c55e, #06b6d4, #6366f1, #d946ef, #ef4444);
}
.sc-swatch-custom input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

@media (max-width: 560px) {
  .sc-form-grid { grid-template-columns: 1fr; }
  .sc-head { align-items: flex-start; }
}
</style>
