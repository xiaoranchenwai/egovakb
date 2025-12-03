<template>
  <CardBox
    shadow="never"
    :title="data.title || '-'"
    class="paragraph-source-card cursor mb-8 paragraph-source-card-height"
    :class="data.is_active ? '' : 'disabled'"
    :showIcon="false"
  >
    <template #icon>
      <AppAvatar class="mr-12 avatar-light" :size="22"> {{ index + 1 + '' }}</AppAvatar>
    </template>
    <div class="active-button primary">{{ score?.toFixed(3) || data.similarity?.toFixed(3) }}</div>
    <template #description>
      <el-scrollbar height="150">
        <div v-if="props.data.chunk_data" class="chunk-preview">
          <div class="chunk-header">
            <el-tag size="small" type="success">命中分块</el-tag>
            <div class="chunk-score">
              <span class="score-value">{{ props.data.similarity.toFixed(2) }}</span>
              <div class="score-bar">
                <div class="score-progress" :style="{width: getScorePercentage(props.data.similarity) + '%'}"></div>
              </div>
            </div>
          </div>
          <div class="chunk-content">{{ props.data.chunk_data }}</div>
        </div>
        <MdPreview ref="editorRef" editorId="preview-only" :modelValue="content" noImgZoomIn/>
      </el-scrollbar>
    </template>
    <template #footer>
      <div class="footer-content flex-between">
        <el-text class="flex align-center item">
          <img :src="getImgUrl(data?.document_name?.trim() || '')" alt="" width="20" class="mr-4" />

          <template v-if="meta?.source_url">
            <a
              :href="getNormalizedUrl(meta?.source_url)"
              target="_blank"
              class="ellipsis-1 break-all"
              :title="data?.document_name?.trim()"
            >
              {{ data?.document_name?.trim() }}
            </a>
          </template>
          <template v-else>
            <el-link v-if="data?.document_url" :href="data?.document_url" target="_blank">
              {{ data?.document_name?.trim() }}
            </el-link>
            <span v-else class="ellipsis-1 break-all" :title="data?.document_name?.trim()">
              {{ data?.document_name?.trim() }}
            </span>
          </template>
        </el-text>
        <div class="flex align-center item" style="line-height: 32px">
          <AppAvatar class="mr-8 avatar-blue" shape="square" :size="18">
            <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
          </AppAvatar>
          <span class="ellipsis-1 break-all" :title="data?.dataset_name">
            {{ data?.dataset_name }}</span
          >
        </div>
      </div>
    </template>
  </CardBox>
</template>
<script setup lang="ts">
import { getImgUrl, getNormalizedUrl } from '@/utils/utils'
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  },
  content: {
    type: String,
    default: ''
  },
  index: {
    type: Number,
    default: 0
  },
  score: {
    type: Number,
    default: null
  }
})

// 获取分块数据
const chunkData = computed(() => {
  console.log('pc chunkData', props.data)
  if (!props.data?.chunk_data) return null
  
  try {
    return JSON.parse(props.data.chunk_data)
  } catch (e) {
    console.error('Failed to parse chunk_data:', e)
    return null
  }
})

// 计算分数的百分比
const getScorePercentage = (score: number) => {
  return Math.min(Math.round(score * 100), 100)
}

const isMetaObject = computed(() => typeof props.data.meta === 'object')
const parsedMeta = computed(() => {
  try {
    return JSON.parse(props.data.meta)
  } catch (e) {
    return {}
  }
})

const meta = computed(() => (isMetaObject.value ? props.data.meta : parsedMeta.value))
</script>
<style lang="scss" scoped>
.paragraph-source-card {
  .footer-content {
    .item {
      max-width: 50%;
    }
  }
}

.paragraph-source-card-height {
  height: 260px;
}

@media only screen and (max-width: 768px) {
  .paragraph-source-card-height {
    height: 285px;
  }
  .paragraph-source-card {
    .footer-content {
      display: block;

      .item {
        max-width: 100%;
      }
    }
  }
}

.highlighted-chunks-container {
  margin-top: 16px;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
  background-color: #f0f9eb;
  overflow: hidden;
}

.highlighted-title {
  padding: 8px 12px;
  border-bottom: 1px solid #e1f3d8;
  background-color: #f0f9eb;
  font-weight: bold;
}

.highlighted-chunk-item {
  padding: 8px 12px;
  border-bottom: 1px solid #e1f3d8;
  
  &:last-child {
    border-bottom: none;
  }
}

.highlighted-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 12px;
}

.highlighted-score-container {
  display: flex;
  align-items: center;
}

.score-percentage {
  font-size: 13px;
  font-weight: 700;
  color: #67c23a;
  margin-right: 8px;
}

.highlighted-score {
  color: #67c23a;
  font-weight: 600;
  background-color: #f0f9eb;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #c2e7b0;
}

.score-bar-container {
  height: 6px;
  background-color: rgba(103, 194, 58, 0.2);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.score-bar {
  height: 100%;
  background-color: #67c23a;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.highlighted-content {
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  background-color: white;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
}

.chunk-preview {
  margin-bottom: 12px;
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
  overflow: hidden;
}

.chunk-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #f0f9eb;
  border-bottom: 1px solid #e1f3d8;
}

.chunk-score {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-value {
  font-size: 13px;
  font-weight: 600;
  color: #67c23a;
}

.score-bar {
  width: 60px;
  height: 4px;
  background-color: rgba(103, 194, 58, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.score-progress {
  height: 100%;
  background-color: #67c23a;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.chunk-content {
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  background-color: white;
  border-bottom: 1px solid #e1f3d8;
}
</style>
