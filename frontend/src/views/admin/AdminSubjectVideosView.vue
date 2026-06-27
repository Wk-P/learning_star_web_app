<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/admin/subjects" class="btn btn-secondary btn-sm" style="margin-bottom:8px">← 返回科目</router-link>
        <h1 class="page-title">{{ subjectName }} — 视频管理</h1>
      </div>
      <button class="btn btn-primary" @click="openAdd">+ 添加视频</button>
    </div>

    <div v-if="loading" class="skeleton" style="height:200px" />

    <div v-else-if="videos.length === 0" class="empty">
      <span class="empty-icon">📹</span>
      <p>暂无视频，点击上方按钮添加</p>
    </div>

    <div v-else class="video-list">
      <div v-for="(v, i) in videos" :key="v.index" class="video-item card">
        <div class="video-index text-muted text-sm">{{ i + 1 }}</div>
        <div class="video-info">
          <div class="video-title">{{ v.title }}</div>
          <a :href="v.url" target="_blank" rel="noopener" class="video-url text-sm text-secondary">{{ v.url }}</a>
        </div>
        <div class="video-actions">
          <button class="btn btn-secondary btn-sm" @click="openEdit(v)">编辑</button>
          <button class="btn btn-danger btn-sm" @click="handleDelete(v)">删除</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
        <div class="modal" style="max-width:520px">
          <div class="modal-header">
            <span>{{ editTarget ? '编辑视频' : '添加视频' }}</span>
            <button class="modal-close" @click="showModal = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field">
              <label class="field-label">标题</label>
              <input v-model="form.title" class="input" placeholder="如：【新概念英语 第一册】" />
            </div>
            <div class="field">
              <label class="field-label">B站链接</label>
              <input v-model="form.url" class="input" placeholder="https://www.bilibili.com/video/..." />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminSubjectApi } from '@/api/admin'
import { subjectApi } from '@/api/course'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import type { BilibiliVideo } from '@/types'

const route = useRoute()
const toast = useToast()
const { confirm } = useConfirm()

const subjectId = Number(route.params.subjectId)
const subjectName = ref('')
const videos = ref<BilibiliVideo[]>([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editTarget = ref<BilibiliVideo | null>(null)
const form = ref({ title: '', url: '' })

onMounted(async () => {
  loading.value = true
  try {
    const [subjectRes, videoRes] = await Promise.all([
      subjectApi.list(),
      adminSubjectApi.listVideos(subjectId),
    ])
    const subject = subjectRes.data.find(s => s.id === subjectId)
    subjectName.value = subject?.name ?? ''
    videos.value = videoRes.data
  } finally {
    loading.value = false
  }
})

function openAdd() {
  editTarget.value = null
  form.value = { title: '', url: '' }
  showModal.value = true
}

function openEdit(v: BilibiliVideo) {
  editTarget.value = v
  form.value = { title: v.title, url: v.url }
  showModal.value = true
}

async function handleSave() {
  if (!form.value.title.trim() || !form.value.url.trim()) {
    toast.warning('请填写标题和链接')
    return
  }
  saving.value = true
  try {
    if (editTarget.value) {
      await adminSubjectApi.updateVideo(subjectId, editTarget.value.index, form.value)
      toast.success('已更新')
    } else {
      await adminSubjectApi.addVideo(subjectId, form.value)
      toast.success('已添加')
    }
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    showModal.value = false
  } catch {
    toast.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(v: BilibiliVideo) {
  const ok = await confirm(`确认删除「${v.title}」？`)
  if (!ok) return
  try {
    await adminSubjectApi.deleteVideo(subjectId, v.index)
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    toast.success('已删除')
  } catch {
    toast.error('删除失败')
  }
}
</script>

<style scoped>
.page-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--c-text); }

.video-list { display: flex; flex-direction: column; gap: 10px; }
.video-item {
  display: flex; align-items: center; gap: 16px; padding: 14px 18px;
}
.video-index {
  min-width: 28px; font-size: 15px; font-weight: 600; flex-shrink: 0;
}
.video-info { flex: 1; min-width: 0; }
.video-title { font-size: 14px; font-weight: 600; color: var(--c-text); margin-bottom: 4px; }
.video-url {
  display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--c-primary); text-decoration: underline;
}
.video-actions { display: flex; gap: 8px; flex-shrink: 0; }
</style>
