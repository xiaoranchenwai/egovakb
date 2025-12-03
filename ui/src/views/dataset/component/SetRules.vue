<template>
  <div class="set-rules">
    <el-row>
      <el-col :span="10" class="p-24">
        <h4 class="title-decoration-1 mb-16">{{ $t('views.document.setRules.title.setting') }}</h4>
        <div class="set-rules__right">
          <el-scrollbar>
            <div class="left-height" @click.stop>
              <el-radio-group v-model="radio" class="set-rules__radio">
                <el-card shadow="never" class="mb-16" :class="radio === '1' ? 'active' : ''">
                  <el-radio value="1" size="large">
                    <p class="mb-4">{{ $t('views.document.setRules.intelligent.label') }}</p>
                    <el-text type="info">{{
                      $t('views.document.setRules.intelligent.text')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card shadow="never" class="mb-16" :class="radio === '2' ? 'active' : ''">
                  <el-radio value="2" size="large">
                    <p class="mb-4">{{ $t('views.document.setRules.advanced.label') }}</p>
                    <el-text type="info">
                      {{ $t('views.document.setRules.advanced.text') }}
                    </el-text>
                  </el-radio>

                  <el-card
                    v-if="radio === '2'"
                    shadow="never"
                    class="card-never mt-16"
                    style="margin-left: 30px"
                  >
                    <div class="set-rules__form">
                      <div class="form-item mb-16">
                        <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">{{
                            $t('views.document.setRules.patterns.label')
                          }}</span>
                          <el-tooltip
                            effect="dark"
                            :content="$t('views.document.setRules.patterns.tooltip')"
                            placement="right"
                          >
                            <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                          </el-tooltip>
                        </div>
                        <div @click.stop>
                          <el-select
                            v-model="form.patterns"
                            multiple
                            allow-create
                            default-first-option
                            filterable
                            :placeholder="$t('views.document.setRules.patterns.placeholder')"
                          >
                            <el-option
                              v-for="(item, index) in splitPatternList"
                              :key="index"
                              :label="item.key"
                              :value="item.value"
                            >
                              <div class="split-pattern-option">
                                <div class="option-key">{{ item.key }}</div>
                                <div class="option-content">
                                  <div 
                                    v-if="item.recommendedLevel !== undefined && item.recommendedLevel !== null"
                                    class="recommendation-area"
                                  >
                                    <div
                                      class="recommended-badge"
                                      :class="[`level-${item.recommendedLevel}`]"
                                    >
                                      <AppIcon iconName="app-recommend" />
                                    </div>
                                    <div class="stars-container">
                                      <el-icon 
                                        v-for="n in 5" 
                                        :key="n" 
                                        :class="{ active: n <= item.recommendedLevel }"
                                      >
                                        <star-filled v-if="n <= item.recommendedLevel" />
                                        <star v-else />
                                      </el-icon>
                                    </div>
                                  </div>
                                  <el-tooltip
                                    effect="dark"
                                    :content="item.description"
                                    placement="right"
                                  >
                                    <el-text
                                      class="option-description"
                                      type="info"
                                      truncated
                                    >
                                      {{ item.description }}
                                    </el-text>
                                  </el-tooltip>
                                </div>
                              </div>
                            </el-option>
                          </el-select>
                        </div>
                      </div>
                      <div class="form-item mb-16">
                        <div class="title mb-8">
                          {{ $t('views.document.setRules.limit.label') }}
                        </div>
                        <el-slider
                          v-model="form.limit"
                          show-input
                          :show-input-controls="false"
                          :min="50"
                          :max="100000"
                        />
                      </div>
                      <div class="form-item mb-16">
                        <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">{{
                            $t('views.document.setRules.chunk_patterns.label')
                          }}</span>
                          <el-tooltip
                            effect="dark"
                            :content="$t('views.document.setRules.chunk_patterns.tooltip')"
                            placement="right"
                          >
                            <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                          </el-tooltip>
                        </div>
                        <div @click.stop>
                          <el-input v-model="form.chunk_patterns" placeholder="请输入子分段标识" />
                        </div>
                      </div>
                      <div class="form-item mb-16">
                        <div class="title flex align-center mb-8">
                          <span style="margin-right: 4px">{{
                            $t('views.document.setRules.chunk_length.label')
                          }}</span>
                          <el-tooltip
                            effect="dark"
                            :content="$t('views.document.setRules.chunk_length.tooltip')"
                            placement="right"
                          >
                            <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                          </el-tooltip>
                        </div>
                        <el-slider
                          v-model="form.chunk_length"
                          show-input
                          :show-input-controls="false"
                          :min="100"
                          :max="256"
                        />
                      </div>
                    </div>
                    <div class="form-item mb-16">
                      <div class="title mb-8">
                        {{ $t('views.document.setRules.with_filter.label') }}
                      </div>
                      <el-switch size="small" v-model="form.with_filter" />
                      <div style="margin-top: 4px">
                        <el-text type="info">
                          {{ $t('views.document.setRules.with_filter.text') }}</el-text
                        >
                      </div>
                    </div>
                  </el-card>
                </el-card>
              </el-radio-group>
            </div>
          </el-scrollbar>
          <div>
            <el-checkbox
            v-model="checkedConnect"
              @change="changeHandle"
              style="white-space: normal"
            >
              {{ $t('views.document.setRules.checkedConnect.label') }}
            </el-checkbox>
          </div>
          <div class="text-right mt-8">
            <el-button @click="splitDocument">
              {{ $t('views.document.buttons.preview') }}</el-button
            >
          </div>
        </div>
      </el-col>

      <el-col :span="14" class="p-24 border-l">
        <div v-loading="loading">
          <h4 class="title-decoration-1 mb-8">{{ $t('views.document.setRules.title.preview') }}</h4>

          <ParagraphPreview v-model:data="paragraphList" :isConnect="checkedConnect" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import ParagraphPreview from '@/views/dataset/component/ParagraphPreview.vue'
import { cutFilename } from '@/utils/utils'
import documentApi from '@/api/document'
import useStore from '@/stores'
import type { KeyValue } from '@/api/type/common'
import { Star, StarFilled, Check } from '@element-plus/icons-vue'

const emit = defineEmits(['uploadSucess'])
const { dataset } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const splitPatternList = ref<Array<KeyValue<string, string> & { 
  recommendedLevel?: number;
  description?: string;
}>>([])

const radio = ref('1')
const loading = ref(false)
const paragraphList = ref<any[]>([])
const patternLoading = ref<boolean>(false)
const checkedConnect = ref<boolean>(false)

const firstChecked = ref(true)

const form = reactive<{
  patterns: Array<string>
  limit: number
  with_filter: boolean
  chunk_patterns: string
  chunk_length: number
  [propName: string]: any
}>({
  patterns: [],
  limit: 500,
  with_filter: true,
  chunk_patterns: '。| |\\\\.|！|;|；|!|\\n',
  chunk_length: 100
})

// 定义props
const props = defineProps<{
  uploadDocType: number
  datasetId: string
}>()

function changeHandle(val: boolean) {
  if (val && firstChecked.value) {
    paragraphList.value = paragraphList.value.map((item: any) => ({
      ...item,
      content: item.content.map((v: any) => ({
        ...v,
        problem_list: v.title.trim()
          ? [
              {
                content: v.title.trim()
              }
            ]
          : []
      }))
    }))
    firstChecked.value = false
  }
}
function splitDocument() {
  loading.value = true
  let fd = new FormData()
  documentsFiles.value.forEach((item) => {
    if (item?.raw) {
      fd.append('file', item?.raw)
    }
  })
  
  // 添加upload_type参数
  fd.append('uploadType', props.uploadDocType.toString())
  fd.append('datasetId', props.datasetId)
  
  if (radio.value === '2') {
    Object.keys(form).forEach((key) => {
      if (key == 'patterns') {
        form.patterns.forEach((item) => fd.append('patterns', item))
      } else {
        fd.append(key, form[key])
      }
    })
  }
  documentApi
    .postSplitDocument(fd)
    .then((res: any) => {
      if (props.uploadDocType == 0) {
        console.log('uploadSucess', res.data.dataset_id)
        emit('uploadSucess', res.data.dataset_id)
        loading.value = false
        return
      }
      const list = res.data

      list.map((item: any) => {
        if (item.name.length > 128) {
          item.name = cutFilename(item.name, 128)
        }
        if (checkedConnect.value) {
          item.content.map((v: any) => {
            v['problem_list'] = v.title.trim()
              ? [
                  {
                    content: v.title.trim()
                  }
                ]
              : []
          })
        }
      })

      paragraphList.value = list
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

const initSplitPatternList = () => {
  documentApi.listSplitPattern(patternLoading).then((ok) => {
    splitPatternList.value = ok.data
  })
}

watch(radio, () => {
  if (radio.value === '2') {
    initSplitPatternList()
  }
})

onMounted(() => {
  splitDocument()
})

defineExpose({
  paragraphList,
  checkedConnect,
  loading
})
</script>
<style scoped lang="scss">
.set-rules {
  width: 100%;

  .left-height {
    max-height: calc(var(--create-dataset-height) - 110px);
    overflow-x: hidden;
  }

  &__radio {
    width: 100%;
    display: block;

    .el-radio {
      white-space: break-spaces;
      width: 100%;
      height: 100%;
      line-height: 22px;
      color: var(--app-text-color);
    }

    :deep(.el-radio__label) {
      padding-left: 30px;
      width: 100%;
    }
    :deep(.el-radio__input) {
      position: absolute;
      top: 16px;
    }
    .active {
      border: 1px solid var(--el-color-primary);
    }
  }

  &__form {
    .title {
      font-size: 14px;
      font-weight: 400;
    }
  }
}

.split-pattern-option {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 0;
}

.option-key {
  flex: 0 0 35%;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 20px;
}

.option-content {
  flex: 0 0 65%;
  display: flex;
  align-items: center;
}

.recommendation-area {
  display: inline-flex;
  align-items: center;
  margin-right: 12px;
  min-width: 110px;
}

.recommended-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-right: 10px;
  
  &.level-0 {
    background-color: #909399;
    color: #fff;
  }
  
  &.level-1 {
    background-color: #67C23A;
    color: #fff;
  }
  
  &.level-2 {
    background-color: #409EFF;
    color: #fff;
  }
  
  &.level-3 {
    background-color: #E6A23C;
    color: #fff;
  }
  
  &.level-4 {
    background-color: #37a5ff;
    color: #fff;
  }
  
  &.level-5 {
    background-color: #03d403;
    color: #fff;
  }
}

.stars-container {
  display: inline-flex;
  align-items: center;
  flex-shrink: 0;
  
  .el-icon {
    font-size: 14px;
    color: var(--el-text-color-placeholder);
    margin-right: 2px;
    
    &.active {
      color: var(--el-color-warning);
    }

    .icon-star-filled {
      color: var(--el-color-warning);
    }

    .icon-star {
      color: var(--el-text-color-placeholder);
    }
  }
}

.option-description {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.align-center {
  align-items: center;
}

.mr-4 {
  margin-right: 4px;
}
</style>
