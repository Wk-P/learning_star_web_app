<template>
  <div class="user-layout">
    <nav>
      <RouterLink :to="{ name: 'home' }" class="link">导航页</RouterLink>
      <RouterLink :to="{ name: 'user-dashboard' }" class="link">首页</RouterLink>
      <RouterLink :to="{ name: 'user-video' }" class="link">视频</RouterLink>
      <RouterLink :to="{ name: 'user-audio' }" class="link">音频</RouterLink>
      <RouterLink :to="{ name: 'user-file' }" class="link">文件</RouterLink>
    </nav>

    <RouterView v-slot="{ Component }">
      <Transition name="opacity" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </div>
</template>
<script setup lang="ts">

</script>
<style scoped>
nav {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 1rem;
  margin-bottom: 1rem;
  overflow-x: auto;
  scrollbar-width: none;
}

nav::-webkit-scrollbar {
  display: none;
}

.link {
  padding: 0.5rem 1.2rem;
  border-radius: 0.5rem;
  color: var(--text);
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.link:hover {
  background: var(--glass-bg-hover);
  color: var(--text);
}

.link.router-link-active {
  background: var(--glass-bg-strong);
  color: var(--text);
  font-weight: 700;
  border: 1px solid var(--glass-border);
}

.opacity-enter-active, .opacity-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.opacity-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.opacity-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

.opacity-enter-to,
.opacity-leave-from {
  opacity: 1;
  transform: none;
}
</style>
