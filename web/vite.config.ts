import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
// @ts-expect-error -- postcss-prefix-selector 没有可用的类型声明
import prefixSelector from 'postcss-prefix-selector'

// 本地开发：后端（backend/，Django）跑在 8000，见 scripts/task.py
const API_DEV = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx(), vueDevTools()],
  css: {
    postcss: {
      plugins: [
        // course 栏目沿用原来的全局样式套件（.btn / .card / .modal …），
        // 统一加上 .mod-course 前缀，只在课程栏目内生效，不影响其他页面
        prefixSelector({
          prefix: '.mod-course',
          includeFiles: [/src\/course\/assets\//],
          transform(prefix: string, selector: string, prefixed: string) {
            if (/^(:root|html|body)$/.test(selector)) return prefix
            if (selector.startsWith('@')) return selector
            return prefixed
          },
        }),
      ],
    },
  },
  server: {
    proxy: {
      '/api': { target: API_DEV, changeOrigin: true },
      '/media': { target: API_DEV, changeOrigin: true },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      // 设计系统（动效、v-reveal、asset()）
      '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
    },
  },
})
