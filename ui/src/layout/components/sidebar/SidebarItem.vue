<template>
  <div v-if="(!menu.meta || !menu.meta.hidden) && showMenu()" class="sidebar-item">
    <el-sub-menu v-if="!menu?.meta?.hideChildren && menu?.children && menu?.children.length > 0" :index="menu.path"
      popper-class="sidebar-container-popper">
      <template #title>
        <el-icon>
          <AppIcon v-if="menu.meta && menu.meta.icon" :iconName="menuIcon" class="sidebar-icon" />
        </el-icon>
        <span>{{ $t(menu.meta?.title as string) }}</span>
      </template>
      <!--      v-hasPermission="child.meta?.permission"-->
      <sidebar-item v-for="(child, index) in menu?.children" :key="index" :menu="child" :activeMenu="activeMenu">
      </sidebar-item>
    </el-sub-menu>
    <el-menu-item v-else class="ccc" ref="subMenu" :index="menu.path" popper-class="sidebar-popper"
      @click="clickHandle(menu)" :class="{'is-active': isActive}">
      <template #title>
        <AppIcon v-if="menu.meta && menu.meta.icon" :iconName="menuIcon" class="sidebar-icon" />
        <span v-if="menu.meta && menu.meta.title">{{ $t(menu.meta?.title as string) }}</span>
      </template>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute, type RouteRecordRaw } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
const props = defineProps<{
  menu: RouteRecordRaw
  activeMenu: any
}>()

const router = useRouter()
const route = useRoute()
const {
  params: { id, type }
} = route as any

function showMenu() {
  if (isWorkFlow(type)) {
    // @ts-ignore
    return !["AppAccess", "AppSetting"].includes(props!.menu!.name); // 隐藏应用接入
  } else {
    // @ts-ignore
    return !["Appflow", "AppAccess"].includes(props!.menu!.name);
  }
}

function clickHandle(item?: any) {
  if (isWorkFlow(type) && item?.name === 'AppSetting') {
    router.push({ path: `/application/${id}/workflow` })
  }
}
const menuIcon = computed(() => {
  if (props.activeMenu === props.menu.path) {
    return props.menu.meta?.iconActive || props.menu?.meta?.icon
  } else {
    return props.menu?.meta?.icon
  }
});

const isActive = computed(() => {
  const { path, meta } = route;
  return path.includes(props.menu.path);
})
</script>

<style scoped lang="scss">
.sidebar-item {
  color: #223355 !important;

  .sidebar-icon {
    font-size: 20px;
    margin-top: -2px;
  }

  .el-menu-item {
    padding: 13px 12px 13px 16px !important;
    font-weight: 500;
    border-radius: 4px;

    &:hover {
      background: none;
      color: var(--el-color-primary);
    }
  }

  :deep(.el-sub-menu__title) {
    padding: 13px 12px 13px 16px !important;

    &:hover {
      background: none;
      color: var(--el-color-primary);
    }
  }

  .el-sub-menu {
    .el-menu-item {
      padding-left: 43px !important;

      >span {
        color: #223355;
      }
    }
  }

  .el-menu-item.is-active {
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
}
</style>
