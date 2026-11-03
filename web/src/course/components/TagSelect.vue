<template>
  <div ref="root" class="ts" :class="[`ts-${size}`, { open, on: !!modelValue }]">
    <button
      ref="trigger"
      type="button"
      class="ts-trigger"
      aria-haspopup="listbox"
      :aria-expanded="open"
      aria-label="按标签筛选"
      @click="toggle"
      @keydown.down.prevent="openAt(selectedIndex)"
      @keydown.up.prevent="openAt(selectedIndex)"
    >
      <svg class="ts-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z" /><circle cx="7.5" cy="7.5" r="1.5" fill="currentColor" stroke="none" /></svg>
      <span class="ts-value">{{ modelValue ? `#${modelValue}` : '全部标签' }}</span>
      <span
        v-if="modelValue"
        class="ts-clear"
        role="button"
        tabindex="-1"
        aria-label="清除标签筛选"
        @click.stop="select('')"
      >✕</span>
      <svg v-else class="ts-chev" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M6 9l6 6 6-6" /></svg>
    </button>

    <Transition name="ts-pop">
      <ul
        v-if="open"
        ref="list"
        class="ts-list"
        role="listbox"
        tabindex="-1"
        :aria-activedescendant="`${uid}-${active}`"
        @keydown.down.prevent="move(1)"
        @keydown.up.prevent="move(-1)"
        @keydown.home.prevent="active = 0"
        @keydown.end.prevent="active = items.length - 1"
        @keydown.enter.prevent="select(items[active]!.value)"
        @keydown.space.prevent="select(items[active]!.value)"
        @keydown.esc.prevent="close(true)"
        @keydown.tab="close(false)"
      >
        <li
          v-for="(o, i) in items"
          :id="`${uid}-${i}`"
          :key="o.value"
          role="option"
          :aria-selected="o.value === modelValue"
          :class="['ts-opt', { active: i === active, selected: o.value === modelValue }]"
          @mouseenter="active = i"
          @click="select(o.value)"
        >
          <span class="ts-opt-label">{{ o.value ? `#${o.value}` : '全部标签' }}</span>
          <span class="ts-opt-count">{{ o.count }}</span>
          <svg v-if="o.value === modelValue" class="ts-check" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
        </li>
      </ul>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue'

export interface TagOption { value: string; count: number }

const props = withDefaults(defineProps<{
  modelValue: string
  options: TagOption[]
  /** 「全部标签」一项显示的数量 */
  total: number
  size?: 'md' | 'sm'
}>(), { size: 'md' })
const emit = defineEmits<{ 'update:modelValue': [string] }>()

const uid = `ts-${Math.random().toString(36).slice(2, 8)}`
const root = ref<HTMLElement>()
const trigger = ref<HTMLButtonElement>()
const list = ref<HTMLElement>()
const open = ref(false)
const active = ref(0)

const items = computed<TagOption[]>(() => [{ value: '', count: props.total }, ...props.options])
const selectedIndex = computed(() => Math.max(0, items.value.findIndex(o => o.value === props.modelValue)))

function onDocPointer(e: PointerEvent) {
  if (!root.value?.contains(e.target as Node)) close(false)
}

async function openAt(i: number) {
  active.value = i
  open.value = true
  document.addEventListener('pointerdown', onDocPointer)
  await nextTick()
  list.value?.focus()
  list.value?.querySelector('.active')?.scrollIntoView({ block: 'nearest' })
}

function close(refocus: boolean) {
  open.value = false
  document.removeEventListener('pointerdown', onDocPointer)
  if (refocus) trigger.value?.focus()
}

function toggle() {
  open.value ? close(true) : openAt(selectedIndex.value)
}

function move(d: number) {
  const n = items.value.length
  active.value = (active.value + d + n) % n
  nextTick(() => list.value?.querySelector('.active')?.scrollIntoView({ block: 'nearest' }))
}

function select(v: string) {
  emit('update:modelValue', v)
  close(true)
}

onBeforeUnmount(() => document.removeEventListener('pointerdown', onDocPointer))
</script>

<style scoped>
.ts { position: relative; flex: 0 0 auto; }

.ts-trigger {
  display: inline-flex; align-items: center; gap: 7px;
  height: 38px; max-width: 200px; padding: 0 12px;
  border: none; border-radius: var(--r);
  font-size: 13px; font-weight: 500; color: var(--c-text-2, var(--c-text));
  background: var(--c-bg, var(--c-surface));
  box-shadow: inset 0 0 0 1px var(--c-border);
  cursor: pointer;
  transition: box-shadow var(--t), color var(--t), background var(--t);
}
.ts-sm .ts-trigger { height: 36px; background: var(--c-surface); }
.ts-trigger:hover { box-shadow: inset 0 0 0 1px var(--c-border-hover, var(--c-border)); color: var(--c-text); }
.ts-trigger:focus-visible,
.ts.open .ts-trigger { outline: none; box-shadow: inset 0 0 0 1.5px var(--accent), 0 0 0 4px color-mix(in srgb, var(--accent) 16%, transparent); }
.ts.on .ts-trigger {
  color: var(--c-text);
  background: color-mix(in srgb, var(--accent) 12%, var(--c-bg, var(--c-surface)));
  box-shadow: inset 0 0 0 1.5px color-mix(in srgb, var(--accent) 55%, transparent);
}

.ts-icon { flex-shrink: 0; color: var(--c-text-3); }
.ts.on .ts-icon { color: var(--accent); }
.ts-value { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ts-chev { flex-shrink: 0; color: var(--c-text-3); transition: transform var(--t); }
.ts.open .ts-chev { transform: rotate(180deg); }
.ts-clear {
  flex-shrink: 0; display: grid; place-items: center;
  width: 18px; height: 18px; margin-right: -4px; border-radius: 50%;
  font-size: 10px; color: var(--c-text-3);
  transition: background var(--t), color var(--t);
}
.ts-clear:hover { background: color-mix(in srgb, var(--c-text-3) 22%, transparent); color: var(--c-text); }

.ts-list {
  position: absolute; top: calc(100% + 6px); left: 0; z-index: 30;
  min-width: 100%; width: max-content; max-width: 260px; max-height: 280px;
  margin: 0; padding: 5px; list-style: none; overflow-y: auto;
  background: var(--c-surface);
  border: 1px solid var(--c-border); border-radius: var(--r-lg);
  box-shadow: var(--shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.18));
  outline: none;
}
.ts-opt {
  display: flex; align-items: center; gap: 10px;
  padding: 7px 10px; border-radius: var(--r-sm, 6px);
  font-size: 13px; color: var(--c-text-2, var(--c-text)); cursor: pointer;
}
.ts-opt.active { background: color-mix(in srgb, var(--accent) 10%, transparent); color: var(--c-text); }
.ts-opt.selected { color: var(--c-text); font-weight: 600; }
.ts-opt-label { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ts-opt-count {
  flex-shrink: 0; min-width: 20px; padding: 0 6px; border-radius: 99px;
  font-size: 11px; font-weight: 500; text-align: center; font-variant-numeric: tabular-nums;
  color: var(--c-text-3); background: color-mix(in srgb, var(--c-text-3) 14%, transparent);
}
.ts-opt.selected .ts-opt-count { color: var(--accent); background: color-mix(in srgb, var(--accent) 14%, transparent); }
.ts-check { flex-shrink: 0; color: var(--accent); margin-left: -4px; }

.ts-pop-enter-active, .ts-pop-leave-active { transition: opacity 0.14s ease, transform 0.14s ease; transform-origin: top left; }
.ts-pop-enter-from, .ts-pop-leave-to { opacity: 0; transform: translateY(-4px) scale(0.98); }

@media (prefers-reduced-motion: reduce) {
  .ts-pop-enter-active, .ts-pop-leave-active, .ts-chev { transition: none; }
}
</style>
