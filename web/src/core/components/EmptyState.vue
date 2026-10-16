<template>
  <div class="empty" role="status">
    <span class="empty-icon"><AppIcon :name="icon" :size="26" :stroke="1.6" /></span>
    <p class="empty-title">{{ title }}</p>
    <p v-if="desc" class="empty-desc">{{ desc }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
import AppIcon from '@/core/components/AppIcon.vue'

defineProps<{ icon: InstanceType<typeof AppIcon>['$props']['name']; title: string; desc?: string }>()
</script>

<style scoped>
.empty {
  display: flex; flex-direction: column; align-items: center; gap: 0.35rem;
  margin-top: 1rem; padding: 3rem 1.5rem; text-align: center;
  border: 1px dashed var(--border-strong); border-radius: var(--r-lg);
  animation: empty-in 0.5s var(--ease-out) both;
}
.empty-icon {
  width: 56px; height: 56px; border-radius: 16px; margin-bottom: 0.5rem;
  display: grid; place-items: center;
  color: var(--primary); background: var(--primary-dim);
}
.empty-title { font-size: 1rem; font-weight: 600; color: var(--text); }
.empty-desc { font-size: 0.85rem; color: var(--text-muted); max-width: 26em; line-height: 1.6; }
@keyframes empty-in { from { opacity: 0; transform: translateY(8px); } }
</style>
