<template>
  <div class="mm-page">

    <!-- 标签切换 -->
    <div class="mm-tabs">
      <button
        v-for="m in maps"
        :key="m.key"
        :class="['mm-tab', { active: active === m.key }]"
        :style="active === m.key ? { borderBottomColor: m.color, color: m.color } : {}"
        @click="active = m.key"
      >
        <span class="mm-tab-icon">{{ m.icon }}</span>
        {{ m.label }}
      </button>
    </div>

    <!-- 图片展示区 -->
    <div class="mm-viewer">
      <template v-for="m in maps" :key="m.key">
        <transition name="fade">
          <div v-if="active === m.key" class="mm-img-wrap" @click="openLight(m)">
            <img :src="m.src" :alt="m.label" class="mm-img" draggable="false" />
            <div class="mm-zoom-hint">点击查看大图</div>
          </div>
        </transition>
      </template>
    </div>

    <!-- 灯箱 -->
    <Teleport to="body">
      <Transition name="light">
        <div v-if="lightItem" class="light-backdrop" @click.self="lightItem = null">
          <div class="light-box">
            <button class="light-close" @click="lightItem = null">✕</button>
            <button class="light-prev" @click="stepLight(-1)">‹</button>
            <img
              :src="lightItem.src"
              :alt="lightItem.label"
              class="light-img"
              :style="{ transform: `scale(${zoom})`, cursor: zoom > 1 ? 'zoom-out' : 'zoom-in' }"
              @click="zoom = zoom > 1 ? 1 : 1.8"
            />
            <button class="light-next" @click="stepLight(1)">›</button>
            <div class="light-label">{{ lightItem.label }}</div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const maps = [
  { key: 'cs',      label: '计算机学习体系', icon: '💻', color: '#2563eb', src: '/mindmaps/cs.png' },
  { key: 'math',    label: '高中数学体系',   icon: '📐', color: '#059669', src: '/mindmaps/math.png' },
  { key: 'english', label: '英语学习体系',   icon: '🔤', color: '#d97706', src: '/mindmaps/english.png' },
]

const active = ref('cs')
const lightItem = ref<typeof maps[0] | null>(null)
const zoom = ref(1)

function openLight(m: typeof maps[0]) {
  lightItem.value = m
  zoom.value = 1
}

function stepLight(dir: 1 | -1) {
  const idx = maps.findIndex(m => m.key === lightItem.value?.key)
  const next = (idx + dir + maps.length) % maps.length
  lightItem.value = maps[next]!
  zoom.value = 1
}
</script>

<style scoped>
.mm-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 58px);
  background: var(--c-bg);
}

/* ── 标签栏 ─────────────────────────────────────────────── */
.mm-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--c-border);
  background: var(--c-surface);
  padding: 0 24px;
  flex-shrink: 0;
}

.mm-tab {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 14px 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--c-text-3);
  border-bottom: 3px solid transparent;
  margin-bottom: -1px;
  cursor: pointer;
  background: transparent;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.mm-tab:hover { color: var(--c-text-2); }
.mm-tab.active { font-weight: 700; }
.mm-tab-icon { font-size: 16px; }

/* ── 图片区 ─────────────────────────────────────────────── */
.mm-viewer {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px;
  position: relative;
}

.mm-img-wrap {
  position: relative;
  cursor: zoom-in;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,.12);
  transition: transform 0.2s, box-shadow 0.2s;
  max-width: 1000px;
  width: 100%;
}
.mm-img-wrap:hover {
  transform: translateY(-3px);
  box-shadow: 0 28px 70px rgba(0,0,0,.18);
}
.mm-img-wrap:hover .mm-zoom-hint { opacity: 1; }

.mm-img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 16px;
  user-select: none;
}

.mm-zoom-hint {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(0,0,0,.55);
  color: #fff;
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 99px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

/* ── 灯箱 ───────────────────────────────────────────────── */
.light-backdrop {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0,0,0,.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.light-box {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: min(1200px, 95vw);
  max-height: 95vh;
}

.light-img {
  max-width: 100%;
  max-height: calc(95vh - 80px);
  object-fit: contain;
  border-radius: 12px;
  transition: transform 0.25s ease;
  user-select: none;
}

.light-label {
  color: rgba(255,255,255,.7);
  font-size: 13px;
}

.light-close {
  position: absolute;
  top: -40px;
  right: 0;
  width: 32px; height: 32px;
  border-radius: 50%;
  background: rgba(255,255,255,.15);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.light-close:hover { background: rgba(255,255,255,.3); }

.light-prev, .light-next {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  width: 44px; height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,.15);
  color: #fff;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.light-prev { left: 16px; }
.light-next { right: 16px; }
.light-prev:hover, .light-next:hover { background: rgba(255,255,255,.3); }

/* ── 动画 ───────────────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; position: absolute; inset: 0; display: flex; align-items: flex-start; justify-content: center; padding: 24px; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.light-enter-active { transition: opacity 0.2s; }
.light-leave-active { transition: opacity 0.15s; }
.light-enter-from, .light-leave-to { opacity: 0; }

/* ── 响应式 ─────────────────────────────────────────────── */
@media (max-width: 600px) {
  .mm-tabs { padding: 0 12px; }
  .mm-tab { padding: 12px 12px; font-size: 13px; }
  .mm-viewer { padding: 12px; }
  .light-prev { left: 8px; }
  .light-next { right: 8px; }
}
</style>
