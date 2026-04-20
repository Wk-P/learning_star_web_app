<template>
  <div class="user-video">

    <!-- 面包屑：currentPath 有内容才显示 -->
    <nav v-if="currentPath.length > 0">
      <!-- 点击「根目录」回到最顶层 -->
      <button @click="currentPath = []">全部</button>
      <template v-for="(segment, i) in currentPath" :key="i">
        <span> / </span>
        <!-- 点击某一级，截断到那一级（退回去） -->
        <button @click="currentPath = currentPath.slice(0, i + 1)">{{ segment }}</button>
      </template>
    </nav>

    <!-- 当前层级的子分类（还没到叶子节点时显示） -->
    <ul v-if="subCategories.length > 0">
      <li v-for="category in subCategories" :key="category">
        <!-- 点击分类，往 currentPath 里加一级 -->
        <button @click="currentPath = [...currentPath, category]">{{ category }}</button>
      </li>
    </ul>

    <!-- 当前路径下的视频（已经钻到叶子节点时显示） -->
    <ul v-if="currentVideos.length > 0">
      <li v-for="video in currentVideos" :key="video.url">
        <a :href="video.url">{{ video.title }}</a>
      </li>
    </ul>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Video {
  url: string
  title: string
  path: string[]
}

const videos = ref<Video[]>([
  { path: ['topik韩语', 'l1', 'l2'], title: 'topik直播1', url: 'https://www.google.com' },
  { path: ['小梁韩语', 'l1', 'l2', 'l3'], title: 'topik回放', url: 'https://www.google.com' },
  { path: ['一墨私塾', '三级班'], title: 'topik直播', url: 'https://www.google.com' },
  { path: ['一墨私塾', '四级班'], title: 'topik直播2', url: 'https://www.google.com' },
])

// 核心状态：当前钻入的路径，比如 [] / ['一墨私塾'] / ['一墨私塾', '三级班']
const currentPath = ref<string[]>([])

// 计算当前路径下的下一级分类（去重）
// 思路：找出所有"前缀匹配 currentPath"的视频，取它们的下一级 path 节点
const subCategories = computed(() => {
  const depth = currentPath.value.length

  const matched = videos.value.filter((video) =>
    // 视频的 path 必须比当前深度还要深（还有下一级）
    video.path.length > depth + 1 &&
    // 视频的前几段必须和 currentPath 完全一致
    currentPath.value.every((segment, i) => video.path[i] === segment)
  )

  // 取下一级的节点，用 Set 去重
  return [...new Set(matched.map((video) => video.path[depth] as string))]
})

// 计算当前路径下直接可看的视频
// 思路：视频的 path 去掉最后一段（文件名）剩下的部分 === currentPath
const currentVideos = computed(() => {
  return videos.value.filter((video) => {
    const parentPath = video.path.slice(0, -1)  // path 去掉最后一级
    return (
      parentPath.length === currentPath.value.length &&
      currentPath.value.every((segment, i) => parentPath[i] === segment)
    )
  })
})
</script>

<style scoped>
nav button,
ul button {
  background: none;
  border: none;
  cursor: pointer;
  color: #2ec4b6;
  font-size: 14px;
}
nav button:hover,
ul button:hover {
  text-decoration: underline;
}
</style>
