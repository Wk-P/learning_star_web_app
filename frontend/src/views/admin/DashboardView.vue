<template>
  <div>
    <h2 style="margin-bottom: 24px">概览</h2>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="视频总数" :value="videoCount" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="音频总数" :value="audioCount" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const videoCount = ref(0)
const audioCount = ref(0)

onMounted(async () => {
  const [videos, audios] = await Promise.all([api.getVideoList(), api.getAudioList()])
  videoCount.value = videos.reduce((sum, folder) => sum + folder.videos.length, 0)
  audioCount.value = audios.reduce((sum, folder) => sum + folder.audios.length, 0)
})
</script>
