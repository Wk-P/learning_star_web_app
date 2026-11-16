<template>
  <div class="hub">
    <header class="hub-head">
      <h1 class="hub-title">语言学习</h1>
      <p class="hub-sub">选择一门语言，查看它的视频课程、听力音频与学习资料</p>
    </header>

    <div v-if="loading" class="sk-grid" aria-label="加载中">
      <div v-for="i in 3" :key="i" class="sk sk-card" />
    </div>
    <EmptyState v-else-if="error" icon="shield" title="加载失败" :desc="error" />
    <EmptyState v-else-if="!visible.length" icon="globe" title="还没有可学习的语言" desc="管理员添加语言后会出现在这里。" />

    <section v-for="cat in visible" v-else :key="cat.id" class="cat">
      <div class="cat-head">
        <h2 class="cat-name">{{ cat.name }}</h2>
        <span v-if="cat.description" class="cat-desc">{{ cat.description }}</span>
      </div>
      <div class="lang-grid">
        <RouterLink
          v-for="(lang, i) in cat.languages" :key="lang.id" v-reveal="i"
          :to="{ name: 'language-home', params: { lang: lang.slug } }"
          class="lang-card lift" :class="{ inactive: !lang.is_active }" :style="{ '--c': lang.color || 'var(--primary)' }"
        >
          <span class="lang-icon"><AppIcon name="globe" :size="22" /></span>
          <span class="lang-text">
            <span class="lang-name">
              {{ lang.name }}<span v-if="lang.native_name" class="lang-native">{{ lang.native_name }}</span>
            </span>
            <span v-if="lang.description" class="lang-desc">{{ lang.description }}</span>
            <span v-if="!lang.is_active" class="lang-badge">未启用 · 仅管理员可见</span>
          </span>
          <AppIcon name="arrow" :size="16" class="lang-arrow" />
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppIcon from '@/core/components/AppIcon.vue'
import EmptyState from '@/core/components/EmptyState.vue'
import { useLanguageStore } from '@/language/stores/languages'

const store = useLanguageStore()
const loading = ref(!store.loaded)
const error = ref('')

// 没有语言的分类不显示
const visible = computed(() => store.categories.filter((c) => c.languages.length))

onMounted(async () => {
  try {
    await store.reload()
  } catch {
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hub { display: flex; flex-direction: column; gap: 2rem; padding: 1.5rem 0; }

.hub-title { font-size: 1.75rem; font-weight: 800; color: var(--text); }
.hub-sub { margin-top: 0.3rem; font-size: 0.9rem; color: var(--text-subtle); }

.cat { display: flex; flex-direction: column; gap: 0.75rem; }
.cat-head { display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap; }
.cat-name { font-size: 1.05rem; font-weight: 700; color: var(--text); }
.cat-desc { font-size: 0.82rem; color: var(--text-subtle); }

.lang-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.lang-card {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 1rem 1.1rem;
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  color: var(--text);
  text-decoration: none;
  min-width: 0;
}
.lang-card:hover { border-color: color-mix(in srgb, var(--c) 45%, var(--border)); }
.lang-card.inactive { opacity: 0.6; }

.lang-icon {
  flex: none;
  display: grid;
  place-items: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: var(--r-md);
  color: var(--c);
  background: color-mix(in srgb, var(--c) 14%, transparent);
}

.lang-text { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; flex: 1; }
.lang-name { font-weight: 700; font-size: 1rem; }
.lang-native { margin-left: 0.5rem; font-weight: 400; font-size: 0.85rem; color: var(--text-muted); }
.lang-desc { font-size: 0.8rem; color: var(--text-subtle); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lang-badge { font-size: 0.72rem; color: var(--text-muted); }
.lang-arrow { flex: none; color: var(--text-subtle); }

.sk-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.75rem; }
.sk-card { height: 4.6rem; border-radius: var(--r-lg); }
</style>
