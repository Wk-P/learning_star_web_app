<template>
  <div class="lv-picker" role="group" aria-label="课程阶段">
    <button
      v-for="l in LEVELS"
      :key="l.key"
      type="button"
      :class="['lv-opt', { on: modelValue.includes(l.key) }]"
      :style="{ '--lv': l.color }"
      :aria-pressed="modelValue.includes(l.key)"
      @click="toggle(l.key)"
    >
      <span class="lv-step">{{ l.step }}</span>
      <span class="lv-text">
        <strong>{{ l.key }}</strong>
        <small>{{ l.hint }}</small>
      </span>
      <svg class="lv-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { LEVELS } from '@/course/levels'
import type { VideoLevel } from '@/course/types'

const props = defineProps<{ modelValue: VideoLevel[] }>()
const emit = defineEmits<{ 'update:modelValue': [VideoLevel[]] }>()

function toggle(k: VideoLevel) {
  const set = new Set(props.modelValue)
  set.has(k) ? set.delete(k) : set.add(k)
  emit('update:modelValue', LEVELS.map(l => l.key).filter(x => set.has(x)))
}
</script>

<style scoped>
.lv-picker { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.lv-opt {
  position: relative;
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: var(--r);
  text-align: left; color: var(--c-text-2);
  background: var(--c-surface);
  box-shadow: inset 0 0 0 1px var(--c-border);
  transition: box-shadow var(--t), background var(--t), color var(--t);
}
.lv-opt:hover { box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--lv) 50%, var(--c-border)); }
.lv-opt.on {
  color: var(--c-text);
  background: color-mix(in srgb, var(--lv) 10%, var(--c-surface));
  box-shadow: inset 0 0 0 1.5px var(--lv);
}
.lv-step {
  width: 26px; height: 26px; border-radius: 8px; flex-shrink: 0;
  display: grid; place-items: center; font-size: 12px; font-weight: 700;
  color: var(--lv); background: color-mix(in srgb, var(--lv) 14%, transparent);
}
.lv-opt.on .lv-step { color: #fff; background: var(--lv); }
.lv-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.3; }
.lv-text strong { font-size: 13px; }
.lv-text small { font-size: 11px; color: var(--c-text-3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lv-check { position: absolute; top: 6px; right: 6px; color: var(--lv); opacity: 0; transform: scale(0.6); transition: opacity var(--t), transform var(--t); }
.lv-opt.on .lv-check { opacity: 1; transform: none; }
@media (max-width: 560px) { .lv-picker { grid-template-columns: 1fr; } }
</style>
