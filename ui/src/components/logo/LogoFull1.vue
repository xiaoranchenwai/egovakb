<template>
    <div class="title">
        <span class="logo"></span>
        {{ platformName }}
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import userSettingApi from '@/api/user-setting'

const platformName = ref('大模型智能应用平台')

onMounted(async () => {
  try {
    const res = await userSettingApi.getSetting({
      name: 'platformName',
      setting_type: 'config'
    })
    if (res.data?.value) {
      platformName.value = res.data.value
    }
  } catch (error) {
    console.error('获取平台名称设置失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.title {
    color: var(--app-header-text-color);
    font-size: 18px;
    display: flex;
    align-items: center;

    .logo {
        width: 42px;
        height: 32px;
        display: inline-block;
        position: relative;
        background-image: url("@/assets/logo/logo.png") !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 100% 100% !important;
        margin-right: 12px;
    }
}
</style>