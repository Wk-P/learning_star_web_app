<template>
  <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
</template>
<script setup lang="ts">
</script>
<style>
/* view animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: none;
}
</style>
