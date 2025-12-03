<template>
  <div class="header">
    <!-- ... existing code ... -->
    <div class="menu-list">
      <div 
        v-for="item in menuList" 
        :key="item.path"
        class="menu-item"
        :class="{ active: route.path.includes(item.path) }"
        @click="handleClick(item)"
        @contextmenu.prevent="handleRightClick(item)"
      >
        {{ item.title }}
      </div>
    </div>
    <!-- ... existing code ... -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuList = ref([
  {
    title: '应用广场',
    path: '/application'
  },
  {
    title: '知识库',
    path: '/dataset'
  },
  {
    title: '函数库', 
    path: '/function-lib'
  },
  {
    title: 'MCP', 
    path: '/mcp'
  },
  {
    title: '定时任务',
    path: '/schedule'
  }
])

const handleClick = (item: any) => {
  router.push(item.path)
}

const handleRightClick = (item: any) => {
  // 在新窗口打开链接
  const url = `${window.location.origin}${item.path}`
  window.open(url, '_blank')
}
</script>

<style lang="scss" scoped>
.menu-item {
  cursor: pointer;
  /* ... existing styles ... */
}
</style> 