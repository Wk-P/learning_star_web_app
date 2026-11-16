<template>
  <div class="admin-page">
    <div class="toolbar">
      <h2 class="page-title">分类与语言</h2>
      <el-button @click="openCategory()">新建分类</el-button>
      <el-button type="primary" :disabled="!store.categories.length" @click="openLanguage()">新建语言</el-button>
    </div>
    <p class="hint">结构：语言学习 → 语言分类 → 具体语言。语言的「标识」决定网址（/language/标识）和服务器媒体目录（media/languages/标识/），创建后不能修改。</p>

    <div v-if="loading" class="hint">加载中…</div>
    <div v-else-if="!store.categories.length" class="hint">还没有分类，先新建一个分类（如「东亚语言」）。</div>

    <section v-for="cat in store.categories" :key="cat.id" class="cat">
      <header class="cat-head">
        <span class="cat-name">{{ cat.name }}</span>
        <span class="cat-desc">{{ cat.description }}</span>
        <span class="cat-order">排序 {{ cat.sort_order }}</span>
        <el-button size="small" text @click="openCategory(cat)">编辑</el-button>
        <el-button size="small" text type="danger" @click="removeCategory(cat)">删除</el-button>
      </header>
      <el-table :data="cat.languages" class="admin-table" empty-text="这个分类下还没有语言">
        <el-table-column label="语言" min-width="160">
          <template #default="{ row }">
            <span class="dot" :style="{ background: row.color }" />{{ row.name }}
            <span v-if="row.native_name" class="muted">{{ row.native_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="slug" label="标识" width="100" />
        <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="70" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" text @click="openLanguage(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="removeLanguage(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <!-- 分类 -->
    <el-dialog v-model="catDialog" :title="catForm.id ? '编辑分类' : '新建分类'" width="420px">
      <el-form label-width="64px" @submit.prevent>
        <el-form-item label="名称"><el-input v-model="catForm.name" maxlength="50" placeholder="如：东亚语言" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="catForm.description" maxlength="200" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="catForm.sort_order" :step="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="catDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 语言 -->
    <el-dialog v-model="langDialog" :title="langForm.id ? '编辑语言' : '新建语言'" width="480px">
      <el-form label-width="76px" @submit.prevent>
        <el-form-item label="分类">
          <el-select v-model="langForm.category" style="width: 100%">
            <el-option v-for="c in store.categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="langForm.name" maxlength="50" placeholder="如：日语" /></el-form-item>
        <el-form-item label="标识">
          <el-input v-model="langForm.slug" maxlength="20" :disabled="!!langForm.id" placeholder="小写字母，如 ja、en、fr" />
        </el-form-item>
        <el-form-item label="本地名称"><el-input v-model="langForm.native_name" maxlength="50" placeholder="如：日本語（可选）" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="langForm.description" maxlength="200" /></el-form-item>
        <el-form-item label="主题色"><el-color-picker v-model="langForm.color" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="langForm.sort_order" :step="1" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="langForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="langDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveLanguage">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { errorDetail } from '@/core/api/http'
import { languageApi, type Language, type LanguageCategory } from '@/language/api'
import { useLanguageStore } from '@/language/stores/languages'

const store = useLanguageStore()
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try { await store.reload() } finally { loading.value = false }
})

// ── 分类 ──
const catDialog = ref(false)
const catForm = ref<Partial<LanguageCategory>>({})

function openCategory(c?: LanguageCategory) {
  catForm.value = c ? { id: c.id, name: c.name, description: c.description, sort_order: c.sort_order }
    : { name: '', description: '', sort_order: store.categories.length + 1 }
  catDialog.value = true
}

async function saveCategory() {
  const { id, ...data } = catForm.value
  if (!data.name?.trim()) return ElMessage.warning('请填写名称')
  saving.value = true
  try {
    if (id) await languageApi.updateCategory(id, data)
    else await languageApi.createCategory(data)
    catDialog.value = false
    await store.reload()
  } catch (e) {
    ElMessage.error(await errorDetail(e, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function removeCategory(c: LanguageCategory) {
  try {
    await ElMessageBox.confirm(`删除分类「${c.name}」？`, '确认', { type: 'warning' })
  } catch { return }
  try {
    await languageApi.deleteCategory(c.id)
    await store.reload()
  } catch (e) {
    ElMessage.error(await errorDetail(e, '删除失败'))
  }
}

// ── 语言 ──
const langDialog = ref(false)
const langForm = ref<Partial<Language>>({})

function openLanguage(l?: Language) {
  langForm.value = l ? { ...l } : {
    category: store.categories[0]?.id, name: '', slug: '', native_name: '', description: '',
    color: '#2ec4c0', sort_order: store.languages.length + 1, is_active: true,
  }
  langDialog.value = true
}

async function saveLanguage() {
  const { id, ...data } = langForm.value
  if (!data.name?.trim() || !data.slug?.trim()) return ElMessage.warning('请填写名称和标识')
  saving.value = true
  try {
    if (id) {
      delete data.slug // 标识不可修改
      await languageApi.updateLanguage(id, data)
    } else {
      await languageApi.createLanguage(data)
    }
    langDialog.value = false
    await store.reload()
  } catch (e) {
    ElMessage.error(await errorDetail(e, '保存失败'))
  } finally {
    saving.value = false
  }
}

async function removeLanguage(l: Language) {
  try {
    await ElMessageBox.confirm(
      `删除语言「${l.name}」？服务器上的媒体文件（media/languages/${l.slug}/）保留不动。`,
      '确认', { type: 'warning' },
    )
  } catch { return }
  try {
    await languageApi.deleteLanguage(l.id)
    await store.reload()
  } catch (e) {
    ElMessage.error(await errorDetail(e, '删除失败'))
  }
}
</script>

<style scoped>
.toolbar { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.page-title { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; margin-right: auto; }
.hint { font-size: 0.8rem; color: #8892a4; margin-bottom: 1.5rem; line-height: 1.6; }

.cat { margin-bottom: 2rem; }
.cat-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem; padding: 0 0.25rem; flex-wrap: wrap; }
.cat-name { font-size: 1rem; font-weight: 700; color: #e2e8f0; }
.cat-desc { font-size: 0.8rem; color: #8892a4; }
.cat-order { font-size: 0.75rem; color: #8892a4; margin-left: auto; }

.admin-table { border-radius: 0.75rem; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08) !important; }
.dot { display: inline-block; width: 0.6rem; height: 0.6rem; border-radius: 50%; margin-right: 0.5rem; vertical-align: middle; }
.muted { margin-left: 0.5rem; color: #8892a4; font-size: 0.8rem; }
</style>
