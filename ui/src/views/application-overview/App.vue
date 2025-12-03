<template>
    <router-view></router-view>
</template>

<script setup lang="ts">
  import { onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'

  const router = useRouter()
  const route = useRoute()

  onMounted(() => {
    console.log(route)
    if (route.fullPath.endsWith('/overview')) {
      const path = route.fullPath.replace('/overview', '/overviewIndex')
      router.push({
        path: path
      })
    }
  })
</script>

<style scoped>

</style>