<template>
  <!-- 课程栏目：套上 .mod-course，让原 course 站的样式套件只在这里生效 -->
  <div class="mod-course">
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </div>
</template>
