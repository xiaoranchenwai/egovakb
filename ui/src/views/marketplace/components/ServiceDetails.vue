<template>
  <div class="service-details-container">
    <div v-if="moduleInfo.markdown_docs" class="markdown-content mb-6">
      <VueMarkdownRender :source="moduleInfo.markdown_docs" class="markdown-body" />
    </div>

    <el-empty v-else description="没有找到工具" />
  </div>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue'
import VueMarkdownRender from 'vue-markdown-render'
import type { McpModuleInfo } from '@/api/type/mcp-square'

const props = defineProps<{
  moduleInfo: McpModuleInfo
}>()
</script>

<style scoped>
.service-details-container {
  height: 100%;
  width: 100%;
}

.markdown-content {
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 16px;
  border: 1px solid #eee;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.markdown-content:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}
</style> 