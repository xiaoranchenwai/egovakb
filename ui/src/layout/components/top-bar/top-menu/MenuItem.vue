<template>
  <div class="menu-item-container flex-center h-full" :class="isActive ? 'active' : ''"
    @click="handleClick"
    @mouseup="handleMouseUp">
    <!-- <div class="icon">
      <AppIcon :iconName="menu.meta ? (menu.meta.icon as string) : '404'" />
    </div> -->
    <div class="title">
      {{ $t(menu.meta?.title as string) }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { useRouter, useRoute, type RouteRecordRaw } from 'vue-router'
import { computed } from 'vue'
const router = useRouter()
const route = useRoute()

const props = defineProps<{
  menu: RouteRecordRaw
}>()

// 处理常规点击
const handleClick = () => {
  router.push({ name: props.menu.name })
}

// 处理鼠标按键
const handleMouseUp = (e: MouseEvent) => {
  // 鼠标中键点击 (button === 1)
  if (e.button === 1) {
    e.preventDefault()
    // 获取完整路径并在新窗口打开
    const url = `${window.location.origin}${router.resolve({ name: props.menu.name }).href}`
    window.open(url, '_blank')
  }
}

const isActive = computed(() => {
  const { name, path, meta } = route;
  return (name == props.menu.name && path == props.menu.path) || meta?.activeMenu == props.menu.path
})
</script>
<style lang="scss" scoped>
.menu-item-container {
  margin-right: 28px;
  cursor: pointer;
  font-size: 16px;
  position: relative;
  padding: 0 10px;

  .icon {
    font-size: 15px;
    margin-right: 5px;
    margin-top: 2px;
  }

  &:hover {
    // color: var(--el-color-primary);
    color: var(--app-header-text-color);
    background-color: var(--app-header-menu-active-bg-color);
  }
}

.active {
  // color: var(--el-color-primary);
  color: var(--app-header-text-color);
  background-color: var(--app-header-menu-active-bg-color);

  // &::after {
  //   position: absolute;
  //   bottom: 0;
  //   width: 100%;
  //   height: 2px;
  //   content: '';
  //   background-color: var(--el-color-primary-light-9);
  //   border-bottom: 3px solid var(--el-color-primary);
  // }
}
</style>
