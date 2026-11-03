<template>
  <div class="hub">
    <!-- ── 科目列表（桌面侧栏 / 手机横向标签） ─────────────────── -->
    <aside class="hub-sidebar">
      <div class="hub-section-label">科目</div>

      <div v-if="loadingSubjects" class="hub-subject-list">
        <div v-for="i in 3" :key="i" class="sk hub-subject-sk" />
      </div>

      <nav v-else class="hub-subject-list" aria-label="科目">
        <button
          v-for="(s, i) in subjects"
          :key="s.id"
          v-reveal="i"
          :class="['hub-subject-item', { active: activeId === s.id }]"
          :style="{ '--accent': s.color || 'var(--c-primary)' }"
          :aria-current="activeId === s.id ? 'true' : undefined"
          @click="selectSubject(s)"
        >
          <span class="hub-subject-icon">{{ s.icon }}</span>
          <span class="hub-subject-name">{{ s.name }}</span>
          <span v-if="cache[s.id]" class="hub-subject-count">{{ cache[s.id]!.length }}</span>
        </button>
      </nav>
    </aside>

    <!-- ── 视频列表 ─────────────────────────────────────────── -->
    <section class="hub-content">
      <Transition name="page" mode="out-in">
        <div v-if="active" :key="active.id" class="hub-panel" :style="{ '--accent': active.color || 'var(--c-primary)' }">
          <header class="hub-hero">
            <span class="hub-hero-icon">{{ active.icon }}</span>
            <div class="hub-hero-text">
              <h1 class="hub-hero-title">{{ active.name }}</h1>
              <p class="hub-hero-desc">{{ active.description || '精选 B 站课程合集' }}</p>
            </div>
            <div class="hub-hero-stat">
              <strong>{{ videos.length }}</strong>
              <span>个视频</span>
            </div>
          </header>

          <!-- 筛选栏：关键词 + 阶段 -->
          <div v-if="videos.length" class="hub-filter">
            <label class="hub-search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
              <input v-model="keyword" type="search" placeholder="搜索本科目的视频…" aria-label="搜索视频" />
              <kbd v-if="!keyword" class="hub-kbd">/</kbd>
            </label>
            <div class="hub-stage-track" role="tablist" aria-label="按阶段筛选">
              <span class="hub-stage-thumb" :style="thumbStyle" aria-hidden="true" />
              <button
                v-for="(o, i) in stageOptions"
                :key="o.key"
                :ref="el => (stageBtns[i] = el as HTMLElement)"
                role="tab"
                :aria-selected="stage === o.key"
                :class="['hub-stage-opt', { on: stage === o.key }]"
                :style="{ '--lv': o.color }"
                @click="stage = o.key"
              >
                <span v-if="o.step" class="hub-stage-dot">{{ o.step }}</span>
                {{ o.label }}
                <span class="hub-stage-count">{{ o.count }}</span>
              </button>
            </div>
          </div>

          <div v-if="loadingVideos" class="hub-video-list">
            <div v-for="i in 4" :key="i" class="sk hub-video-sk" />
          </div>

          <div v-else-if="videos.length === 0" class="hub-empty">
            <span class="empty-icon">📹</span>
            <p>这个科目还没有视频，过段时间再来看看</p>
          </div>

          <div v-else-if="groups.length === 0" class="hub-empty">
            <span class="empty-icon">🔍</span>
            <p>没有符合条件的视频</p>
            <button class="btn btn-secondary btn-sm" @click="resetFilter">清除筛选</button>
          </div>

          <div v-else class="hub-stages">
            <section v-for="g in groups" :key="g.key" class="hub-stage" :style="{ '--lv': g.color }">
              <header class="hub-stage-head">
                <span class="hub-stage-badge">{{ g.step || '·' }}</span>
                <div class="hub-stage-text">
                  <h2>{{ g.label }}</h2>
                  <p>{{ g.hint }}</p>
                </div>
                <span class="hub-stage-num">{{ g.items.length }} 个视频</span>
              </header>
              <ol class="hub-video-list">
                <li v-for="(v, i) in g.items" :key="v.index" v-reveal="i" class="hub-video-item lift">
                  <a :href="cleanUrl(v.url)" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer" class="hub-video-main">
                    <span class="hub-video-num">{{ String(v.index + 1).padStart(2, '0') }}</span>
                    <span class="hub-video-info">
                      <span class="hub-video-title">{{ v.title }}</span>
                      <span class="hub-video-meta">
                        <span class="hub-bili-tag">bilibili</span>
                        <span v-if="bvid(v.url)" class="hub-video-bv">{{ bvid(v.url) }}</span>
                      </span>
                    </span>
                    <span class="hub-video-play" aria-hidden="true">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l11-6.5a1 1 0 0 0 0-1.72l-11-6.5A1 1 0 0 0 8 5.5z" /></svg>
                      <span>去观看</span>
                    </span>
                  </a>
                  <button
                    class="hub-copy press"
                    :class="copyState[v.index]"
                    :aria-label="`复制《${v.title}》的链接`"
                    :title="copyLabel(v.index)"
                    @click="copyUrl(v)"
                  >
                    <svg v-if="copyState[v.index] === 'ok'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
                    <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="2.5" /><path d="M5 15V6a2 2 0 0 1 2-2h9" /></svg>
                  </button>
                </li>
              </ol>
            </section>
          </div>
        </div>

        <div v-else-if="!loadingSubjects" class="hub-empty">
          <span class="empty-icon">📚</span>
          <p>暂时还没有科目</p>
        </div>
      </Transition>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { subjectApi } from '@/course/api/course'
import { useToast } from '@/course/composables/useToast'
import type { Subject, BilibiliVideo, VideoLevel } from '@/course/types'
import { LEVELS } from '@/course/levels'

function useEventListener<K extends keyof WindowEventMap>(t: Window, type: K, fn: (e: WindowEventMap[K]) => void) {
  onMounted(() => t.addEventListener(type, fn))
  onBeforeUnmount(() => t.removeEventListener(type, fn))
}

const route = useRoute()
const router = useRouter()
const toast = useToast()

const subjects = ref<Subject[]>([])
const activeId = ref<number | null>(null)
const active = computed(() => subjects.value.find(s => s.id === activeId.value) ?? null)
const loadingSubjects = ref(false)
const loadingVideos = ref(false)
// 每个科目的视频只请求一次，切换科目即时显示
const cache = reactive<Record<number, BilibiliVideo[]>>({})
const videos = computed(() => (activeId.value != null ? cache[activeId.value] : undefined) ?? [])

// ── 筛选：关键词 + 阶段（入门/基础/进阶，一个视频可出现在多个阶段） ──
const UNLEVELED = '未分级'
type StageKey = 'all' | VideoLevel | typeof UNLEVELED

const keyword = ref('')
const stage = ref<StageKey>('all')

const searched = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  return k ? videos.value.filter(v => v.title.toLowerCase().includes(k)) : videos.value
})

const stageDefs = computed(() => {
  const defs = LEVELS.map(l => ({
    key: l.key as StageKey, label: l.key as string, step: l.step, hint: l.hint, color: l.color,
    items: searched.value.filter(v => v.levels.includes(l.key)),
  }))
  const rest = searched.value.filter(v => !v.levels.length)
  if (videos.value.some(v => !v.levels.length)) {
    defs.push({ key: UNLEVELED as StageKey, label: UNLEVELED as string, step: 0, hint: '尚未归入阶段的视频', color: 'var(--c-text-3)', items: rest })
  }
  return defs
})

const stageOptions = computed(() => [
  { key: 'all' as StageKey, label: '全部', step: 0, color: 'var(--accent)', count: searched.value.length },
  ...stageDefs.value.map(d => ({ key: d.key, label: d.label, step: d.step, color: d.color, count: d.items.length })),
])

const groups = computed(() =>
  stageDefs.value.filter(d => d.items.length && (stage.value === 'all' || stage.value === d.key)),
)

// 选中态滑块：跟随当前按钮的位置与宽度
const stageBtns = ref<HTMLElement[]>([])
const thumbStyle = ref<Record<string, string>>({})
function syncThumb() {
  const i = stageOptions.value.findIndex(o => o.key === stage.value)
  const el = stageBtns.value[i]
  if (!el) return
  const color = stageOptions.value[i]!.color
  thumbStyle.value = { width: `${el.offsetWidth}px`, transform: `translateX(${el.offsetLeft}px)`, '--lv': color }
}
watch([stage, stageOptions, activeId], () => nextTick(syncThumb), { flush: 'post' })
useEventListener(window, 'resize', syncThumb)

function resetFilter() {
  keyword.value = ''
  stage.value = 'all'
}

// 按 / 聚焦搜索框
useEventListener(window, 'keydown', (e: KeyboardEvent) => {
  if (e.key !== '/' || (e.target as HTMLElement)?.closest('input, textarea')) return
  const input = document.querySelector<HTMLInputElement>('.hub-search input')
  if (input) { e.preventDefault(); input.focus() }
})

function bvid(url: string) {
  return url.match(/BV[0-9A-Za-z]{10}/)?.[0] ?? ''
}

// ── 复制链接 ─────────────────────────────────────────────────
const copyState = reactive<Record<number, string>>({})

function copyLabel(index: number) {
  return copyState[index] === 'ok' ? '已复制' : '复制链接'
}

// B 站链接统一成 https、去掉 spm_id_from / vd_source 等追踪参数（只保留分P），
// 打开时不带 Referer——来自陌生站点的 Referer 与追踪参数容易触发 B 站风控返回 412
function cleanUrl(raw: string) {
  try {
    const u = new URL(raw.trim().replace(/^http:\/\//i, 'https://'))
    if (!/(^|\.)bilibili\.com$|(^|\.)b23\.tv$/.test(u.hostname)) return u.href
    const p = u.searchParams.get('p')
    u.search = p ? `?p=${p}` : ''
    u.hash = ''
    return u.href
  } catch {
    return raw.trim()
  }
}

// navigator.clipboard 只在 HTTPS / localhost 可用；HTTP 下退回 execCommand
function legacyCopy(text: string) {
  const ta = document.createElement('textarea')
  ta.value = text
  ta.setAttribute('readonly', '')
  ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none'
  document.body.appendChild(ta)
  ta.select()
  ta.setSelectionRange(0, text.length) // iOS Safari
  let ok = false
  try { ok = document.execCommand('copy') } catch { ok = false }
  document.body.removeChild(ta)
  return ok
}

async function copyUrl(v: BilibiliVideo) {
  const text = cleanUrl(v.url)
  let ok = false
  if (window.isSecureContext && navigator.clipboard) {
    try { await navigator.clipboard.writeText(text); ok = true } catch { ok = false }
  }
  if (!ok) ok = legacyCopy(text)
  if (ok) {
    copyState[v.index] = 'ok'
    toast.success('链接已复制')
  } else {
    toast.error(`复制失败，请手动复制：${text}`)
  }
  setTimeout(() => { copyState[v.index] = 'idle' }, 2000)
}

// ── 科目切换（记在 URL 上，刷新/分享后仍停留在同一科目） ──────
async function loadVideos(id: number) {
  if (cache[id]) return
  const { data } = await subjectApi.videos(id)
  cache[id] = data
}

async function selectSubject(s: Subject) {
  if (activeId.value === s.id) return
  activeId.value = s.id
  resetFilter()
  router.replace({ query: { ...route.query, s: String(s.id) } })
  if (cache[s.id]) return
  loadingVideos.value = true
  try {
    await loadVideos(s.id)
  } finally {
    loadingVideos.value = false
  }
}

onMounted(async () => {
  loadingSubjects.value = true
  try {
    const { data } = await subjectApi.list()
    subjects.value = data
    const fromUrl = data.find(s => String(s.id) === route.query.s)
    const first = fromUrl ?? data[0]
    if (first) await selectSubject(first)
    // 其余科目后台预取，用于侧栏数量与即时切换
    data.forEach(s => loadVideos(s.id).catch(() => {}))
  } finally {
    loadingSubjects.value = false
  }
})
</script>

<style scoped>
.hub {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  min-height: calc(100dvh - var(--header-h));
  max-width: 1280px;
  margin: 0 auto;
}

/* ── 侧栏 ─────────────────────────────────────────────────── */
.hub-sidebar {
  position: sticky;
  top: var(--header-h);
  align-self: start;
  max-height: calc(100dvh - var(--header-h));
  overflow-y: auto;
  padding: 24px 12px 24px 24px;
}
.hub-section-label {
  font-size: 12px; font-weight: 600; letter-spacing: 0.06em;
  color: var(--c-text-3); padding: 0 12px 10px;
}
.hub-subject-list { display: flex; flex-direction: column; gap: 4px; }
.hub-subject-sk { height: 44px; }

.hub-subject-item {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 10px 12px;
  border-radius: var(--r);
  font-size: 14px; font-weight: 500; color: var(--c-text-2);
  text-align: left;
  transition: background var(--t), color var(--t), box-shadow var(--t);
}
.hub-subject-item:hover { background: var(--c-surface); color: var(--c-text); }
.hub-subject-item.active {
  background: var(--c-surface);
  color: var(--c-text);
  box-shadow: var(--shadow-sm), inset 0 0 0 1px var(--c-border);
}
.hub-subject-item::before {
  content: '';
  position: absolute; left: 0; top: 50%;
  width: 3px; height: 0; border-radius: 3px;
  background: var(--accent);
  transform: translateY(-50%);
  transition: height 0.28s var(--ease-spring);
}
.hub-subject-item.active::before { height: 20px; }
.hub-subject-icon {
  width: 30px; height: 30px; border-radius: 9px;
  display: grid; place-items: center; font-size: 16px; flex-shrink: 0;
  background: color-mix(in srgb, var(--accent) 14%, transparent);
}
.hub-subject-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hub-subject-count {
  font-size: 12px; font-variant-numeric: tabular-nums;
  padding: 1px 8px; border-radius: var(--r-full);
  background: var(--c-info-light); color: var(--c-text-3);
}
.hub-subject-item.active .hub-subject-count {
  background: color-mix(in srgb, var(--accent) 16%, transparent);
  color: color-mix(in srgb, var(--accent) 70%, #0f172a);
}

/* ── 内容区 ───────────────────────────────────────────────── */
.hub-content { padding: 24px 24px 48px 12px; min-width: 0; }

.hub-hero {
  position: relative;
  display: flex; align-items: center; gap: 16px;
  padding: 24px;
  border-radius: var(--r-lg);
  background:
    radial-gradient(120% 140% at 0% 0%, color-mix(in srgb, var(--accent) 20%, transparent) 0%, transparent 55%),
    var(--c-surface);
  border: 1px solid var(--c-border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.hub-hero-icon {
  width: 56px; height: 56px; border-radius: 16px;
  display: grid; place-items: center; font-size: 28px; flex-shrink: 0;
  background: color-mix(in srgb, var(--accent) 16%, var(--c-surface));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--accent) 22%, transparent);
}
.hub-hero-text { flex: 1; min-width: 0; }
.hub-hero-title { font-size: 22px; font-weight: 700; letter-spacing: -0.02em; color: var(--c-text); }
.hub-hero-desc { color: var(--c-text-2); margin-top: 2px; }
.hub-hero-stat { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.2; }
.hub-hero-stat strong { font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--c-text); }
.hub-hero-stat span { font-size: 12px; color: var(--c-text-3); }

/* ── 筛选栏 ───────────────────────────────────────────────── */
.hub-filter {
  position: sticky; top: calc(var(--header-h) + 8px); z-index: 5;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  margin-top: 16px; padding: 8px;
  background: var(--c-surface-glass, var(--c-surface));
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border: 1px solid var(--c-border); border-radius: var(--r-lg);
  box-shadow: var(--shadow-sm);
}
.hub-search {
  flex: 1 1 220px; min-width: 0;
  display: flex; align-items: center; gap: 8px;
  padding: 0 12px; height: 38px;
  background: var(--c-bg, transparent); border-radius: var(--r);
  box-shadow: inset 0 0 0 1px var(--c-border);
  color: var(--c-text-3); cursor: text;
  transition: box-shadow var(--t);
}
.hub-search:focus-within { box-shadow: inset 0 0 0 1.5px var(--accent), 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent); }
.hub-search input { flex: 1; min-width: 0; border: none; outline: none; background: transparent; color: var(--c-text); font-size: 14px; }
.hub-search input::-webkit-search-cancel-button { cursor: pointer; }
.hub-kbd {
  font: 600 11px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
  padding: 3px 6px; border-radius: 6px; color: var(--c-text-3);
  box-shadow: inset 0 0 0 1px var(--c-border), 0 1px 0 var(--c-border);
}

.hub-stage-track {
  position: relative; isolation: isolate;
  display: flex; gap: 2px; padding: 3px;
  border-radius: var(--r);
  background: color-mix(in srgb, var(--c-text-3) 10%, transparent);
  overflow-x: auto; scrollbar-width: none; max-width: 100%;
}
.hub-stage-track::-webkit-scrollbar { display: none; }
.hub-stage-thumb {
  position: absolute; z-index: -1; top: 3px; bottom: 3px; left: 0;
  border-radius: calc(var(--r) - 3px);
  background: var(--c-surface);
  box-shadow: var(--shadow-sm), inset 0 -2px 0 var(--lv);
  transition: transform 0.32s var(--ease-spring), width 0.32s var(--ease-spring), box-shadow var(--t);
}
.hub-stage-opt {
  display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0;
  height: 32px; padding: 0 12px; border-radius: calc(var(--r) - 3px);
  font-size: 13px; font-weight: 600; color: var(--c-text-3); white-space: nowrap;
  transition: color var(--t);
}
.hub-stage-opt:hover, .hub-stage-opt.on { color: var(--c-text); }
.hub-stage-dot {
  width: 18px; height: 18px; border-radius: 6px;
  display: grid; place-items: center; font-size: 11px;
  color: var(--lv); background: color-mix(in srgb, var(--lv) 15%, transparent);
  transition: background var(--t), color var(--t);
}
.hub-stage-opt.on .hub-stage-dot { color: #fff; background: var(--lv); }
.hub-stage-count { font-size: 11px; font-weight: 500; font-variant-numeric: tabular-nums; color: var(--c-text-3); }

/* ── 阶段分区 ─────────────────────────────────────────────── */
.hub-stages { display: flex; flex-direction: column; gap: 28px; margin-top: 20px; }
.hub-stage { position: relative; }
.hub-stage-head {
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 10px; margin-bottom: 2px;
  border-bottom: 1px dashed color-mix(in srgb, var(--lv) 35%, var(--c-border));
}
.hub-stage-badge {
  width: 34px; height: 34px; border-radius: 11px; flex-shrink: 0;
  display: grid; place-items: center; font-size: 15px; font-weight: 800; color: #fff;
  background: linear-gradient(135deg, var(--lv), color-mix(in srgb, var(--lv) 70%, #000));
  box-shadow: 0 4px 12px color-mix(in srgb, var(--lv) 30%, transparent);
}
.hub-stage-text { flex: 1; min-width: 0; }
.hub-stage-text h2 { font-size: 17px; font-weight: 700; color: var(--c-text); letter-spacing: -0.01em; }
.hub-stage-text p { font-size: 12px; color: var(--c-text-3); }
.hub-stage-num {
  font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums;
  padding: 2px 10px; border-radius: var(--r-full);
  color: var(--lv); background: color-mix(in srgb, var(--lv) 12%, transparent);
}
.hub-stage .hub-video-list { grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); }
.hub-stage .hub-video-item:hover { border-color: color-mix(in srgb, var(--lv) 45%, var(--c-border)); }
.hub-stage .hub-video-num { color: color-mix(in srgb, var(--lv) 80%, #0f172a); background: color-mix(in srgb, var(--lv) 12%, transparent); }

/* ── 视频卡片 ─────────────────────────────────────────────── */
.hub-video-list {
  display: grid; gap: 10px; margin-top: 16px;
}
.hub-video-sk { height: 76px; border-radius: var(--r); }

.hub-video-item {
  display: flex; align-items: stretch;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.hub-video-item:hover { border-color: color-mix(in srgb, var(--accent) 45%, var(--c-border)); box-shadow: var(--shadow); }

.hub-video-main {
  flex: 1; min-width: 0;
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px;
  color: inherit;
}
.hub-video-main:hover { color: inherit; }
.hub-video-num {
  width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
  display: grid; place-items: center;
  font-size: 13px; font-weight: 700; font-variant-numeric: tabular-nums;
  color: color-mix(in srgb, var(--accent) 75%, #0f172a);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
}
.hub-video-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.hub-video-title {
  font-size: 15px; font-weight: 600; color: var(--c-text); line-height: 1.45;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.hub-video-meta { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--c-text-3); }
.hub-bili-tag {
  padding: 0 6px; border-radius: 4px; font-weight: 600;
  color: var(--c-bilibili); background: #fff0f5;
}
.hub-video-bv { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

.hub-video-play {
  display: inline-flex; align-items: center; gap: 6px; flex-shrink: 0;
  height: 34px; padding: 0 14px; border-radius: var(--r-full);
  font-size: 13px; font-weight: 600; color: #fff;
  background: var(--c-bilibili);
  box-shadow: 0 4px 12px rgba(251, 114, 153, 0.3);
  transition: transform var(--t), box-shadow var(--t);
}
.hub-video-main:hover .hub-video-play { transform: translateX(2px); box-shadow: 0 6px 16px rgba(251, 114, 153, 0.4); }

.hub-copy {
  width: 52px; flex-shrink: 0;
  display: grid; place-items: center;
  border-left: 1px solid var(--c-border);
  color: var(--c-text-3);
  transition: background var(--t), color var(--t);
}
.hub-copy:hover { background: var(--c-info-light); color: var(--c-text); }
.hub-copy.ok { color: var(--c-success); }

.hub-empty {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 64px 24px; color: var(--c-text-3); text-align: center;
}
.empty-icon { font-size: 40px; }

/* ── 手机 ─────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .hub { grid-template-columns: minmax(0, 1fr); align-content: start; min-height: 0; }
  .hub-sidebar { min-width: 0; }

  .hub-sidebar {
    position: sticky; top: var(--header-h); z-index: 10;
    max-height: none; overflow: visible;
    padding: 10px 0;
    background: var(--c-surface-glass);
    backdrop-filter: saturate(180%) blur(14px);
    -webkit-backdrop-filter: saturate(180%) blur(14px);
    border-bottom: 1px solid var(--c-border);
  }
  .hub-section-label { display: none; }
  .hub-subject-list {
    flex-direction: row; gap: 8px;
    overflow-x: auto; scroll-snap-type: x proximity; scroll-padding-inline: 16px;
    padding: 0 16px; scrollbar-width: none;
  }
  .hub-subject-list::-webkit-scrollbar { display: none; }
  .hub-subject-sk { width: 96px; height: 38px; flex-shrink: 0; border-radius: var(--r-full); }
  .hub-subject-item {
    width: auto; flex-shrink: 0; scroll-snap-align: start;
    padding: 6px 14px 6px 6px; border-radius: var(--r-full);
    background: var(--c-surface); box-shadow: inset 0 0 0 1px var(--c-border);
  }
  .hub-subject-item::before { display: none; }
  .hub-subject-item.active {
    background: var(--accent); color: #fff;
    box-shadow: 0 4px 12px color-mix(in srgb, var(--accent) 35%, transparent);
  }
  .hub-subject-item.active .hub-subject-icon { background: rgba(255,255,255,0.25); }
  .hub-subject-item.active .hub-subject-count { background: rgba(255,255,255,0.25); color: #fff; }
  .hub-subject-icon { width: 26px; height: 26px; border-radius: 50%; font-size: 14px; }

  .hub-content { padding: 16px 16px 32px; }
  .hub-hero { padding: 16px; gap: 12px; }
  .hub-hero-icon { width: 44px; height: 44px; font-size: 22px; border-radius: 12px; }
  .hub-hero-title { font-size: 18px; }
  .hub-hero-desc { font-size: 13px; }
  .hub-hero-stat strong { font-size: 22px; }

  .hub-video-main { padding: 12px; gap: 12px; }
  .hub-video-num { width: 34px; height: 34px; font-size: 12px; border-radius: 10px; }
  .hub-video-title { font-size: 14px; }
  .hub-video-play span { display: none; }
  .hub-video-play { width: 34px; padding: 0; justify-content: center; }
  .hub-copy { width: 44px; }
  .hub-filter { top: calc(var(--header-h) + 64px); }
  .hub-stage .hub-video-list { grid-template-columns: minmax(0, 1fr); }
  .hub-kbd { display: none; }
}
</style>
