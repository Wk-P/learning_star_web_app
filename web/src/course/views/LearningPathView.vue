<template>
  <div class="lp">
    <!-- 目录：桌面端左侧固定，手机端顶部横向滚动 -->
    <aside class="lp-toc" aria-label="目录">
      <div class="lp-toc-head">
        <span>目录</span>
        <span v-if="checkTotal" class="lp-progress" :title="`检查表已完成 ${checkDone}/${checkTotal}`">
          <span class="lp-progress-bar"><span :style="{ width: `${(checkDone / checkTotal) * 100}%` }" /></span>
          {{ checkDone }}/{{ checkTotal }}
        </span>
      </div>
      <nav class="lp-toc-list">
        <a
          v-for="c in chapters" :key="c.id" :href="`#${c.id}`"
          :class="{ active: c.id === activeId }"
          @click.prevent="jump(c.id)"
        >{{ c.title }}</a>
      </nav>
    </aside>

    <!-- 正文 -->
    <article ref="bodyEl" class="lp-body" @change="onCheck" v-html="html" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { marked } from 'marked'
import source from '@/course/content/learning-path.md?raw'
import { useAuthStore } from '@/core/stores/auth'

// ── 渲染 ─────────────────────────────────────────────────────
// 一级标题作为章节（目录项），链接新窗口打开且不带 Referer（B 站风控）
const chapters: Array<{ id: string; title: string }> = []
let checkIndex = 0

const renderer = new marked.Renderer()
renderer.heading = function ({ tokens, depth }) {
  const text = this.parser.parseInline(tokens)
  if (depth === 1) {
    const id = `ch-${chapters.length}`
    const plain = text.replace(/<[^>]+>/g, '')
    if (!/^学习路线图/.test(plain)) {
      chapters.push({ id, title: plain })
      return `<h1 id="${id}" class="lp-chapter">${text}</h1>`
    }
    return `<h1 class="lp-title">${text}</h1>`
  }
  return `<h${depth}>${text}</h${depth}>`
}
renderer.link = function ({ href, tokens }) {
  return `<a href="${href}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">${this.parser.parseInline(tokens)}</a>`
}
renderer.checkbox = function () {
  return `<input type="checkbox" class="lp-check" data-i="${checkIndex++}" aria-label="标记为已完成" />`
}

const html = marked.parse(source, { renderer, gfm: true, async: false }) as string
const checkTotal = checkIndex

// ── 检查表进度：按账号存在本机 ───────────────────────────────
const auth = useAuthStore()
const storeKey = computed(() => `learning-path-checks:${auth.username || 'guest'}`)
const done = ref<Set<number>>(new Set())
const checkDone = computed(() => done.value.size)

function loadChecks() {
  try {
    done.value = new Set(JSON.parse(localStorage.getItem(storeKey.value) ?? '[]'))
  } catch {
    done.value = new Set()
  }
  bodyEl.value?.querySelectorAll<HTMLInputElement>('.lp-check').forEach(el => {
    el.checked = done.value.has(Number(el.dataset.i))
    el.closest('li')?.classList.toggle('is-done', el.checked)
  })
}

function onCheck(e: Event) {
  const el = e.target as HTMLInputElement
  if (!el.classList.contains('lp-check')) return
  const next = new Set(done.value)
  const i = Number(el.dataset.i)
  if (el.checked) next.add(i)
  else next.delete(i)
  done.value = next
  el.closest('li')?.classList.toggle('is-done', el.checked)
  try { localStorage.setItem(storeKey.value, JSON.stringify([...next])) } catch { /* 隐私模式等 */ }
}

// ── 目录高亮与跳转 ───────────────────────────────────────────
const bodyEl = ref<HTMLElement>()
const activeId = ref(chapters[0]?.id ?? '')
let observer: IntersectionObserver | undefined

function jump(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  history.replaceState(null, '', `#${id}`)
}

onMounted(async () => {
  await nextTick()
  loadChecks()
  observer = new IntersectionObserver(
    entries => {
      const hit = entries.filter(e => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]
      if (hit) activeId.value = hit.target.id
    },
    { rootMargin: '-80px 0px -65% 0px' },
  )
  bodyEl.value?.querySelectorAll('.lp-chapter').forEach(h => observer!.observe(h))
  if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView()
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<style scoped>
.lp {
  max-width: 1180px; margin: 0 auto;
  padding: 1.5rem clamp(1rem, 4vw, 2rem) 4rem;
  display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 2rem; align-items: start;
}

/* ── 目录 ─────────────────────────────────────────────── */
.lp-toc {
  position: sticky; top: 76px; max-height: calc(100vh - 96px); overflow: auto;
  padding: 1rem; border-radius: 18px;
  background: var(--surface-1); border: 1px solid var(--border);
}
.lp-toc-head {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
  font-size: 0.8rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.6rem;
}
.lp-progress { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.lp-progress-bar { width: 56px; height: 6px; border-radius: 99px; background: var(--surface-2); overflow: hidden; }
.lp-progress-bar span { display: block; height: 100%; background: var(--primary); transition: width var(--t); }
.lp-toc-list { display: flex; flex-direction: column; gap: 2px; }
.lp-toc-list a {
  padding: 0.4rem 0.65rem; border-radius: 10px; font-size: 0.88rem; line-height: 1.45;
  color: var(--text-muted); transition: background var(--t), color var(--t);
}
.lp-toc-list a:hover { background: var(--surface-2); color: var(--text); }
.lp-toc-list a.active { background: var(--primary-dim); color: var(--primary); font-weight: 650; }

/* ── 正文排版 ─────────────────────────────────────────── */
.lp-body { color: var(--text); font-size: 15.5px; line-height: 1.8; min-width: 0; }
.lp-body :deep(.lp-title) {
  font-size: clamp(1.8rem, 4vw, 2.4rem); font-weight: 800; letter-spacing: -0.02em; margin-bottom: 1rem;
  background: linear-gradient(100deg, var(--primary), var(--secondary));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.lp-body :deep(.lp-chapter) {
  scroll-margin-top: 80px;
  font-size: clamp(1.35rem, 3vw, 1.7rem); font-weight: 780; letter-spacing: -0.01em;
  margin: 2.6rem 0 1rem; padding-bottom: 0.6rem; border-bottom: 2px solid var(--border-primary);
}
.lp-body :deep(h2) {
  font-size: 1.22rem; font-weight: 720; margin: 2rem 0 0.75rem;
  padding: 0.55rem 0.9rem; border-radius: 12px;
  background: var(--primary-dim); border-left: 4px solid var(--primary);
}
.lp-body :deep(h3) { font-size: 1.05rem; font-weight: 700; margin: 1.4rem 0 0.5rem; color: var(--primary); }
.lp-body :deep(h4) { font-size: 0.98rem; font-weight: 700; margin: 1.1rem 0 0.4rem; }
.lp-body :deep(p) { margin: 0.55rem 0; }
.lp-body :deep(strong) { font-weight: 700; }
.lp-body :deep(ul), .lp-body :deep(ol) { margin: 0.5rem 0 0.8rem; padding-left: 1.4rem; }
.lp-body :deep(ul) { list-style: disc; }
.lp-body :deep(ol) { list-style: decimal; }
.lp-body :deep(li) { margin: 0.18rem 0; padding-left: 0.2rem; }
.lp-body :deep(li::marker) { color: var(--primary); }
.lp-body :deep(hr) { border: none; height: 1px; background: var(--border); margin: 1.8rem 0; }
.lp-body :deep(blockquote) {
  margin: 0.9rem 0; padding: 0.75rem 1rem; border-radius: 12px;
  background: var(--surface-1); border: 1px solid var(--border); border-left: 4px solid var(--secondary);
  color: var(--text-muted);
}
.lp-body :deep(blockquote p) { margin: 0.25rem 0; }
.lp-body :deep(code) {
  padding: 0.12rem 0.42rem; border-radius: 6px; font-size: 0.88em;
  background: var(--surface-2); border: 1px solid var(--border);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.lp-body :deep(a) { color: var(--primary); text-decoration: underline; text-underline-offset: 3px; word-break: break-all; }
.lp-body :deep(table) {
  display: block; overflow-x: auto; width: 100%; border-collapse: collapse; margin: 0.8rem 0;
  font-size: 0.92rem;
}
.lp-body :deep(th), .lp-body :deep(td) { padding: 0.55rem 0.8rem; border: 1px solid var(--border-strong); text-align: left; white-space: nowrap; }
.lp-body :deep(th) { background: var(--primary-dim); font-weight: 700; }

/* 检查表 */
.lp-body :deep(li:has(> .lp-check)) { list-style: none; margin-left: -1.4rem; }
.lp-body :deep(.lp-check) {
  width: 18px; height: 18px; margin-right: 0.55rem; vertical-align: -3px;
  accent-color: var(--primary); cursor: pointer;
}
.lp-body :deep(li.is-done) { color: var(--text-subtle); text-decoration: line-through; }

@media (max-width: 900px) {
  .lp { grid-template-columns: 1fr; gap: 1rem; padding-top: 1rem; }
  .lp-toc { position: sticky; top: 60px; z-index: 5; max-height: none; padding: 0.6rem; backdrop-filter: var(--blur); background: var(--surface-nav); }
  .lp-toc-head { margin-bottom: 0.4rem; }
  .lp-toc-list { flex-direction: row; overflow-x: auto; scrollbar-width: none; }
  .lp-toc-list a { white-space: nowrap; font-size: 0.82rem; }
}
</style>
