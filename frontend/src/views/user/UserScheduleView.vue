<template>
  <div>
    <div class="toolbar">
      <h1 class="page-title" style="margin:0">课程表</h1>
      <div class="toolbar-spacer" />
      <div class="week-nav">
        <button class="btn btn-secondary btn-sm" @click="changeWeek(-1)">←</button>
        <span class="week-label">{{ weekLabel }}</span>
        <button class="btn btn-secondary btn-sm" @click="changeWeek(1)">→</button>
        <button v-if="weekOffset !== 0" class="btn btn-secondary btn-sm" @click="weekOffset = 0">本周</button>
      </div>
    </div>

    <div v-if="loading" class="skeleton" style="height:300px" />

    <template v-else>
      <!-- 桌面：7 列网格 -->
      <div class="sched-grid">
        <div v-for="day in weekDays" :key="day.key" class="sched-col">
          <div class="sched-day-header" :class="{ today: day.isToday }">
            <div class="sched-day-name">{{ day.name }}</div>
            <div class="sched-day-date">{{ day.shortDate }}</div>
          </div>
          <div class="sched-day-body">
            <div v-if="day.slots.length === 0" class="sched-empty">—</div>
            <component
              :is="slot.classId ? 'router-link' : 'div'"
              v-for="(slot, i) in day.slots"
              :key="i"
              v-bind="slot.classId ? { to: `/courses/${slot.courseId}/classes/${slot.classId}` } : {}"
              class="sched-card"
              :class="{ 'sched-card-link': slot.classId && !slot.cancelled, 'sched-card-cancelled': slot.cancelled }"
              :style="{ borderLeftColor: slot.cancelled ? '#d1d5db' : courseColor(slot.courseId) }"
            >
              <div class="sched-card-name">{{ slot.courseName }}</div>
              <div class="sched-card-time">{{ slot.timeStr }}</div>
              <div v-if="slot.cancelled" class="sched-card-cancelled-label">休讲</div>
              <div v-else-if="slot.teacherName" class="sched-card-teacher">{{ slot.teacherName }}</div>
            </component>
          </div>
        </div>
      </div>

      <!-- 移动端：按天列表 -->
      <div class="sched-list">
        <div v-for="day in weekDays" :key="day.key" class="sched-list-day">
          <div class="sched-list-header" :class="{ today: day.isToday }">
            <span>{{ day.name }}</span>
            <span class="sched-list-date">{{ day.shortDate }}</span>
          </div>
          <div v-if="day.slots.length === 0" class="sched-list-empty">无课</div>
          <component
            :is="slot.classId && !slot.cancelled ? 'router-link' : 'div'"
            v-for="(slot, i) in day.slots"
            :key="i"
            v-bind="slot.classId && !slot.cancelled ? { to: `/courses/${slot.courseId}/classes/${slot.classId}` } : {}"
            class="sched-list-card"
            :class="{ 'sched-list-cancelled': slot.cancelled }"
            :style="{ borderLeftColor: slot.cancelled ? '#d1d5db' : courseColor(slot.courseId) }"
          >
            <span class="sched-list-time">{{ slot.timeStr }}</span>
            <span class="sched-list-name">{{ slot.courseName }}</span>
            <span v-if="slot.cancelled" class="sched-list-cancelled-tag">休讲</span>
          </component>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEnrollmentStore } from '@/stores/enrollment'
import { courseApi } from '@/api/course'
import { classApi } from '@/api/class'
import type { Course, ClassSession } from '@/types'

const enrollment = useEnrollmentStore()
const loading = ref(false)
const weekOffset = ref(0)

// ── 已报课程详情 + 课节列表 ───────────────────────────────────
interface CourseWithSessions {
  course: Course
  sessions: ClassSession[]
}
const courseData = ref<CourseWithSessions[]>([])

// ── 工具 ──────────────────────────────────────────────────────
const pad = (n: number) => String(n).padStart(2, '0')

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']
const courseColor = (id: number) => COLORS[id % COLORS.length]

/** 解析 schedule 字符串，返回 { weekdays: number[], hour, minute } */
function parseSchedule(schedule: string) {
  const FULL: Record<string, number> = {
    '周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周日': 6, '周天': 6,
  }
  const SHORT: Record<string, number> = {
    '一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6,
  }

  const timeMatch = schedule.match(/(\d{1,2}):(\d{2})/)
  const hour = timeMatch ? parseInt(timeMatch[1]!) : 9
  const minute = timeMatch ? parseInt(timeMatch[2]!) : 0

  const dayPart = timeMatch ? schedule.slice(0, schedule.indexOf(timeMatch[0])) : schedule
  const weekdays = new Set<number>()
  let remaining = dayPart

  // 先匹配全称 "周X"
  for (const [name, wd] of Object.entries(FULL)) {
    if (remaining.includes(name)) {
      weekdays.add(wd)
      remaining = remaining.split(name).join(' ')
    }
  }
  // 再匹配单字缩写
  for (const [ch, wd] of Object.entries(SHORT)) {
    if (remaining.includes(ch)) weekdays.add(wd)
  }

  return { weekdays: [...weekdays].sort((a, b) => a - b), hour, minute }
}

/** 获取当周周一（offset=0 当周，-1 上周，+1 下周） */
function getMonday(offset: number): Date {
  const now = new Date()
  const dow = now.getDay()
  const diff = dow === 0 ? -6 : 1 - dow
  const mon = new Date(now)
  mon.setDate(now.getDate() + diff + offset * 7)
  mon.setHours(0, 0, 0, 0)
  return mon
}

const weekLabel = computed(() => {
  const mon = getMonday(weekOffset.value)
  const sun = new Date(mon); sun.setDate(mon.getDate() + 6)
  const f = (d: Date) => `${d.getMonth() + 1}月${d.getDate()}日`
  return `${mon.getFullYear()}年${f(mon)} ～ ${f(sun)}`
})

// ── 每周的槽位 ─────────────────────────────────────────────────
interface Slot {
  courseId: number
  courseName: string
  teacherName: string
  timeStr: string
  sortKey: number   // 用于排序：当天分钟数
  classId: number | null
  cancelled: boolean
}

const DAY_NAMES = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const weekDays = computed(() => {
  const mon = getMonday(weekOffset.value)
  const todayTs = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d.getTime() })()

  return DAY_NAMES.map((name, i) => {
    const date = new Date(mon)
    date.setDate(mon.getDate() + i)
    date.setHours(0, 0, 0, 0)
    const dateTs = date.getTime()
    const dateEnd = dateTs + 86400000

    const slots: Slot[] = []

    for (const { course, sessions } of courseData.value) {
      if (!course.schedule) continue

      const { weekdays, hour, minute } = parseSchedule(course.schedule)

      // 这天在课程的课表里吗？
      if (!weekdays.includes(i)) continue

      // 这天在课程有效期内吗？
      const courseStart = new Date(course.startTime).setHours(0, 0, 0, 0)
      const courseEnd = new Date(course.endTime).setHours(23, 59, 59, 999)
      if (dateTs < courseStart || dateTs > courseEnd) continue

      // 找匹配的真实课节（同一天同课程）
      const matched = sessions.find(s => {
        const t = new Date(s.classTime).getTime()
        return t >= dateTs && t < dateEnd
      })

      const timeStr = `${pad(hour)}:${pad(minute)}`
      slots.push({
        courseId: course.id,
        courseName: course.name,
        teacherName: matched?.teacherName ?? course.teacherName ?? '',
        timeStr: matched ? `${pad(new Date(matched.classTime).getHours())}:${pad(new Date(matched.classTime).getMinutes())}` : timeStr,
        sortKey: matched
          ? new Date(matched.classTime).getHours() * 60 + new Date(matched.classTime).getMinutes()
          : hour * 60 + minute,
        classId: matched?.id ?? null,
        cancelled: matched?.status === 'cancelled',
      })
    }

    // 按时间升序
    slots.sort((a, b) => a.sortKey - b.sortKey)

    return {
      name,
      key: date.toISOString(),
      shortDate: `${date.getMonth() + 1}/${date.getDate()}`,
      isToday: dateTs === todayTs,
      slots,
    }
  })
})

function changeWeek(n: number) { weekOffset.value += n }

// ── 数据加载 ───────────────────────────────────────────────────
onMounted(async () => {
  if (!enrollment.loaded) await enrollment.fetchEnrollments()
  if (enrollment.enrollments.size === 0) return

  loading.value = true
  try {
    const courseIds = [...enrollment.enrollments.keys()]
    const results = await Promise.all(
      courseIds.map(async courseId => {
        const [courseRes, clsRes] = await Promise.all([
          courseApi.get(courseId),
          classApi.listByCourse(courseId),
        ])
        return { course: courseRes.data, sessions: clsRes.data }
      })
    )
    courseData.value = results
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ── 周导航 ──────────────────────────────────────────────── */
.week-nav { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.week-label { font-size: 13px; color: var(--c-text-2); white-space: nowrap; }

/* ── 桌面 7 列网格 ───────────────────────────────────────── */
.sched-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}
.sched-list { display: none; }

.sched-col { display: flex; flex-direction: column; min-width: 0; }

.sched-day-header {
  text-align: center; padding: 8px 4px;
  border-radius: var(--r-sm);
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  margin-bottom: 6px;
}
.sched-day-header.today {
  background: var(--c-primary); border-color: var(--c-primary);
}
.sched-day-header.today .sched-day-name,
.sched-day-header.today .sched-day-date { color: #fff; }
.sched-day-name { font-size: 13px; font-weight: 600; color: var(--c-text); }
.sched-day-date { font-size: 11px; color: var(--c-text-3); margin-top: 2px; }

.sched-day-body { display: flex; flex-direction: column; gap: 6px; }
.sched-empty { text-align: center; font-size: 12px; color: var(--c-text-3); padding: 12px 0; }

.sched-card {
  display: block; padding: 8px 10px;
  border-radius: var(--r-sm);
  border: 1px solid var(--c-border);
  border-left-width: 3px;
  background: var(--c-surface);
}
.sched-card-link { transition: box-shadow var(--t); }
.sched-card-link:hover { box-shadow: var(--shadow); }
.sched-card-name { font-size: 12px; font-weight: 600; color: var(--c-text); line-height: 1.3; }
.sched-card-time { font-size: 11px; color: var(--c-text-2); margin-top: 3px; }
.sched-card-teacher { font-size: 11px; color: var(--c-text-3); margin-top: 2px; }
.sched-card-cancelled { background: #f3f4f6; }
.sched-card-cancelled .sched-card-name { color: #9ca3af; }
.sched-card-cancelled .sched-card-time { color: #d1d5db; }
.sched-card-cancelled-label { font-size: 10px; color: #9ca3af; margin-top: 3px; }

/* ── 移动端列表 ─────────────────────────────────────────── */
@media (max-width: 640px) {
  .sched-grid { display: none; }
  .sched-list { display: flex; flex-direction: column; gap: 12px; }

  .sched-list-day { display: flex; flex-direction: column; gap: 6px; }
  .sched-list-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 6px 12px; border-radius: var(--r-sm);
    background: var(--c-surface); border: 1px solid var(--c-border);
    font-size: 13px; font-weight: 600; color: var(--c-text);
  }
  .sched-list-header.today { background: var(--c-primary); border-color: var(--c-primary); color: #fff; }
  .sched-list-header.today .sched-list-date { color: rgba(255,255,255,0.8); }
  .sched-list-date { font-size: 12px; color: var(--c-text-3); }
  .sched-list-empty { font-size: 12px; color: var(--c-text-3); padding: 4px 12px; }
  .sched-list-card {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px; border-radius: var(--r-sm);
    border: 1px solid var(--c-border); border-left-width: 3px;
    background: var(--c-surface);
  }
  .sched-list-time { font-size: 13px; font-weight: 600; color: var(--c-text-2); white-space: nowrap; }
  .sched-list-name { font-size: 13px; color: var(--c-text); }
  .sched-list-cancelled { background: #f3f4f6; }
  .sched-list-cancelled .sched-list-time,
  .sched-list-cancelled .sched-list-name { color: #9ca3af; }
  .sched-list-cancelled-tag { font-size: 11px; color: #9ca3af; margin-left: auto; }
}
</style>
