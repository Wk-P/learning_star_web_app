<template>
  <!-- 课程栏目：套上 .mod-course，让原 course 站的样式套件只在这里生效。
       这里不再套 Transition：页面切换动画由外层（AppShell / AdminShell）按完整路径统一处理。
       两层 out-in Transition 嵌套时，离开课程栏目会让外层动画卡住，新页面显示为空白。 -->
  <div class="mod-course">
    <RouterView />
  </div>
</template>
