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

/**
 * 从 ISO 串中提取 YYYY-MM-DD 日期部分（服务端按 +08:00 返回，日期部分始终正确），
 * 并在浏览器本地时区构造当天午夜 0 点的时间戳。
 *
 * 为什么不能直接用 new Date(iso).setHours(0,0,0,0)：
 *   "2026-06-04T00:00:00+08:00" 在 UTC-5 浏览器中会被解析为 6月3日，
 *   .setHours(0,0,0,0) 就把课程开始日锁定到了 6月3日，
 *   导致 6月3日出现幽灵课节（课程实际 6月4日才开始）。
 */
function isoToLocalMidnight(iso: string): number {
  const m = iso.match(/^(\d{4}-\d{2}-\d{2})/)
  // "2026-06-04T00:00:00" 不带时区后缀 → JS 解析为浏览器本地时区的 6月4日午夜
  return m ? new Date(`${m[1]}T00:00:00`).getTime() : new Date(iso).setHours(0, 0, 0, 0)
}

/**
 * 从 sessions 的 classTime ISO 串提取时区偏移字符串（如 "+08:00"）。
 * 用于将 schedule 字符串里的原始时间值转换为含时区的 ISO 串，
 * 再由 new Date() 按浏览器本地时区展示，保证占位符槽位的时间也正确转换。
 */
function extractIsoOffset(sessions: ClassSession[]): string {
  const first = sessions.find(s => s.classTime)
  if (!first) return '+08:00'  // 无 session 时回退到服务器时区
  const m = first.classTime.match(/([+-]\d{2}:\d{2})$/)
  return m?.[1] ?? '+00:00'
}

/**
 * 将 schedule 里的小时/分钟（服务器时区）转换为浏览器本地时间的 HH:MM 字符串。
 * 通过把时间拼成含时区偏移的 ISO 串，再用 Date.getHours()/getMinutes() 完成转换。
 */
function scheduleTimeToLocal(
  dateRef: Date,   // 参考日期（决定年月日，用于构造 ISO 串）
  h: number, m: number,
  isoOffset: string,
): string {
  const iso = `${dateRef.getFullYear()}-${pad(dateRef.getMonth() + 1)}-${pad(dateRef.getDate())}T${pad(h)}:${pad(m)}:00${isoOffset}`
  const d = new Date(iso)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316']
const courseColor = (id: number) => COLORS[id % COLORS.length]

/** 解析 schedule 字符串，返回 { weekdays: number[], hour, minute, endHour?, endMinute? } */
function parseSchedule(schedule: string) {
  const FULL: Record<string, number> = {
    '周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周日': 6, '周天': 6,
  }
  const SHORT: Record<string, number> = {
    '一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6,
  }

  const timeRangeMatch = schedule.match(/(\d{1,2}):(\d{2})[–\-](\d{1,2}):(\d{2})/)
  const timeMatch = timeRangeMatch ?? schedule.match(/(\d{1,2}):(\d{2})/)
  const hour = timeMatch ? parseInt(timeMatch[1]!) : 9
  const minute = timeMatch ? parseInt(timeMatch[2]!) : 0
  const endHour = timeRangeMatch ? parseInt(timeRangeMatch[3]!) : undefined
  const endMinute = timeRangeMatch ? parseInt(timeRangeMatch[4]!) : undefined

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

  return { weekdays: [...weekdays].sort((a, b) => a - b), hour, minute, endHour, endMinute }
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

      const { weekdays, hour, minute, endHour, endMinute } = parseSchedule(course.schedule)

      // 这天在课程的课表里吗？
      if (!weekdays.includes(i)) continue

      // 这天在课程有效期内吗？
      // 用 isoToLocalMidnight 而非 new Date(iso).setHours(0,0,0,0)，
      // 避免跨时区时 +08:00 的日期被浏览器偏移到前一天。
      const courseStart = isoToLocalMidnight(course.startTime)
      const courseEnd = isoToLocalMidnight(course.endTime) + 86400000 - 1  // 当天最后一毫秒
      if (dateTs < courseStart || dateTs > courseEnd) continue

      // 找匹配的真实课节（同一天同课程）
      const matched = sessions.find(s => {
        const t = new Date(s.classTime).getTime()
        return t >= dateTs && t < dateEnd
      })

      let startStr: string
      let endStr: string
      if (matched) {
        const startDate = new Date(matched.classTime)
        startStr = `${pad(startDate.getHours())}:${pad(startDate.getMinutes())}`
        if (endHour !== undefined) {
          // 用 schedule 中的时长偏移 classTime，保证结束时间也按浏览器时区转换
          const durationMin = (endHour * 60 + (endMinute ?? 0)) - (hour * 60 + minute)
          const endDate = new Date(startDate.getTime() + durationMin * 60000)
          endStr = `${pad(endDate.getHours())}:${pad(endDate.getMinutes())}`
        } else {
          endStr = ''
        }
      } else {
        // 占位符：无实际课节。用 sessions 中任意一条的时区偏移把 schedule 里的时间转换为本地时区。
        const isoOffset = extractIsoOffset(sessions)
        startStr = scheduleTimeToLocal(date, hour, minute, isoOffset)
        endStr = endHour !== undefined
          ? scheduleTimeToLocal(date, endHour, endMinute!, isoOffset)
          : ''
      }
      const timeStr = endStr ? `${startStr}–${endStr}` : startStr

      // sortKey 统一用本地小时分钟，确保跨来源的槽位排序一致
      const sortKeyDate = matched
        ? new Date(matched.classTime)
        : (() => {
            const isoOffset = extractIsoOffset(sessions)
            const iso = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(hour)}:${pad(minute)}:00${isoOffset}`
            return new Date(iso)
          })()

      slots.push({
        courseId: course.id,
        courseName: course.name,
        teacherName: matched?.teacherName ?? course.teacherName ?? '',
        timeStr,
        sortKey: sortKeyDate.getHours() * 60 + sortKeyDate.getMinutes(),
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
