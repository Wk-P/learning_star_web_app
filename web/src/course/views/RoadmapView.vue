<template>
  <div class="rm-wrap">
    <div v-if="loading" class="rm-state">
      <div class="skeleton" style="height:100%;border-radius:0" />
    </div>

    <div v-else-if="error" class="rm-state rm-error">
      <span style="font-size:40px">📭</span>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="load">重新加载</button>
    </div>

    <iframe
      v-else
      class="rm-frame"
      sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox"
      :srcdoc="processed"
      title="学习路线图"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { roadmapApi } from '@/course/api/course'

// ── 专业术语关键词，长词在前防止被短词提前截断 ──────────────────────────────
const KEYWORDS = [
  // 中文专业词
  '机器学习',
  '深度学习',
  '人工智能',
  '数据结构',
  '操作系统',
  '计算思维',
  '布尔逻辑',
  '三角函数',
  '解析几何',
  '立体几何',
  '概率统计',
  '数学建模',
  '程序设计',
  '数字素养',
  '国际音标',
  '二进制',
  '导数',
  '函数',
  '音标',
  // 英文专业词/缩写
  'IEEE',
  'ACM',
  'CPU',
  'ALU',
  'AI',
].sort((a, b) => b.length - a.length)

const EN_KW = new Set(['IEEE', 'ACM', 'CPU', 'ALU', 'AI'])

const KW_RE = new RegExp(
  KEYWORDS.map(k => {
    const escaped = k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    return EN_KW.has(k) ? `\\b${escaped}\\b` : escaped
  }).join('|'),
  'g',
)

function injectBaiduLinks(html: string): string {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')

  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const p = (node as Text).parentElement
      if (!p || p.closest('a') || p.tagName === 'SCRIPT' || p.tagName === 'STYLE') {
        return NodeFilter.FILTER_SKIP
      }
      return NodeFilter.FILTER_ACCEPT
    },
  })

  const textNodes: Text[] = []
  let n: Node | null
  while ((n = walker.nextNode())) textNodes.push(n as Text)

  for (const textNode of textNodes) {
    const original = textNode.textContent ?? ''
    KW_RE.lastIndex = 0
    if (!KW_RE.test(original)) continue
    KW_RE.lastIndex = 0

    const replaced = original.replace(KW_RE, (kw) => {
      const url = `https://www.baidu.com/s?wd=${encodeURIComponent(kw)}`
      return `<a href="${url}" target="_blank" rel="noopener" style="color:#2563eb;text-decoration:underline;text-decoration-color:#2563eb;font-weight:600;cursor:pointer">${kw}</a>`
    })

    const span = doc.createElement('span')
    span.innerHTML = replaced
    textNode.parentNode?.replaceChild(span, textNode)
  }

  return '<!doctype html>' + doc.documentElement.outerHTML
}

const processed = ref('')
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await roadmapApi.get()
    processed.value = injectBaiduLinks(data.content)
  } catch {
    error.value = '路线图暂未生成，请联系管理员上传。'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.rm-wrap {
  width: 100%;
  height: calc(100vh - 58px);
  display: flex;
  flex-direction: column;
}

.rm-frame {
  flex: 1;
  width: 100%;
  border: none;
  display: block;
}

.rm-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--c-text-2);
  font-size: 15px;
}

.rm-error { color: var(--c-text-3); }
</style>
