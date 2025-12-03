<template>
  <component
    v-if="isIconfont"
    :is="
      Object.keys(iconMap).includes(iconName)
        ? iconMap[iconName].iconReader()
        : iconMap['404'].iconReader()
    "
    class="el-icon app-icon"
  >
  </component>
  <el-icon v-else-if="iconName">
    <component :is="iconName" />
  </el-icon>
  <span class="icon" v-else></span>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { iconMap } from '@/components/icons/index'
defineOptions({ name: 'AppIcon' })

const props = withDefaults(
  defineProps<{
    iconName?: string
  }>(),
  {
    iconName: ''
  }
)

const isIconfont = computed(() => props.iconName?.includes('app-'))
</script>

<style lang="scss" scoped>
.icon {
  width: 24px;
  height: 24px;
  position: relative;
  display: inline-block;
  &.app-view {
    background-image: url("../../assets/application/app-view.png");
    background-size: 100% 100%;
  }
  &.setting {
    background-image: url("../../assets/application/setting.png");
    background-size: 100% 100%;
  }
  &.copy {
    background-image: url("../../assets/application/copy.png");
    background-size: 90% 90%;
    background-position: center center;
  }
}
</style>
