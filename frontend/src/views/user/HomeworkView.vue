<template>
  <div>
    <div v-if="loading" class="skeleton" style="height:300px" />
    <div v-else-if="hw" class="card">
      <div class="card-header">
        {{ hw.name }}
        <span :class="['badge', statusBadge(hw.status)]" style="margin-left:10px">{{ statusLabel(hw.status) }}</span>
      </div>
      <div class="card-body" style="display:flex;flex-direction:column;gap:20px">

        <!-- 基本信息 -->
        <div class="desc-list">
          <div class="desc-row"><span class="desc-label">所属课程</span><span class="desc-value">{{ hw.courseName }}</span></div>
          <div class="desc-row"><span class="desc-label">作业描述</span><span class="desc-value" style="white-space:pre-wrap">{{ hw.description || '暂无' }}</span></div>
          <div class="desc-row"><span class="desc-label">开始时间</span><span class="desc-value">{{ fmt(hw.startTime) }}</span></div>
          <div class="desc-row"><span class="desc-label">截止时间</span><span class="desc-value">{{ fmt(hw.endTime) }}</span></div>
          <div class="desc-row"><span class="desc-label">满分</span><span class="desc-value">{{ hw.maxScore }} 分</span></div>
        </div>

        <!-- 提交状态区 -->
        <div>
          <h3 class="section-title">提交状态</h3>

          <!-- ① 作业未开始 -->
          <div v-if="hw.status === 'not_started'" class="status-box status-info">
            <span style="font-size:22px">📅</span>
            <div>
              <div style="font-weight:600">作业尚未开始</div>
              <div>开放时间：{{ fmt(hw.startTime) }}</div>
            </div>
          </div>

          <!-- ② 进行中：可提交 / 重提交 -->
          <template v-else-if="hw.status === 'in_progress'">
            <!-- 已提交记录 -->
            <div v-if="submission" class="submission-record">
              <div class="submission-meta">
                <span class="badge badge-success">已提交</span>
                <span style="font-size:13px;color:var(--c-text-2);margin-left:10px">
                  提交时间：{{ fmt(submission.submittedAt) }}
                </span>
              </div>
              <a
                v-if="submission.fileUrl"
                :href="submission.fileUrl"
                target="_blank"
                class="submission-file"
              >
                📎 {{ submission.fileName || '查看提交文件' }}
              </a>
            </div>
            <div v-else class="status-box status-info">
              <span style="font-size:22px">📝</span>
              <div>
                <div style="font-weight:600">尚未提交</div>
                <div>截止时间：{{ fmt(hw.endTime) }}</div>
              </div>
            </div>

            <!-- 上传按钮 -->
            <div style="margin-top:14px;display:flex;flex-direction:column;gap:6px">
              <!-- 隐藏的 file input，通过 ref 触发 -->
              <input
                ref="fileInputRef"
                type="file"
                style="display:none"
                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.gif,.zip,.tar.gz,.py,.js,.ts,.java,.c,.cpp,.txt"
                @change="handleUpload"
              />
              <button
                class="btn btn-primary"
                style="width:fit-content"
                :class="{ loading: uploading }"
                :disabled="uploading"
                @click="fileInputRef?.click()"
              >
                {{ uploading ? '' : (submission ? '重新提交' : '提交作业') }}
              </button>
              <div class="upload-tip">支持 pdf / docx / 截图 / 代码文件，不超过 50 MB</div>
            </div>
          </template>

          <!-- ③ 截止日期已过：显示提交记录 + 评分 -->
          <template v-else-if="hw.status === 'ended' || courseEnded">
            <!-- 提交记录 -->
            <div v-if="submission" class="submission-record" style="margin-bottom:14px">
              <div class="submission-meta">
                <span class="badge badge-info">已提交</span>
                <span style="font-size:13px;color:var(--c-text-2);margin-left:10px">
                  {{ fmt(submission.submittedAt) }}
                </span>
              </div>
              <a
                v-if="submission.fileUrl"
                :href="submission.fileUrl"
                target="_blank"
                class="submission-file"
              >
                📎 {{ submission.fileName || '查看提交文件' }}
              </a>
            </div>
            <div v-else style="margin-bottom:14px">
              <span class="badge badge-warning">未提交</span>
            </div>

            <!-- 评分结果 -->
            <div v-if="submission?.graded" class="status-box status-success">
              <span style="font-size:22px">✅</span>
              <div>
                <div style="font-weight:600;color:#065f46">已评分</div>
                <div style="color:#065f46;font-size:20px;font-weight:700">
                  {{ submission.score }} / {{ hw.maxScore }} 分
                </div>
              </div>
            </div>
            <div v-else class="status-box status-warning">
              <span style="font-size:22px">⏳</span>
              <div>
                <div style="font-weight:600;color:#92400e">等待评分</div>
                <div style="color:#92400e">-- / {{ hw.maxScore }} 分</div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <div v-else-if="!loading" class="empty">
      <span class="empty-icon">📭</span>
      <p>作业不存在或无权访问</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmt, fmtDate, toDatetimeLocal, toDateLocal } from '@/utils/time'
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEnrollmentStore } from '@/stores/enrollment'
import { useToast } from '@/composables/useToast'
import { useBreadcrumb } from '@/composables/useBreadcrumb'
import { homeworkApi } from '@/api/homework'
import type { Homework, HomeworkSubmission, HomeworkStatus } from '@/types'

const route = useRoute()
const enrollment = useEnrollmentStore()
const toast = useToast()
const { setSegments } = useBreadcrumb()

const homeworkId = Number(route.params.homeworkId)
const loading = ref(false)
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const hw = ref<Homework | null>(null)
const submission = ref<HomeworkSubmission | null>(null)

const courseEnded = computed(() =>
  hw.value ? enrollment.getCourseStatus(hw.value.courseId) === 'ended' : false
)

onMounted(async () => {
  loading.value = true
  try {
    const [hwRes, subRes] = await Promise.allSettled([
      homeworkApi.get(homeworkId),
      homeworkApi.mySubmission(homeworkId),
    ])
    if (hwRes.status === 'fulfilled') {
      hw.value = hwRes.value.data
      setSegments([
        { label: '我的作业', path: '/user/homework' },
        { label: hw.value.name },
      ])
    }
    if (subRes.status === 'fulfilled') submission.value = subRes.value.data
  } finally {
    loading.value = false
  }
})

async function handleUpload(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 50 * 1024 * 1024) {
    toast.error('文件不能超过 50MB')
    input.value = ''
    return
  }
  uploading.value = true
  try {
    submission.value = (await homeworkApi.submit(homeworkId, file)).data
    toast.success('提交成功')
  } catch {
    toast.error('提交失败，请重试')
  } finally {
    uploading.value = false
    input.value = ''  // 清空 input，允许重复选同一文件
  }
}

const statusLabel = (s: HomeworkStatus) =>
  ({ not_started: '未开始', in_progress: '进行中', ended: '已结束' }[s])
const statusBadge = (s: HomeworkStatus) =>
  ({ not_started: 'badge-info', in_progress: 'badge-success', ended: 'badge-warning' }[s])
</script>

<style scoped>
.status-box {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: var(--r);
  font-size: 14px;
  line-height: 1.6;
}
.status-info    { background: var(--c-info-light); color: var(--c-text-2); }
.status-success { background: var(--c-success-light); }
.status-warning { background: var(--c-warning-light); }

.submission-record {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  background: var(--c-info-light);
  border-radius: var(--r);
  border: 1px solid var(--c-border);
}
.submission-meta { display: flex; align-items: center; }
.submission-file {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--c-primary);
  text-decoration: none;
  font-weight: 500;
}
.submission-file:hover { text-decoration: underline; }

.upload-tip {
  font-size: 12px;
  color: var(--c-text-3);
}
</style>
