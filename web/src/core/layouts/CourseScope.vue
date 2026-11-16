<template>
  <div class="mod-course">
    <!-- 课程栏目：套上 .mod-course，让原 course 站的样式套件只在这里生效。
         注意：注释必须写在根元素里面。写在外面时开发模式会保留它，组件变成多根节点，
         外层 <Transition mode="out-in"> 离开后不再渲染新页面，内容区一片空白。 -->
    <RouterView />
  </div>
</template>
