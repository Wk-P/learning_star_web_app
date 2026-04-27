<template>
  <div class="user file">

    <Transition name="nav-fade">
      <nav v-if="currentPath.length > 0">
        <button @click="currentPath = []">全部</button>
        <TransitionGroup name="crumb" tag="span" class="crumb-group">
          <span class="crumb-item" v-for="(segment, i) in currentPath" :key="segment">
            <span class="sep">/</span>
            <button @click="currentPath = currentPath.slice(0, i + 1)">{{ segment }}</button>
          </span>
        </TransitionGroup>
      </nav>
    </Transition>

    <Transition name="content" mode="out-in">
      <ul v-if="subCategories.length > 0" :key="'cat-' + currentPath.join('/')">
        <li v-for="category in subCategories" :key="category">
          <button @click="currentPath = [...currentPath, category]">{{ category }}</button>
        </li>
      </ul>
    </Transition>

    <Transition name="content" mode="out-in">
      <ul v-if="currentFiles.length > 0" :key="'file-' + currentPath.join('/')">
        <li v-for="file in currentFiles" :key="file.url">
          <a :href="file.url">{{ file.title }}</a>
        </li>
      </ul>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface File {
  url: string
  title: string
  path: string[]
}

const files = ref<File[]>([
  { path: ['topik韩语', 'l1', 'l2'], title: 'topik直播1', url: 'https://www.google.com' },
  { path: ['小梁韩语', 'l1', 'l2', 'l3'], title: 'topik回放', url: 'https://www.google.com' },
  { path: ['一墨私塾', '三级班'], title: 'topik直播', url: 'https://www.google.com' },
  { path: ['一墨私塾', '四级班'], title: 'topik直播2', url: 'https://www.google.com' },
])

// 核心状态：当前钻入的路径，比如 [] / ['一墨私塾'] / ['一墨私塾', '三级班']
const currentPath = ref<string[]>([])

// 计算当前路径下的下一级分类（去重）
// 思路：找出所有"前缀匹配 currentPath"的文件，取它们的下一级 path 节点
const subCategories = computed(() => {
  const depth = currentPath.value.length

  const matched = files.value.filter((file) =>
    // 文件的 path 必须比当前深度还要深（还有下一级）
    file.path.length > depth + 1 &&
    // 文件的前几段必须和 currentPath 完全一致
    currentPath.value.every((segment, i) => file.path[i] === segment)
  )

  // 取下一级的节点，用 Set 去重
  return [...new Set(matched.map((file) => file.path[depth] as string))]
})

// 计算当前路径下直接可看的文件
// 思路：文件的 path 去掉最后一段（文件名）剩下的部分 === currentPath
const currentFiles = computed(() => {
  return files.value.filter((file) => {
    const parentPath = file.path.slice(0, -1)  // path 去掉最后一级
    return (
      parentPath.length === currentPath.value.length &&
      currentPath.value.every((segment, i) => parentPath[i] === segment)
    )
  })
})
</script>

<style scoped>
ul {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

li {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

li:hover {
  background: var(--glass-bg-hover);
  transform: translateY(-1px);
}

nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
  color: var(--text-muted);
  font-size: 14px;
}

.crumb-group {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.crumb-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.sep {
  color: var(--text-muted);
}

nav button,
ul button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text);
  font-size: 14px;
  padding: 0.5rem 0.75rem;
}

nav button:hover,
ul button:hover {
  color: var(--primary);
  text-decoration: underline;
}

a {
  display: block;
  padding: 0.5rem 0.75rem;
  color: var(--text);
  text-decoration: none;
}

a:hover {
  color: var(--primary-deep);
}

.nav-fade-enter-active,
.nav-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.nav-fade-enter-from,
.nav-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.crumb-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.crumb-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.crumb-enter-from {
  opacity: 0;
  transform: translateX(12px);
}
.crumb-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.content-enter-active,
.content-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.content-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.content-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
