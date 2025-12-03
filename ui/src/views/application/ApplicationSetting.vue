<template>
  <LayoutContainer class="create-application">
    <template #header>
      <div class="flex-between w-full">
        <h3>
          {{ $t('common.setting') }}
        </h3>
        <el-button type="primary" @click="submit(applicationFormRef)" :disabled="loading">
          {{ $t('views.application.applicationForm.buttons.publish') }}
        </el-button>
      </div>
    </template>
    <el-row v-loading="loading">
      <el-col :span="10">
        <!-- <div class="title" style="padding-bottom: 0">
          <span>{{ $t('views.application.applicationForm.title.info') }}</span> -->
        <div class="p-24 mb-16" style="padding-bottom: 0">
          <h4 class="_title-decoration-1">
            {{ $t('views.applicationOverview.appInfo.header') }}
          </h4>
        </div>
        <div class="scrollbar-height-left">
          <el-scrollbar>
            <el-form hide-required-asterisk ref="applicationFormRef" :model="applicationForm" :rules="rules"
              label-width="150px" label-position="left" class="p-24" style="padding-top: 0">
              <el-form-item prop="name" required>
                <template #label>
                  <div class="flex-between">
                    <span>
                      <span class="danger">*</span>
                      {{ $t('views.application.applicationForm.form.appName.label') + ':' }}
                    </span>
                  </div>
                </template>
                <el-input v-model="applicationForm.name" maxlength="64"
                  :placeholder="$t('views.application.applicationForm.form.appName.placeholder')" show-word-limit
                  @blur="applicationForm.name = applicationForm.name?.trim()" />
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.appDescription.label') + ':'" class="required-dot">
                <el-input v-model="applicationForm.desc" type="textarea" :placeholder="$t('views.application.applicationForm.form.appDescription.placeholder')
                  " :rows="3" maxlength="256" show-word-limit />
              </el-form-item>

              <el-form-item :label="$t('views.application.applicationForm.form.aiModel.label') + ':'" class="inline-flex"
                required>
                <template #label>
                  <div class="flex-between" style="padding-left: 1em;">
                    <span>{{ $t('views.application.applicationForm.form.aiModel.label') + ":" }}</span>

                    <el-button type="primary" link @click="openAIParamSettingDialog"
                      :disabled="!applicationForm.model_id">
                      {{ $t('common.paramSetting') }}
                    </el-button>
                  </div>
                </template>
                <ModelSelect v-model="applicationForm.model_id"
                  :placeholder="$t('views.application.applicationForm.form.aiModel.placeholder')"
                  :options="modelOptions" @change="model_change" @submitModel="getModel" showFooter :model-type="'LLM'">
                </ModelSelect>
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.roleSettings.label') + ':'" class="required-dot">
                <MdEditorMagnify :title="$t('views.application.applicationForm.form.roleSettings.label')"
                  v-model="applicationForm.model_setting.system" style="height: 120px"
                  @submitDialog="submitSystemDialog" :placeholder="$t('views.application.applicationForm.form.roleSettings.placeholder')
                    " />
              </el-form-item>
              <el-form-item prop="model_setting.no_references_prompt" :rules="{
                required: applicationForm.model_id,
                message: $t('views.application.applicationForm.form.prompt.requiredMessage'),
                trigger: 'blur'
              }">
                <template #label>
                  <div class="flex align-center" style="padding-left: 1em;">
                    <span class="danger mr-4" v-if="applicationForm.model_id">*</span>
                    <span class="mr-4">{{
                      $t('views.application.applicationForm.form.prompt.label') + ":"
                    }}
                      <br />
                      {{ $t('views.application.applicationForm.form.prompt.noReferences') }}
                    </span>
                    <el-tooltip effect="dark" :content="$t('views.application.applicationForm.form.prompt.noReferencesTooltip', {
                      question: '{question}'
                    })
                      " placement="right" popper-class="max-w-350">
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>

                  </div>
                </template>

                <MdEditorMagnify :title="$t('views.application.applicationForm.form.prompt.label') +
                  $t('views.application.applicationForm.form.prompt.noReferences')
                  " v-model="applicationForm.model_setting.no_references_prompt" style="height: 120px"
                  @submitDialog="submitNoReferencesPromptDialog" placeholder="{question}" />
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.historyRecord.label') + ':'"
                @click.prevent class="required-dot">
                <el-input-number v-model="applicationForm.dialogue_number" :min="0" :value-on-clear="0"
                  controls-position="right" class="w-full" :step="1" :step-strictly="true" />
              </el-form-item>

              <el-form-item label="$t('views.application.applicationForm.form.relatedKnowledgeBase')+':'"
                class="inline-flex">
                <template #label>
                  <div class="flex-between" style="padding-left: 1em;">
                    <span>{{
                      $t('views.application.applicationForm.form.relatedKnowledge.label') + ":"
                    }}</span>
                    <!-- <div>
                      <el-button type="primary" link @click="openParamSettingDialog">
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                        {{ $t('common.paramSetting') }}
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4">
                          <Plus />
                        </el-icon>
                        {{ $t('common.add') }}
                      </el-button>
                    </div> -->
                  </div>
                </template>
                <div class="w-full flex flex-between">
                  <div class="kownledge-select">
                    <div>
                      <el-text type="info">{{ $t('views.application.applicationForm.form.relatedKnowledge.placeholder')
                      }}
                      </el-text>
                      <el-button type="primary" link @click="openParamSettingDialog">
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                        {{ $t('common.paramSetting') }}
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4">
                          <Plus />
                        </el-icon>
                        {{ $t('common.add') }}
                      </el-button>
                    </div>
                    <div>
                      <el-row :gutter="12">
                        <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="12" class="mb-8"
                          v-for="(item, index) in applicationForm.dataset_id_list" :key="index">
                          <el-card class="relate-dataset-card border-r-4" shadow="never">
                            <div class="flex-between">
                              <div class="flex align-center" style="width: 80%">
                                <AppAvatar v-if="relatedObject(datasetList, item, 'id')?.type === '1'"
                                  class="mr-8 avatar-purple" shape="square" :size="32">
                                  <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                                </AppAvatar>
                                <AppAvatar v-else-if="relatedObject(datasetList, item, 'id')?.type === '2'"
                                  class="mr-8 avatar-purple" shape="square" :size="32" style="background: none">
                                  <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                                </AppAvatar>
                                <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                                  <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                                </AppAvatar>

                                <span class="ellipsis cursor" :title="relatedObject(datasetList, item, 'id')?.name">
                                  {{ relatedObject(datasetList, item, 'id')?.name }}</span>
                              </div>
                              <el-button text @click="removeDataset(item)">
                                <el-icon>
                                  <Close />
                                </el-icon>
                              </el-button>
                            </div>
                          </el-card>
                        </el-col>
                      </el-row>
                    </div>
                  </div>
                </div>
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.prompt.label') + ':'"
                prop="model_setting.prompt" :rules="{
                  required: applicationForm.model_id,
                  message: $t('views.application.applicationForm.form.prompt.requiredMessage'),
                  trigger: 'blur'
                }">
                <template #label>
                  <div class="flex align-center" style="padding-left: 1em;">
                    <span class="danger mr-4" v-if="applicationForm.model_id">*</span>
                    <span class="mr-4">
                      {{ $t('views.application.applicationForm.form.prompt.label') + ':' }}<br />
                      {{ $t('views.application.applicationForm.form.prompt.references') }}
                    </span>
                    <el-tooltip effect="dark" :content="$t('views.application.applicationForm.form.prompt.referencesTooltip', {
                      data: '{data}',
                      question: '{question}'
                    })
                      " popper-class="max-w-350" placement="right">
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>

                  </div>
                </template>

                <MdEditorMagnify :title="$t('views.application.applicationForm.form.prompt.label') +
                  $t('views.application.applicationForm.form.prompt.references')
                  " v-model="applicationForm.model_setting.prompt" style="height: 150px"
                  @submitDialog="submitPromptDialog" :placeholder="defaultPrompt" />
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.prologue') + ':'" class="required-dot">
                <MdEditorMagnify :title="$t('views.application.applicationForm.form.prologue')"
                  v-model="applicationForm.prologue" style="height: 150px" @submitDialog="submitPrologueDialog" />
              </el-form-item>
              <el-form-item @click.prevent>
                <template #label>
                  <div class="flex-between">
                    <span class="mr-4">
                      {{ $t('views.application.applicationForm.form.reasoningContent.label') + ':' }}
                    </span>

                    <div class="flex">
                      <el-button type="primary" link @click="openReasoningParamSettingDialog">
                        <el-icon>
                          <Setting />
                        </el-icon>
                      </el-button>
                      <el-switch class="ml-8" active-text="是" inactive-text="否" inline-prompt
                        v-model="applicationForm.model_setting.reasoning_content_enable"
                        @change="sttModelEnableChange" />
                    </div>
                  </div>
                </template>
              </el-form-item>

              <el-form-item prop="stt_model_id" :rules="{
                required: applicationForm.stt_model_enable,
                message: $t('views.application.applicationForm.form.voiceInput.requiredMessage'),
                trigger: 'change'
              }">
                <template #label>
                  <div class="flex-between">
                    <span class="mr-4 ellipsis">
                      <span class="danger" v-if="applicationForm.stt_model_enable">*</span>
                      <span :class="{hide:applicationForm.stt_model_enable}">{{ $t('views.application.applicationForm.form.voiceInput.label') + ":" }}</span>
                    </span>

                    <div class="flex">
                      <el-checkbox v-if="applicationForm.stt_model_enable" v-model="applicationForm.stt_autosend">{{
                        $t('views.application.applicationForm.form.voiceInput.autoSend')
                      }}</el-checkbox>
                      <el-switch class="ml-8" v-model="applicationForm.stt_model_enable" active-text="是"
                        inactive-text="否" inline-prompt @change="sttModelEnableChange" />
                    </div>
                  </div>
                </template>
                <ModelSelect v-show="applicationForm.stt_model_enable" v-model="applicationForm.stt_model_id"
                  :placeholder="$t('views.application.applicationForm.form.voiceInput.placeholder')"
                  :options="sttModelOptions" :model-type="'STT'"></ModelSelect>
              </el-form-item>
              <el-form-item prop="tts_model_id" :rules="{
                required: applicationForm.tts_type === 'TTS' && applicationForm.tts_model_enable,
                message: $t('views.application.applicationForm.form.voicePlay.requiredMessage'),
                trigger: 'change'
              }">
                <template #label>
                  <div class="flex-between">
                    <span class="mr-4 ellipsis">
                      <span class="danger" v-if="
                        applicationForm.tts_type === 'TTS' && applicationForm.tts_model_enable
                      ">*</span>
                      <span :class="{hide:applicationForm.tts_model_enable}">{{ $t('views.application.applicationForm.form.voicePlay.label') + ":" }}</span>
                    </span>
                    <div class="flex">
                      <el-checkbox v-if="applicationForm.tts_model_enable" v-model="applicationForm.tts_autoplay">{{
                        $t('views.application.applicationForm.form.voicePlay.autoPlay')
                      }}</el-checkbox>
                      <el-switch class="ml-8" v-model="applicationForm.tts_model_enable" @change="ttsModelEnableChange"
                        active-text="是" inactive-text="否" inline-prompt />
                    </div>
                  </div>
                </template>
                <div class="w-full">
                  <el-radio-group v-model="applicationForm.tts_type" v-show="applicationForm.tts_model_enable"
                    class="mb-8">
                    <el-radio value="BROWSER">{{
                      $t('views.application.applicationForm.form.voicePlay.browser')
                    }}</el-radio>
                    <el-radio value="TTS">{{
                      $t('views.application.applicationForm.form.voicePlay.tts')
                    }}</el-radio>
                  </el-radio-group>
                </div>
                <div class="flex-between w-full">
                  <ModelSelect v-if="applicationForm.tts_type === 'TTS' && applicationForm.tts_model_enable"
                    v-model="applicationForm.tts_model_id" :placeholder="$t('views.application.applicationForm.form.voicePlay.placeholder')
                      " :options="ttsModelOptions" @change="ttsModelChange()" :model-type="'TTS'"></ModelSelect>

                  <el-button v-if="applicationForm.tts_type === 'TTS'" @click="openTTSParamSettingDialog"
                    :disabled="!applicationForm.tts_model_id" class="ml-8">
                    <el-icon>
                      <Operation />
                    </el-icon>
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </div>
      </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="_title-decoration-1 mb-16">
          {{ $t('views.application.applicationForm.title.appTest') }}
        </h4>
        <div class="dialog-bg">
          <div class="flex align-center p-16 mb-8">
            <div class="edit-avatar mr-12" @mouseenter="showEditIcon = true" @mouseleave="showEditIcon = false">
              <AppAvatar v-if="isAppIcon(applicationForm?.icon)" shape="square" :size="32" style="background: none">
                <img :src="applicationForm?.icon" alt="" />
              </AppAvatar>
              <AppAvatar v-else-if="applicationForm?.name" :name="applicationForm?.name" pinyinColor shape="square"
                :size="32" />
              <AppAvatar v-if="showEditIcon" shape="square" class="edit-mask" :size="32" @click="openEditAvatar">
                <el-icon>
                  <EditPen />
                </el-icon>
              </AppAvatar>
            </div>
            <h4>
              {{
                applicationForm?.name || $t('views.application.applicationForm.form.appName.label')
              }}
            </h4>
          </div>
          <div class="scrollbar-height">
            <AiChat :applicationDetails="applicationForm" :type="'debug-ai-chat'"></AiChat>
          </div>
        </div>
      </el-col>
    </el-row>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshForm" />
    <TTSModeParamSettingDialog ref="TTSModeParamSettingDialogRef" @refresh="refreshTTSForm" />
    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
    <AddDatasetDialog ref="AddDatasetDialogRef" @addData="addDataset" :data="datasetList" @refresh="refresh"
      :loading="datasetLoading" />

    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshIcon" />
    <ReasoningParamSettingDialog ref="ReasoningParamSettingDialogRef" @refresh="submitReasoningDialog" />
  </LayoutContainer>
</template>
<script setup lang="ts">

import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { groupBy } from 'lodash'
import AIModeParamSettingDialog from './component/AIModeParamSettingDialog.vue'
import ParamSettingDialog from './component/ParamSettingDialog.vue'
import AddDatasetDialog from './component/AddDatasetDialog.vue'
import EditAvatarDialog from '@/views/application-overview/component/EditAvatarDialog.vue'
import applicationApi from '@/api/application'
import { isAppIcon } from '@/utils/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import { relatedObject } from '@/utils/utils'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'
import TTSModeParamSettingDialog from './component/TTSModeParamSettingDialog.vue'
import http from '@/api/http-utils'
import ReasoningParamSettingDialog from './component/ReasoningParamSettingDialog.vue'

const { model, application } = useStore()

const route = useRoute()
const {
  params: { id }
} = route as any
// @ts-ignore
const defaultPrompt = t('views.application.applicationForm.form.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}'
})

const optimizationPrompt =
  t('views.application.applicationForm.dialog.defaultPrompt1', {
    question: '{question}'
  }) +
  '<data></data>' +
  t('views.application.applicationForm.dialog.defaultPrompt2')

const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const ReasoningParamSettingDialogRef = ref<InstanceType<typeof ReasoningParamSettingDialog>>()
const TTSModeParamSettingDialogRef = ref<InstanceType<typeof TTSModeParamSettingDialog>>()
const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()

const applicationFormRef = ref<FormInstance>()
const AddDatasetDialogRef = ref()
const EditAvatarDialogRef = ref()
const groupList = ref<any>([])
const loading = ref(false)
const datasetLoading = ref(false)
const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  dialogue_number: 1,
  prologue: t('views.application.applicationForm.form.defaultPrologue'),
  dataset_id_list: [],
  dataset_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}'
    }
  },
  model_setting: {
    prompt: defaultPrompt,
    system: t('views.application.applicationForm.form.roleSettings.placeholder'),
    no_references_prompt: '{question}',
    reasoning_content_enable: false
  },
  model_params_setting: {},
  problem_optimization: false,
  problem_optimization_prompt: optimizationPrompt,
  stt_model_id: '',
  tts_model_id: '',
  stt_model_enable: false,
  tts_model_enable: false,
  tts_type: 'BROWSER',
  type: 'SIMPLE'
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [
    {
      required: true,
      message: t('views.application.applicationForm.form.appName.placeholder'),
      trigger: 'blur'
    }
  ]
})
const modelOptions = ref<any>(null)
const datasetList = ref([])
const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const showEditIcon = ref(false)

function submitPrologueDialog(val: string) {
  applicationForm.value.prologue = val
}
function submitPromptDialog(val: string) {
  applicationForm.value.model_setting.prompt = val
}
function submitNoReferencesPromptDialog(val: string) {
  applicationForm.value.model_setting.no_references_prompt = val
}
function submitSystemDialog(val: string) {
  applicationForm.value.model_setting.system = val
}
function submitReasoningDialog(val: any) {
  applicationForm.value.model_setting = {
    ...applicationForm.value.model_setting,
    ...val
  }
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      application.asyncPutApplication(id, applicationForm.value, loading).then((res) => {
        MsgSuccess(t('common.saveSuccess'))
      })
    }
  })
}
const model_change = (model_id?: string) => {
  applicationForm.value.model_id = model_id
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshForm({})
  }
}
const openAIParamSettingDialog = () => {
  if (applicationForm.value.model_id) {
    AIModeParamSettingDialogRef.value?.open(
      applicationForm.value.model_id,
      id,
      applicationForm.value.model_params_setting
    )
  }
}

const openReasoningParamSettingDialog = () => {
  ReasoningParamSettingDialogRef.value?.open(applicationForm.value.model_setting)
}

const openTTSParamSettingDialog = () => {
  if (applicationForm.value.tts_model_id) {
    TTSModeParamSettingDialogRef.value?.open(
      applicationForm.value.tts_model_id,
      id,
      applicationForm.value.tts_model_params_setting
    )
  }
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(applicationForm.value)
}

function refreshParam(data: any) {
  applicationForm.value = { ...applicationForm.value, ...data }
}

function refreshForm(data: any) {
  applicationForm.value.model_params_setting = data
}

function refreshTTSForm(data: any) {
  applicationForm.value.tts_model_params_setting = data
}

function removeDataset(id: any) {
  if (applicationForm.value.dataset_id_list) {
    applicationForm.value.dataset_id_list.splice(
      applicationForm.value.dataset_id_list.indexOf(id),
      1
    )
  }
}

function addDataset(val: Array<string>) {
  applicationForm.value.dataset_id_list = val
}

function openDatasetDialog() {
  AddDatasetDialogRef.value.open(applicationForm.value.dataset_id_list)
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    applicationForm.value = res.data
    applicationForm.value.model_id = res.data.model
    applicationForm.value.stt_model_id = res.data.stt_model
    applicationForm.value.tts_model_id = res.data.tts_model
    applicationForm.value.tts_type = res.data.tts_type
    applicationForm.value.model_setting.no_references_prompt =
      res.data.model_setting.no_references_prompt || '{question}'
    application.asyncGetAccessToken(id, loading).then((res: any) => {
      applicationForm.value = { ...applicationForm.value, ...res.data }
    })
  })
}

function getDataset() {
  application.asyncGetApplicationDataset(id, datasetLoading).then((res: any) => {
    datasetList.value = res.data
  })
}

function getModel() {
  loading.value = true
  applicationApi
    .getApplicationModel(id)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getSTTModel() {
  loading.value = true
  applicationApi
    .getApplicationSTTModel(id)
    .then((res: any) => {
      sttModelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getTTSModel() {
  loading.value = true
  applicationApi
    .getApplicationTTSModel(id)
    .then((res: any) => {
      ttsModelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function ttsModelChange() {
  if (applicationForm.value.tts_model_id) {
    TTSModeParamSettingDialogRef.value?.reset_default(applicationForm.value.tts_model_id, id)
  } else {
    refreshTTSForm({})
  }
}

function ttsModelEnableChange() {
  if (!applicationForm.value.tts_model_enable) {
    applicationForm.value.tts_model_id = ''
    applicationForm.value.tts_type = 'BROWSER'
  }
}

function sttModelEnableChange() {
  if (!applicationForm.value.stt_model_enable) {
    applicationForm.value.stt_model_id = ''
  }
}

function openEditAvatar() {
  EditAvatarDialogRef.value.open(applicationForm.value)
}
function refreshIcon() {
  getDetail()
}

function refresh() {
  getDataset()
}

const getGroupList = () => {
}

onMounted(() => {
  getModel()
  getDataset()
  getDetail()
  getSTTModel()
  getTTSModel()
  getGroupList()
})
</script>
<style lang="scss" scoped>
.create-application {
  padding: var(--app-view-padding);
  height: 100%;
  box-sizing: border-box;

  :deep(.content-container__header) {
    padding: 0 var(--app-view-padding) !important;
  }

  :deep(.el-scrollbar__view) {
    height: 100%;

    .content-container__main {
      height: 100%;

      .title {
        height: 56px;
        line-height: 56px;
        position: relative;
        font-weight: 600;
        font-size: 16px;
        color: #223355;
        padding-left: 20px;
      }
    }
  }

  .relate-dataset-card {
    color: var(--app-text-color);
  }

  .dialog-bg {
    border-radius: 8px;
    background: var(--dialog-bg-gradient-color);
    overflow: hidden;
    box-sizing: border-box;
  }

  .scrollbar-height-left {
    height: calc(var(--app-main-height) - 64px);
  }

  .scrollbar-height {
    height: calc(var(--app-main-height) - 166px);
  }

  :deep(.cm-content) {
    color: #223355 !important;
  }

  :deep(.el-textarea) {
    .el-input__count {
      color: #A8B4C8 !important;
    }
  }
  :deep(.el-input-number) {
    .el-input__inner {
      text-align: left;
    }
  }
  :deep(.el-scrollbar__bar) {
    .el-scrollbar__thumb {
      background-color: #223355;
    }
  } 
}

.prologue-md-editor {
  height: 150px;
}

:deep(.el-form-item__label) {
  display: block;
}

:deep(.dialog-bg) {
  height: calc(100% - 90px) !important;

  .edit-avatar {
    height: 32px;

    .edit-mask {
      width: 32px;
      height: 32px;
    }
  }
}

:deep(.operate-textarea) {
  height: 130px !important;
  border: none !important;
}
.hide {
  display: none;
}
</style>
<style lang="scss">
.create-application {
  .content-container__header {
    height: 56px;
    line-height: 56px;
    position: relative;
    padding: 0 20px;
    border-bottom: 1px solid #E9ECF2;
    background-color: var(--app-view-bg-color);
    // display: none !important;
  }

  > .el-scrollbar {
    height: calc(100% - 56px) !important;

    > .el-scrollbar__wrap {
      overflow: hidden;
    }
  }

  .el-scrollbar {
    .el-scrollbar__view {
      .dialog-bg {
        border-radius: 0;
        background-color: var(--app-view-bg-color);

        > .flex {
          height: 56px;
          line-height: 56px;
          position: relative;
          padding-left: 20px;
          border-bottom: 1px solid #E9ECF2;
          border-top: 1px solid #E9ECF2;
        }

        .scrollbar-height {
          height: calc(var(--app-main-height) - 122px);
          box-sizing: border-box;
          padding-top: 20px;

          .ai-chat__operate {
            padding: 0;
            height: 195px;

            .operate-textarea {
              border-radius: 0;
              height: 100%;
              //border-top: 1px solid #E9ECF2;

              .el-scrollbar {
                height: 1px;
              }

              .flex {
                height: 100%;
              }
            }
          }
        }
      }

      .inline-flex {
        .el-form-item__content {
          display: flex;
          flex-wrap: nowrap;
        }
      }
    }
  }

}

.kownledge-select {
  flex-direction: column !important;
}
</style>