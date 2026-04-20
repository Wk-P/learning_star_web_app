<template>
  <nav class="wrapper">
    <RouterLink :to="{ name: 'user-dashboard'}" class="link">学习内容</RouterLink>
    <RouterLink :to="{ name: 'admin-dashboard'}" class="link">管理界面</RouterLink>
  </nav>
  <main>
    <div class="content">
      <div class="header">
        <h1>韩国语学习资料网站</h1>
        <h2>学习资源</h2>
      </div>
      <ul class="group">
        <li class="card" v-for="card in cards" :key="card.url.name">
          <RouterLink :to="card.url" class="link">{{ card.name }}</RouterLink>
        </li>
      </ul>
    </div>
  </main>
</template>
<script setup lang="ts">
import { ref } from 'vue';
const cards = ref([
  { url: { name: 'user-video'}, name: '视频' },
  { url: { name: 'user-audio'}, name: '音频' }
])
</script>
<style scoped>
.wrapper {
  display: flex;
  justify-content: space-evenly;
  width: 100%;
}

.link {
  display: block;
  width: 100%;
  padding: 1rem;
  text-align: center;
}


.content {
  text-align: center;
  margin: 4rem 10rem;
}

.group {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem;
  margin-top: 2rem;
}

.card {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 2rem;
  font-size: 1.2rem;
  transition: all 0.4s ease;
  padding: 2rem;
}

.card:hover {
  background-color: #ccc;
  cursor: pointer;
}

.header {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
