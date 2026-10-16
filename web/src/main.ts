// course 栏目的样式套件（构建时自动加 .mod-course 作用域），需在整站样式之前引入
import './course/assets/main.css'
import './core/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import { vReveal } from '@shared/reveal'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.directive('reveal', vReveal)

app.mount('#app')
