<script setup lang="ts">
import { ref, onMounted } from "vue";
import { AppHeader, AppMain } from '../components'
import useStore from '@/stores'
const { user } = useStore();

const hideMenus = ref(false);
onMounted(() => {
  const val = sessionStorage.getItem("hide-menus");
  if (val) {
    hideMenus.value = val === "1" ? true : false;
  }
});
</script>

<template>
  <div class="app-layout" :class="{hideMenus: hideMenus}">
    <AppHeader />
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''">
      <AppMain />
    </div>
  </div>
</template>
<style lang="scss">
@import './index.scss';
.app-layout.hideMenus {
  .app-header {
    display: none !important;
  }
  .app-main {
    padding: 0 !important;
  }
}
</style>
