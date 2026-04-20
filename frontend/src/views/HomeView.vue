<template>
  <div clas="wrapper">
    <RouterLink :to="{ name: 'user-dashboard'}" class="link">User Dashbord</RouterLink>
    <RouterLink :to="{ name: 'admin-dashboard'}" class="link">Admin Dashbord</RouterLink>
  </div>
</template>
<script setup lang="ts">
</script>
<style scoped>
.wrapper {
  display: flex;
  justify-content: space-evenly;
  width: 100%;
}

.link {
  display: block;
  padding: 1rem;
}
</style>
