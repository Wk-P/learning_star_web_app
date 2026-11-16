import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLanguageStore } from '@/language/stores/languages'

/** 当前网址 /language/:lang/... 对应的语言（语言列表未加载完时 language 为 undefined） */
export function useCurrentLanguage() {
  const route = useRoute()
  const store = useLanguageStore()
  store.load().catch(() => {})

  const slug = computed(() => (typeof route.params.lang === 'string' ? route.params.lang : ''))
  const language = computed(() => store.bySlug(slug.value))
  /** 列表已加载但没有这个语言（网址写错或已被删除 / 停用） */
  const notFound = computed(() => store.loaded && !language.value)
  /** 本语言内的路由，如 to('language-video') */
  const to = (name: 'language-home' | 'language-video' | 'language-audio' | 'language-file') =>
    ({ name, params: { lang: slug.value } })

  return { slug, language, notFound, to }
}
