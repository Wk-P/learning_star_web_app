<template>
  <video ref="video" controls class="video-player"></video>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, useTemplateRef } from 'vue'
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

onMounted(() => loadSrc(src))
watch(() => src, loadSrc)

onUnmounted(() => hls?.destroy())
</script>

<style scoped>
.video-player {
  width: 100%;
}
</style>
