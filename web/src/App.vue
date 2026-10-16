<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>

  <!-- course 栏目的弹窗 / 提示挂在这里，以继承 .mod-course 样式作用域 -->
  <div id="course-layer" class="mod-course course-layer">
    <AppToast />
    <AppConfirm />
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/core/stores/theme'
import AppToast from '@/course/components/AppToast.vue'
import AppConfirm from '@/course/components/AppConfirm.vue'

// 初始化即把保存的主题应用到 <html>
useThemeStore()
</script>

<style>
.course-layer { position: fixed; inset: 0 auto auto 0; width: 0; height: 0; z-index: 1000; }
</style>
