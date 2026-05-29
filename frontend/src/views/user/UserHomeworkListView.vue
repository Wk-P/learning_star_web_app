<template>
  <div style="display:flex;flex-direction:column;gap:20px">
    <h1 class="page-title">我的作业</h1>
    <div v-if="loading" class="skeleton" style="height:200px" />
    <template v-else>
      <div class="card">
        <div class="card-header">当周进行中</div>
        <div v-if="currentWeek.length === 0" class="empty"><span class="empty-icon">✅</span><p>当周作业为空...</p></div>
        <div v-else class="table-wrap">
          <table class="table">
            <thead><tr><th>课程</th><th>作业名称</th><th>截止时间</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="hw in currentWeek" :key="hw.id">
                <td>{{ hw.courseName }}</td>
                <td>{{ hw.name }}</td>
                <td>{{ fmt(hw.endTime) }}</td>
                <td><button class="btn btn-link btn-sm" @click="router.push(`/user/homework/${hw.id}`)">查看</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-header">历史作业</div>
        <div v-if="history.length === 0" class="empty"><span class="empty-icon">📂</span><p>历史作业为空...</p></div>
        <div v-else class="table-wrap">
          <table class="table">
            <thead><tr><th>课程</th><th>作业名称</th><th>截止时间</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="hw in history" :key="hw.id">
                <td>{{ hw.courseName }}</td>
                <td>{{ hw.name }}</td>
                <td>{{ fmt(hw.endTime) }}</td>
                <td><button class="btn btn-link btn-sm" @click="router.push(`/user/homework/${hw.id}`)">查看</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { homeworkApi } from '@/api/homework'
import type { Homework } from '@/types'
const router = useRouter(); const loading = ref(false); const homework = ref<Homework[]>([])
onMounted(async () => { loading.value = true; try { homework.value = (await homeworkApi.myList()).data } finally { loading.value = false } })
const currentWeek = computed(() => homework.value.filter(h => h.status === 'in_progress'))
const history = computed(() => homework.value.filter(h => h.status === 'ended'))
</script>
