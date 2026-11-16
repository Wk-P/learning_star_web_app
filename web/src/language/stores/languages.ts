import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { languageApi, type Language, type LanguageCategory } from '@/language/api'

/** 语言分类与语言列表：整站共用，加载一次；后台增删改后调用 reload() */
export const useLanguageStore = defineStore('languages', () => {
  const categories = ref<LanguageCategory[]>([])
  const loaded = ref(false)
  let pending: Promise<void> | null = null

  const languages = computed<Language[]>(() => categories.value.flatMap((c) => c.languages))

  function load(force = false): Promise<void> {
    if (loaded.value && !force) return Promise.resolve()
    pending ??= languageApi.categories()
      .then((data) => { categories.value = data; loaded.value = true })
      .finally(() => { pending = null })
    return pending
  }

  const bySlug = (slug: unknown) => languages.value.find((l) => l.slug === slug)

  function clear() {
    categories.value = []
    loaded.value = false
  }

  return { categories, languages, loaded, load, reload: () => load(true), bySlug, clear }
})
