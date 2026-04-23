<template>
  <div>
    <nav class="header-nav">
      <RouterLink :to="{ name: 'user-dashboard' }" class="link">学习内容</RouterLink>
      <RouterLink :to="{ name: 'admin-dashboard' }" class="link">管理界面</RouterLink>
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
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
const cards = ref([
  { url: { name: 'user-video' }, name: '视频' },
  { url: { name: 'user-audio' }, name: '音频' }
]);


</script>
<style scoped>
.header-nav {
  display: flex;
  justify-content: space-evenly;
  width: 100%;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: 2rem;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
  padding: 0.5rem;
  border: 1px solid var(--glass-border);
}

@media (max-width: 768px) {
  .header-nav {
    max-width: 100svw;
  }

  .header-nav .link {
    border: 1px solid var(--border);
    margin: .5rem;
  }
}

.link {
  display: block;
  width: 100%;
  padding: 1rem;
  text-align: center;
  border-radius: 2rem;
  color: var(--text);
}

.card .link {
  padding: 2rem;
}

.link:hover {
  background-color: var(--bg-hover);
}

.content {
  text-align: center;
  margin: 4rem 10rem;
}

@media (max-width: 768px) {
  .content {
    margin: .2rem;
  }
}

.group {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15%;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .group {
    grid-template-columns: 1fr;
  }
}

.card {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 2rem;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.card:hover {
  background: var(--glass-bg-hover);
  border-color: var(--primary);
  transform: translateY(-2px);
  cursor: pointer;
}

.header {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-shadow: var(--border) 1px 10px 5px;
}

@media (max-width: 768px) {
  .header * {
    width: 100%;
  }

  .header h1 {
    margin-bottom: 1rem;
  }
}
</style>
