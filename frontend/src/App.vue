<template>
  <RouterView v-slot="{ Component }">
    <Transition name="fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'
// initializing the store applies the saved theme to <html> immediately
useThemeStore()
</script>

<style>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s var(--ease), transform 0.3s var(--ease);
}
.fade-enter-from  { opacity: 0; transform: translateY(-16px); }
.fade-leave-to    { opacity: 0; transform: translateY(14px); }
.fade-enter-to, .fade-leave-from { opacity: 1; transform: none; }
</style>
