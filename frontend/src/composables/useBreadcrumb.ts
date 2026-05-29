import { ref } from 'vue'

export interface BreadcrumbSegment {
  label: string
  path?: string
}

// 全局单例：当前页面的动态面包屑段
const _segments = ref<BreadcrumbSegment[]>([])

export function useBreadcrumb() {
  function setSegments(segments: BreadcrumbSegment[]) {
    _segments.value = segments
  }
  function clearSegments() {
    _segments.value = []
  }
  return { segments: _segments, setSegments, clearSegments }
}
