<template>
  <div class="tree-node">
    <div
      class="node-row"
      :style="{ paddingLeft: depth * 1.4 + 0.5 + 'rem' }"
      :class="{ 'node-inherited': inherited }"
      @click="!inherited && emit('toggle', node.path)"
    >
      <!-- expand toggle -->
      <button
        v-if="node.children.length"
        class="expand-btn"
        @click.stop="expanded = !expanded"
      >
        {{ expanded ? '▾' : '▸' }}
      </button>
      <span v-else class="expand-spacer" />

      <!-- custom checkbox -->
      <div
        class="custom-check"
        :class="{
          'is-checked':       checked,
          'is-indeterminate': indeterminate,
          'is-inherited':     inherited,
        }"
      >
        <svg v-if="checked" viewBox="0 0 10 8" fill="none">
          <path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span v-else-if="indeterminate" class="dash" />
      </div>

      <span class="node-text" :class="{ 'text-active': checked || inherited }">
        {{ node.label }}
      </span>
      <span v-if="inherited" class="inherited-tag">继承</span>
    </div>

    <!-- children -->
    <Transition name="expand">
      <div v-if="expanded && node.children.length">
        <PermTreeNode
          v-for="child in node.children"
          :key="child.path"
          :node="child"
          :perms="perms"
          :depth="depth + 1"
          @toggle="emit('toggle', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TreeNode } from '@/api'

const props = defineProps<{
  node: TreeNode
  perms: string[]
  depth: number
}>()

const emit = defineEmits<{ toggle: [path: string] }>()

const expanded = ref(props.depth < 1)

const checked = computed(() => props.perms.includes(props.node.path))

const inherited = computed(() => {
  if (checked.value) return false
  return props.perms.some(p => props.node.path.startsWith(p + '/'))
})

function hasSelectedDescendant(node: TreeNode): boolean {
  return node.children.some(c =>
    props.perms.includes(c.path) ||
    props.perms.some(p => c.path.startsWith(p + '/')) ||
    hasSelectedDescendant(c)
  )
}

const indeterminate = computed(() =>
  !checked.value && !inherited.value && hasSelectedDescendant(props.node)
)
</script>

<style scoped>
.tree-node { display: flex; flex-direction: column; }

.node-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding-top: 0.28rem;
  padding-bottom: 0.28rem;
  padding-right: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  user-select: none;
}
.node-row:hover { background: rgba(255,255,255,0.04); }
.node-row.node-inherited { cursor: default; }

/* ── expand btn ── */
.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #8892a4;
  font-size: 0.7rem;
  width: 16px;
  flex-shrink: 0;
  padding: 0;
  transition: color 0.15s;
  z-index: 1;
}
.expand-btn:hover { color: #e2e8f0; }
.expand-spacer { width: 16px; flex-shrink: 0; }

/* ── custom checkbox ── */
.custom-check {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
  border-radius: 4px;
  border: 1.5px solid rgba(255,255,255,0.18);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, background 0.15s;
}

.custom-check svg {
  width: 10px;
  height: 8px;
  color: #07090e;
}

.custom-check.is-checked {
  background: #2dd4bf;
  border-color: #2dd4bf;
}

.custom-check.is-indeterminate {
  border-color: #2dd4bf;
  background: rgba(45,212,191,0.15);
}

.custom-check.is-inherited {
  border-color: rgba(45,212,191,0.35);
  background: rgba(45,212,191,0.08);
}

.dash {
  width: 7px;
  height: 1.5px;
  background: #2dd4bf;
  border-radius: 1px;
}

.node-row:hover .custom-check:not(.is-checked):not(.is-inherited) {
  border-color: rgba(255,255,255,0.35);
}

/* ── label ── */
.node-text {
  font-size: 0.875rem;
  color: #8892a4;
  transition: color 0.15s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.node-text.text-active { color: #e2e8f0; }

.inherited-tag {
  font-size: 0.65rem;
  padding: 0.05rem 0.35rem;
  border-radius: 4px;
  background: rgba(45,212,191,0.12);
  color: #2dd4bf;
  flex-shrink: 0;
}

/* ── expand transition ── */
.expand-enter-active, .expand-leave-active {
  transition: opacity 0.18s, transform 0.18s;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
