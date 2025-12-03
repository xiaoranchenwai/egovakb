<template>
  <LayoutContainer :header="$t('views.document.uploadDocument')" class="create-dataset">
    <template #backButton>
      <back-button @click="back"></back-button>
    </template>
    <div class="create-dataset__main flex" v-loading="loading">
      <div class="create-dataset__component main-calc-height">
        <el-scrollbar>
          <template v-if="active === 0">
            <div class="upload-document p-24">
              <!-- 上传文档 -->
              <UploadComponent ref="UploadComponentRef" />
              <div v-if="uploadProgress > 0 && isUploading" class="upload-progress">
                <el-progress :percentage="uploadProgress" :format="progressFormat" />
              </div>
            </div>
          </template>
          <template v-else-if="active === 1">
            <SetRules ref="SetRulesRef" :upload-doc-type="uploadDocType" :dataset-id="datasetId" @uploadSucess="uploadSucess" />
          </template>
          <template v-else-if="active === 2">
            <ResultSuccess :data="successInfo" />
          </template>
        </el-scrollbar>
      </div>
    </div>
    <div class="create-dataset__footer text-right border-t align-center flex-end" v-if="active !== 2">
      <el-text type="primary" size="large" style="margin-right: 10px;">
        上传模式
        <el-tooltip :content="$t('views.document.uploadType.tooltip')" placement="top">
          <el-icon >
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </el-text>
      <el-select
        v-model="uploadDocType"
        placeholder="请选择分段模式"
        size="default"
        style="width: 140px; margin-right: 10px;"
      >
        <el-option
          v-for="item in documentUploadType"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-divider direction="vertical" />
      <el-text type="primary" size="large" style="margin-right: 10px;">
        {{ $t('views.document.setRules.limit.label') }}
        <el-tooltip :content="$t('views.document.uploadType.splitLimit')" placement="top">
          <el-icon >
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </el-text>
      <el-slider
        v-model="splitLimit"
        show-input
        :show-input-controls="false"
        :min="50"
        :max="100000"
        class="split-slider "
      />
      <el-divider direction="vertical" />
      <el-text type="primary" size="large" style="margin-right: 10px;">
        覆盖同名文件
        <el-tooltip :content="$t('views.document.uploadType.cover')" placement="top">
          <el-icon >
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </el-text>
      <el-switch
        v-model="cover"
        inline-prompt
        active-text="覆盖"
        inactive-text="不覆盖"
        >
      </el-switch>
      <el-divider direction="vertical" />
      <el-text type="primary" size="large" style="margin-right: 10px;">
        自动生成检索问题
        <el-tooltip :content="$t('views.document.uploadType.generateRelated')" placement="top">
          <el-icon >
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </el-text>
      <el-switch
        v-model="generateRelated"
        inline-prompt
        active-text="生成"
        inactive-text="不生成"
        >
      </el-switch>
      <el-divider direction="vertical" />
      <el-text v-if="generateRelated" type="primary" size="large" style="margin-right: 10px;">
        每个分段自动生成问题数量
        <el-tooltip :content="$t('views.document.uploadType.generateRelatedCount')" placement="top">
          <el-icon >
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </el-text>
      <el-input-number v-if="generateRelated" v-model="generateRelatedCount" :min="1" :max="6" style="width: 90px; margin-right: 10px;" />
      <el-divider v-if="generateRelated" direction="vertical" />
      <el-button @click="router.go(-1)" :disabled="SetRulesRef?.loading || loading">{{
        $t('common.cancel')
      }}</el-button>
      <el-button @click="prev" v-if="active === 1" :disabled="SetRulesRef?.loading || loading">{{
        $t('views.document.buttons.prev')
      }}</el-button>
      <el-button
        @click="next"
        type="primary"
        v-if="active === 0"
        :disabled="SetRulesRef?.loading || isUploading"
        :loading="isUploading"
      >
        {{
          uploadDocType === 0
            ? $t('views.document.buttons.import')
            : (documentsType === 'txt'
                ? $t('views.document.buttons.next')
                : $t('views.document.buttons.import'))
        }}
      </el-button>
      <el-button
        @click="submit"
        type="primary"
        v-if="active === 1"
        :disabled="SetRulesRef?.loading || loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SetRules from './component/SetRules.vue'
import ResultSuccess from './component/ResultSuccess.vue'
import UploadComponent from './component/UploadComponent.vue'
import documentApi from '@/api/document'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'
import { DocumentUploadEnum } from '@/enums/document'
import { documentUploadType } from '@/utils/document'
const { dataset, document } = useStore()
const documentsFiles = computed(() => dataset.documentsFiles)
const documentsType = computed(() => dataset.documentsType)

const router = useRouter()
const route = useRoute()
const {
  query: { id } // id为datasetID，有id的是上传文档
} = route

const SetRulesRef = ref()
const UploadComponentRef = ref()
const uploadDocType = ref(0)
const generateRelated = ref(false)
const generateRelatedCount = ref(0)
const splitLimit = ref(10000)
const loading = ref(false)
const isUploading = ref(false)
const disabled = ref(false)
const cover = ref(false)
const active = ref(0)
const datasetId = id as string
const successInfo = ref<any>(null)
const uploadProgress = ref(0)

function progressFormat(percentage: number) {
  return percentage === 100 ? '处理中...' : `上传中：${percentage}%`
}

async function next() {
  isUploading.value = true
  disabled.value = true
  uploadProgress.value = 0
  if (await UploadComponentRef.value.validate()) {
    if (documentsType.value === 'QA') {
      let fd = new FormData()
      documentsFiles.value.forEach((item: any) => {
        if (item?.raw) {
          fd.append('file', item?.raw)
        }
      })
      fd.append('uploadType', uploadDocType.value.toString())
      if (id) {
        // QA文档上传
        documentApi.postQADocument(id as string, fd, loading, (percentage) => {
          uploadProgress.value = percentage
        }).then((res) => {
          uploadProgress.value = 100
          MsgSuccess(t('common.submitSuccess'))
          clearStore()
          isUploading.value = false
          router.push({ path: `/dataset/${id}/document` })
        }).catch(() => {
          uploadProgress.value = 0
          isUploading.value = false
        })
      }
    } else if (documentsType.value === 'table') {
      let fd = new FormData()
      fd.append('uploadType', uploadDocType.value.toString())
      fd.append('datasetId', id as string)
      fd.append('generateRelated', generateRelated.value.toString())
      fd.append('generateRelatedCount', generateRelatedCount.value.toString())
      fd.append('cover', cover.value.toString())
      if (splitLimit.value > 0)
      {
        fd.append('limit', splitLimit.value.toString())
      }
      documentsFiles.value.forEach((item: any) => {
        if (item?.raw) {
          fd.append('file', item?.raw)
        }
      })
      if (id) {
        // table文档上传
        documentApi.postTableDocument(id as string, fd, loading, (percentage) => {
          uploadProgress.value = percentage
        }).then((res) => {
          uploadProgress.value = 100
          MsgSuccess(t('common.submitSuccess'))
          clearStore()
          router.push({ path: `/dataset/${id}/document` })
        }).catch(() => {
          uploadProgress.value = 0
          isUploading.value = false
        })
      }
    } else {
      if (uploadDocType.value === 0) {
        let fd = new FormData()
        documentsFiles.value.forEach((item: any) => {
          if (item?.raw) {
            fd.append('file', item?.raw)
          }
        })
        fd.append('uploadType', uploadDocType.value.toString())
        fd.append('datasetId', id as string)
        fd.append('generateRelated', generateRelated.value.toString())
        fd.append('generateRelatedCount', generateRelatedCount.value.toString())
        fd.append('cover', cover.value.toString())
        if (splitLimit.value > 0)
        {
          fd.append('limit', splitLimit.value.toString())
        }
        documentApi
        .postSplitDocument(fd, (percentage) => {
          uploadProgress.value = percentage
        })
        .then((res: any) => {
          uploadProgress.value = 100
          uploadSucess(id as string)
        }).catch(() => {
          isUploading.value = false
          uploadProgress.value = 0
        })
      } else {
        if (active.value++ > 2) active.value = 0

      }
    }
  } else {
    disabled.value = false
    isUploading.value = false
  }
}

function uploadSucess(datasetId: string) {
  MsgSuccess(t('common.submitSuccess'))
  clearStore()
  router.push({ path: `/dataset/${id}/document` })
}

const prev = () => {
  active.value = 0
}

function clearStore() {
  dataset.saveDocumentsFile([])
  dataset.saveDocumentsType('')
}
function submit() {
  loading.value = true
  const documents = [] as any
  SetRulesRef.value?.paragraphList.map((item: any) => {
    if (!SetRulesRef.value?.checkedConnect) {
      item.content.map((v: any) => {
        delete v['problem_list']
      })
    }
    documents.push({
      name: item.name,
      paragraphs: item.content,
      document_url: item.document_url
    })
  })

  if (id) {
    // 上传文档
    document
      .asyncPostDocument(id as string, documents)
      .then(() => {
        MsgSuccess(t('common.submitSuccess'))
        clearStore()
        router.push({ path: `/dataset/${id}/document` })
      })
      .catch(() => {
        loading.value = false
      })
  }
}
function back() {
  if (documentsFiles.value?.length > 0) {
    MsgConfirm(t('common.tip'), t('views.document.tip.saveMessage'), {
      confirmButtonText: t('common.confirm'),
      type: 'warning'
    })
      .then(() => {
        router.go(-1)
        clearStore()
      })
      .catch(() => {})
  } else {
    router.go(-1)
  }
}
onUnmounted(() => {
  clearStore()
})
</script>
<style lang="scss" scoped>
.create-dataset {
  &__steps {
    min-width: 450px;
    max-width: 800px;
    width: 80%;
    margin: 0 auto;
    padding-right: 60px;

    :deep(.el-step__line) {
      left: 64% !important;
      right: -33% !important;
    }
  }

  &__component {
    width: 100%;
    margin: 0 auto;
    overflow: hidden;
  }
  &__footer {
    padding: 16px 24px;
    position: fixed;
    bottom: 0;
    left: 0;
    background: #ffffff;
    width: 100%;
    box-sizing: border-box;
  }
  .upload-document {
    width: 70%;
    margin: 0 auto;
    margin-bottom: 20px;
  }
  .split-slider {
    max-width: 200px;
  }
  .upload-progress {
    margin-top: 20px;
    width: 100%;
  }
}
</style>
