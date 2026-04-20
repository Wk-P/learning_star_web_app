<template>
  <div class="user-layout">
    <nav>
      <RouterLink :to="{ name: 'home' }" class="link">导航页</RouterLink>
      <RouterLink :to="{ name: 'user-dashboard' }" class="link">首页</RouterLink>
      <RouterLink :to="{ name: 'user-video' }" class="link">视频</RouterLink>
      <RouterLink :to="{ name: 'user-audio' }" class="link">音频</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>
<script setup lang="ts">

</script>
<style scoped>
.link {
  margin: 1rem;
  padding: 1rem;
}
</style>
