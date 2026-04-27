<template>
  <video ref="video" controls class="video-player"></video>
</template>

<script setup lang="ts">
import { onUnmounted, watch, useTemplateRef } from 'vue'
import Hls from 'hls.js'

const { src } = defineProps<{ src: string }>()

const videoRef = useTemplateRef<HTMLVideoElement>('video')

let hls: Hls | null = null

function loadSrc(src: string): void {
  const el = videoRef.value
  if (!el) return

  if (Hls.isSupported()) {
    hls?.destroy()
    hls = new Hls()
    hls.loadSource(src)
    hls.attachMedia(el)
  } else if (el.canPlayType('application/vnd.apple.mpegurl')) {
    // Safari 原生支持 HLS
    el.src = src
  }
}

// Vue 3.5 props 解构后仍然是响应式的，watch 可以直接追踪
watch(() => src, loadSrc, { immediate: true })

onUnmounted(() => hls?.destroy())
</script>

<style scoped>
.video-player {
  width: 100%;
}
</style>
