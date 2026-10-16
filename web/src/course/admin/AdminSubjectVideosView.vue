<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/admin/course/subjects" class="btn btn-secondary btn-sm" style="margin-bottom:8px">← 返回科目</router-link>
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

    <!-- 添加弹窗（粘贴一行） -->
    <Teleport to="#course-layer">
      <div v-if="showAddModal" class="modal-backdrop" @click.self="showAddModal = false">
        <div class="modal" style="max-width:560px">
          <div class="modal-header">
            <span>添加视频</span>
            <button class="modal-close" @click="showAddModal = false">✕</button>
          </div>
          <div class="modal-body" style="padding-top:20px">
            <div class="field">
              <label class="field-label">粘贴一行</label>
              <textarea
                v-model="addLine"
                class="textarea"
                rows="2"
                placeholder="【视频标题】 https://www.bilibili.com/video/..."
                style="resize:vertical;font-size:13px"
              />
              <p class="field-hint">与 txt 文件格式一致：标题 + 空格 + 链接</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAddModal = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleAdd">保存</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 编辑弹窗（title + url） -->
    <Teleport to="#course-layer">
      <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
        <div class="modal" style="max-width:520px">
          <div class="modal-header">
            <span>编辑视频</span>
            <button class="modal-close" @click="showEditModal = false">✕</button>
          </div>
          <div class="modal-body" style="display:flex;flex-direction:column;gap:14px;padding-top:20px">
            <div class="field">
              <label class="field-label">标题</label>
              <input v-model="editForm.title" class="input" placeholder="视频标题" />
            </div>
            <div class="field">
              <label class="field-label">B站链接</label>
              <input v-model="editForm.url" class="input" placeholder="https://www.bilibili.com/video/..." />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button class="btn btn-primary" :class="{ loading: saving }" @click="handleEditSave">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminSubjectApi } from '@/course/api/admin'
import { subjectApi } from '@/course/api/course'
import { useToast } from '@/course/composables/useToast'
import { useConfirm } from '@/course/composables/useConfirm'
import type { BilibiliVideo } from '@/course/types'

const route = useRoute()
const toast = useToast()
const { confirm } = useConfirm()

const subjectId = Number(route.params.subjectId)
const subjectName = ref('')
const videos = ref<BilibiliVideo[]>([])
const loading = ref(false)
const saving = ref(false)

// 添加弹窗
const showAddModal = ref(false)
const addLine = ref('')

// 编辑弹窗
const showEditModal = ref(false)
const editTarget = ref<BilibiliVideo | null>(null)
const editForm = ref({ title: '', url: '' })

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
  addLine.value = ''
  showAddModal.value = true
}

function openEdit(v: BilibiliVideo) {
  editTarget.value = v
  editForm.value = { title: v.title, url: v.url }
  showEditModal.value = true
}

async function handleAdd() {
  const line = addLine.value.trim()
  if (!line) { toast.warning('请输入内容'); return }
  saving.value = true
  try {
    await adminSubjectApi.addVideo(subjectId, { line })
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    showAddModal.value = false
    toast.success('已添加')
  } catch (e: any) {
    const msg = e?.response?.data?.detail || '格式错误，应为「标题 https://...」'
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

async function handleEditSave() {
  if (!editForm.value.title.trim() || !editForm.value.url.trim()) {
    toast.warning('请填写标题和链接')
    return
  }
  saving.value = true
  try {
    await adminSubjectApi.updateVideo(subjectId, editTarget.value!.index, editForm.value)
    const { data } = await adminSubjectApi.listVideos(subjectId)
    videos.value = data
    showEditModal.value = false
    toast.success('已更新')
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
.field-hint { font-size: 12px; color: var(--c-text-3); margin-top: 6px; }
</style>
