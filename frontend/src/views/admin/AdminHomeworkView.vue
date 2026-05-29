<template>
  <div>
    <h1 class="page-title">作业详情编辑</h1>
    <div v-if="loading" class="skeleton" style="height:300px" />
    <div v-else-if="hw" class="card" style="max-width:560px">
      <div class="card-body" style="display:flex;flex-direction:column;gap:14px">
        <div class="field"><label class="field-label">作业名称</label><input v-model="form.name" class="input" /></div>
        <div class="field"><label class="field-label">作业描述</label><textarea v-model="form.description" class="textarea" /></div>
        <div class="field"><label class="field-label">开始时间</label><input type="datetime-local" v-model="form.startTime" /></div>
        <div class="field"><label class="field-label">截止时间</label><input type="datetime-local" v-model="form.endTime" /></div>
        <div class="field"><label class="field-label">满分</label>
          <div class="num-input" style="width:120px"><button @click="form.maxScore = Math.max(0, form.maxScore - 10)">−</button><input type="number" v-model="form.maxScore" min="0" /><button @click="form.maxScore += 10">＋</button></div>
        </div>
        <div><button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button></div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { toDatetimeLocal, datetimeLocalToISO } from '@/utils/time'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { adminHomeworkApi } from '@/api/admin'
import type { Homework } from '@/types'
const route = useRoute(); const toast = useToast()
const homeworkId = Number(route.params.homeworkId); const loading = ref(false); const saving = ref(false)
const hw = ref<Homework | null>(null); const form = ref({ name: '', description: '', startTime: '', endTime: '', maxScore: 100 })
onMounted(async () => {
  loading.value = true
  try { hw.value = (await adminHomeworkApi.get(homeworkId)).data; form.value = { name: hw.value.name, description: hw.value.description, startTime: toDatetimeLocal(hw.value.startTime), endTime: toDatetimeLocal(hw.value.endTime), maxScore: hw.value.maxScore } }
  finally { loading.value = false }
})
async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value, startTime: datetimeLocalToISO(form.value.startTime), endTime: datetimeLocalToISO(form.value.endTime) }
    await adminHomeworkApi.update(homeworkId, payload)
    toast.success('保存成功')
  } finally { saving.value = false }
}
</script>
