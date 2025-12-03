<template>
  <div class="login-warp flex-center">
    <div class="login-container w-full h-full">
      <div class="login-image" :style="{ backgroundImage: `url(${loginImage})` }">
        <div class="login-title-img"></div>
        <div class="login-content">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { getThemeImg } from '@/utils/theme'
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
defineProps({
  lang: {
    type: Boolean,
    default: true
  }
})
defineOptions({ name: 'LoginLayout' })
const { user } = useStore()

const changeLang = (lang: string) => {
  useLocalStorage(localeConfigKey, getBrowserLang()).value = lang
  window.location.reload()
}

const currentLanguage = computed(() => {
  return langList.value?.filter((v: any) => v.value === user.getLanguage())?.[0]?.label
})

const fileURL = computed(() => {
  if (user.themeInfo?.loginImage) {
    if (typeof user.themeInfo?.loginImage === 'string') {
      return user.themeInfo?.loginImage
    } else {
      return URL.createObjectURL(user.themeInfo?.loginImage)
    }
  } else {
    return ''
  }
})

const loginImage = computed(() => {
  return new URL("../../assets/theme/bg.png", import.meta.url);
})
</script>
<style lang="scss" scoped>
.login-warp {
  height: 100vh;

  .login-image {
    background-repeat: no-repeat;
    background-position: center;
    background-size: cover;
    width: 100%;
    height: 100%;
  }

  .login-content {
    position: absolute;
    right: 140px;
    top: 50%;
    transform: translateY(-50%);
  }

  .login-title-img {
    width: 566px;
    height: 86px;
    background-image: url("../../assets/theme/logo.png") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 100% 100% !important;
    position: absolute;
    left: 100px;
    top: 70px;
  }
}
</style>
