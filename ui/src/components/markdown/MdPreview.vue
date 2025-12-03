<template>
  <MdPreview :language="language" noIconfont noPrettier :codeFoldable="false" v-bind="$attrs" class="aaaa" @click.stop="onPreviewImg"/>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { MdPreview, config } from 'md-editor-v3'
import { getBrowserLang } from '@/locales/index'
import useStore from '@/stores'
// 引入公共库中的语言配置
import ZH_TW from '@vavt/cm-extension/dist/locale/zh-TW'
import { api as viewerApi } from 'v-viewer'
defineOptions({ name: 'MdPreview' })
const { user } = useStore()
const language = computed(() => user.getLanguage() || getBrowserLang() || '')
config({
  editorConfig: {
    languageUserDefined: {
      'zh-Hant': ZH_TW
    }
  }
})
const onPreviewImg = (e: any) => {
  const dom = e.target
  if (dom instanceof HTMLImageElement) {
    const imgSrc = dom.currentSrc
    viewerApi({
      images: [imgSrc]
    })
  }
  // e.target.currentSrc
}
</script>
