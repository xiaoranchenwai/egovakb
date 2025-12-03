<template>
  <div class="common-table-view">
    <LayoutContainer header="设置" class="dataset-setting-view">
      <template #header>
        <div class="flex-between w-full">
          <h3>
            {{ t('common.setting') }}
          </h3>
          <div>
            <el-button type="default" :disabled="loading">
              {{ t('common.cancel') }}
            </el-button>
            <el-button type="primary" :disabled="loading" @click="submit">
              {{ t('common.save') }}
            </el-button>
          </div>

        </div>
      </template>
      <div class="dataset-setting main-calc-height">
        <el-scrollbar>
          <div class="p-24" v-loading="loading">
            <h4 class="title mb-16">{{ t('views.dataset.datasetForm.title.info') }}</h4>
            <BaseForm ref="BaseFormRef" :data="detail" />

            <el-form ref="webFormRef" :rules="rules" :model="form" label-position="left"
              require-asterisk-position="left" label-width="7em">
              <el-form-item label="知识库类型:" required>
                <el-card shadow="never" class="mb-8" v-if="detail.type === '0'">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <div>通用型</div>
                      <el-text type="info">可以通过上传文件或手动录入方式构建知识库</el-text>
                    </div>
                  </div>
                </el-card>
                <el-card shadow="never" class="mb-8" v-if="detail?.type === '1'">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-purple" shape="square" :size="32">
                      <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <div>Web 站点</div>
                      <el-text type="info"> 通过网站链接同步方式构建知识库 </el-text>
                    </div>
                  </div>
                </el-card>
              </el-form-item>
              <el-form-item label="Web 根地址:" prop="source_url" v-if="detail.type === '1'">
                <el-input v-model="form.source_url" placeholder="请输入 Web 根地址"
                  @blur="form.source_url = form.source_url.trim()" />
              </el-form-item>
              <el-form-item label="选择器:" v-if="detail.type === '1'">
                <el-input v-model="form.selector" placeholder="默认为 body，可输入 .classname/#idname/tagname"
                  @blur="form.selector = form.selector.trim()" />
              </el-form-item>
            </el-form>
            <div v-if="application_id_list.length > 0">
              <h4 class="title mb-16">关联应用</h4>
              <el-row :gutter="12">
                <el-col :span="12" v-for="(item, index) in application_list.filter((obj: any) =>
                  application_id_list.some((v: any) => v === obj?.id)
                )" :key="index" class="mb-16">
                  <el-card shadow="never">
                    <div class="flex-between">
                      <div class="flex align-center">
                        <AppAvatar v-if="isAppIcon(item?.icon)" shape="square" :size="32" style="background: none"
                          class="mr-12">
                          <img :src="item?.icon" alt="" />
                        </AppAvatar>
                        <AppAvatar v-else-if="item?.name" :name="item?.name" pinyinColor shape="square" :size="32"
                          class="mr-12" />
                        {{ item.name }}
                      </div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>

          <div class="text-right" style="opacity: 0;pointer-events: none;">
            <el-button @click="submit" type="primary"> {{ $t('common.save') }}</el-button>
          </div>
          </div>
        </el-scrollbar>
      </div>
    </LayoutContainer>
  </div>

</template>
<script setup lang="ts">

import { ref, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import BaseForm from '@/views/dataset/component/BaseForm.vue'
import datasetApi from '@/api/dataset'
import type { ApplicationFormType } from '@/api/type/application'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { isAppIcon } from '@/utils/application'
import "@/layout/layout-template/index.scss";
import useStore from '@/stores'
import { t } from '@/locales'

const route = useRoute()
const {
  params: { id }
} = route as any

const { dataset } = useStore()
const webFormRef = ref()
const BaseFormRef = ref()
const loading = ref(false)
const detail = ref<any>({})
const application_list = ref<Array<ApplicationFormType>>([])
const application_id_list = ref([])
const cloneModelId = ref('')
const cloneQuestionModelId = ref('')

const form = ref<any>({
  source_url: '',
  selector: '',
  app_id: '',
  app_secret: '',
  folder_token: ''
})

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.source_url.requiredMessage'),
      trigger: 'blur'
    }
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur'
    }
  ]
})

async function submit() {
  if (await BaseFormRef.value?.validate()) {
    await webFormRef.value.validate((valid: any) => {
      if (valid) {
        const obj =
          detail.value.type === '1' || detail.value.type === '2'
            ? {
              application_id_list: application_id_list.value,
              meta: form.value,
              ...BaseFormRef.value.form
            }
            : {
              application_id_list: application_id_list.value,
              ...BaseFormRef.value.form
            }

        if (cloneModelId.value !== BaseFormRef.value.form.embedding_mode_id) {
          MsgConfirm(t('common.tip'), t('views.dataset.tip.updateModeMessage'), {
            confirmButtonText: t('views.dataset.setting.vectorization')
          })
            .then(() => {
              if (detail.value.type === '2') {
                datasetApi.putLarkDataset(id, obj, loading).then((res) => {
                  datasetApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              } else {
                datasetApi.putDataset(id, obj, loading).then((res) => {
                  datasetApi.putReEmbeddingDataset(id).then(() => {
                    MsgSuccess(t('common.saveSuccess'))
                  })
                })
              }
            })
            .catch(() => { })
        } else {
          if (detail.value.type === '2') {
            datasetApi.putLarkDataset(id, obj, loading).then((res) => {
              datasetApi.putReEmbeddingDataset(id).then(() => {
                MsgSuccess(t('common.saveSuccess'))
              })
            })
          } else {
            datasetApi.putDataset(id, obj, loading).then((res) => {
              MsgSuccess(t('common.saveSuccess'))
            })
          }
        }
      }
    })
  }
}

function getDetail() {
  dataset.asyncGetDatasetDetail(id, loading).then((res: any) => {
    detail.value = res.data
    cloneModelId.value = res.data?.embedding_mode_id
    cloneQuestionModelId.value = res.data?.question_model_id
    if (detail.value.type === '1' || detail.value.type === '2') {
      form.value = res.data.meta
    }
    application_id_list.value = res.data?.application_id_list
    datasetApi.listUsableApplication(id, loading).then((ok) => {
      application_list.value = ok.data
    })
  })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss" scoped>
.dataset-setting {
  width: 70%;
  margin: 0 auto;
}
</style>
<style lang="scss">
.dataset-setting-view {
  .el-scrollbar__wrap {
    overflow-y: hidden;
  }
  .el-scrollbar__bar {
    z-index: -1;
  }
}
</style>