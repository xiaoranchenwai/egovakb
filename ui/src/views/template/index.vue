<template>
  <LayoutContainer class="template-page">
    <div class="template-manage flex main-calc-height">
      <div class="template-manage__left p-20 border-r">
        <h4 style="height: 44px;line-height: 44px;padding-left: 8px;font-size: 16px;">模型厂家</h4>

        <div class="team-member-input mt-8 mb-16">
          <el-input placeholder="请输入模型名搜索" suffix-icon="Search" clearable />
        </div>

        <div class="model-list-height-left">
          <div class="all-mode flex cursor" @click="clickListHandle(allObj as Provider)"
            :class="!active_provider?.provider ? 'all-mode-active' : ''">
            <AppIcon class="mr-8" style="height: 20px; width: 20px" :iconName="'app-all-menu-active'"></AppIcon>
            <span>{{ $t('views.template.model.allModel') }}</span>

          </div>

          <el-scrollbar>
            <el-collapse class="template-collapse">
              <el-collapse-item :title="$t('views.template.model.publicModel')" name="1">
                <template #title>
                  <img src="@/assets/icon_file-folder_colorful.svg" class="mr-8" />
                  {{ $t('views.template.model.publicModel') }}
                </template>
                <common-list :data="online_provider_list" v-loading="loading" @click="clickListHandle"
                  value-key="provider" default-active="" ref="commonList1">
                  <template #default="{ row }">
                    <div class="flex align-center">
                      <span
                        :innerHTML="row.icon"
                        alt=""
                        style="height: 20px; width: 20px"
                        class="mr-8"
                      />
                      <span>{{ row.name }}</span>
                    </div>
                  </template>
                </common-list>
              </el-collapse-item>
              <el-collapse-item :title="$t('views.template.model.privateModel')" name="2">
                <template #title>
                  <img src="@/assets/icon_file-folder_colorful.svg" class="mr-8" />
                  {{ $t('views.template.model.privateModel') }}
                </template>
                <common-list :data="local_provider_list" v-loading="loading" @click="clickListHandle"
                  value-key="provider" default-active="" ref="commonList2">
                  <template #default="{ row }">
                    <div class="flex align-center">
                      <span
                        :innerHTML="row.icon"
                        alt=""
                        style="height: 20px; width: 20px"
                        class="mr-8"
                      />
                      <span>{{ row.name }}</span>
                    </div>
                  </template>
                </common-list>
              </el-collapse-item>
            </el-collapse>
          </el-scrollbar>
        </div>
      </div>
      <div class="template-manage__right w-full" v-loading="list_model_loading">
        <div class="pb-0 toolboxs">
          <h4>{{ active_provider?.name }}</h4>

          <div class="flex-between toolbar">
            <el-button @click="openCreateModel(active_provider)" round>
              <el-icon><Plus /></el-icon> 添加模型
            </el-button>

            <div class="flex-between" v-if="false">
              <el-select v-model="search_type" style="width: 120px" @change="search_type_change">
                <el-option label="创建者" value="create_user" />
                <el-option label="权限" value="permission_type" />
                <el-option label="模型类型" value="model_type" />
                <el-option label="模型名称" value="name" />
              </el-select>
              <el-input v-if="search_type === 'name'" v-model="model_search_form.name" @change="list_model"
                placeholder="按名称搜索" suffix-icon="Search" style="width: 220px" clearable />
              <el-select v-else-if="search_type === 'create_user'" v-model="model_search_form.create_user"
                @change="list_model" clearable style="width: 220px">
                <el-option v-for="u in user_options" :key="u.id" :value="u.id" :label="u.username" />
              </el-select>
              <el-select v-else-if="search_type === 'permission_type'" v-model="model_search_form.permission_type"
                clearable @change="list_model" style="width: 220px">
                <el-option label="公有" value="PUBLIC" />
                <el-option label="私有" value="PRIVATE" />
              </el-select>
              <el-select v-else-if="search_type === 'model_type'" v-model="model_search_form.model_type" clearable
                @change="list_model" style="width: 220px">
                <el-option label="大语言模型" value="LLM" />
                <el-option label="向量模型" value="EMBEDDING" />
                <el-option label="重排模型" value="RERANKER" />
                <el-option label="语音识别" value="STT" />
                <el-option label="语音合成" value="TTS" />
                <el-option label="图片理解" value="IMAGE" />
              </el-select>
            </div>

            <el-input v-if="search_type === 'name'" v-model="model_search_form.name" @change="list_model"
                placeholder="按名称搜索" suffix-icon="Search" style="width: 220px" clearable />
          </div>
        </div>
        <div class="model-list-height">
          <el-scrollbar>
            <div class="p-20 pt-0">
              <el-row v-if="model_split_list.length > 0" :gutter="15">
                <template v-for="(row, index) in model_split_list" :key="index">
                  <el-col :xs="24" :sm="24" :md="24" :lg="12" :xl="8" class="mb-16" v-for="(model, i) in row" :key="i">
                    <ModelCard @change="list_model" :updateModelById="updateModelById" :model="model"
                      :provider_list="provider_list">
                    </ModelCard>
                  </el-col>
                </template>
              </el-row>
              <el-empty :image="emptyImg" :description="$t('common.noData')" v-else />
            </div>
          </el-scrollbar>
        </div>
      </div>
    </div>
    <CreateModelDialog
      ref="createModelRef"
      @submit="list_model"
      @change="openCreateModel($event)"
    ></CreateModelDialog>

    <SelectProviderDialog
      ref="selectProviderRef"
      @change="(provider, modelType) => openCreateModel(provider, modelType)"
    ></SelectProviderDialog>
  </LayoutContainer>
</template>

<script lang="ts" setup>

import { onMounted, ref, computed } from 'vue'
import ModelApi from '@/api/model'
import type { Provider, Model } from '@/api/type/model'
import AppIcon from '@/components/icons/AppIcon.vue'
import ModelCard from '@/views/template/component/ModelCard.vue'
import { splitArray } from '@/utils/common'
import { modelTypeList } from '@/views/template/component/data'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'
import { t } from '@/locales'
import emptyImg from '@/assets/hit-test-empty.png'

const allObj = {
  icon: '',
  provider: '',
  name: t('views.template.model.allModel')
}

const commonList1 = ref()
const commonList2 = ref()
const loading = ref<boolean>(false)

const active_provider = ref<Provider>()
const search_type = ref('name')
const model_search_form = ref<{
  name: string
  create_user: string
  permission_type: string
  model_type: string
}>({
  name: '',
  create_user: '',
  permission_type: '',
  model_type: ''
})
const user_options = ref<any[]>([])
const list_model_loading = ref<boolean>(false)
const provider_list = ref<Array<Provider>>([])
const online_provider_list = ref<Array<Provider>>([])
const local_provider_list = ref<Array<Provider>>([])

const model_list = ref<Array<Model>>([])

const updateModelById = (model_id: string, model: Model) => {
  model_list.value
    .filter((m) => m.id == model_id)
    .forEach((m) => {
      m.status = model.status
    })
}
const model_split_list = computed(() => {
  return splitArray(model_list.value, 2)
})
const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()

const clickListHandle = (item: Provider) => {
  active_provider.value = item
  list_model()
  if (active_provider.value.provider === '') {
    commonList1.value.clearCurrent()
    commonList2.value.clearCurrent()
  }
}

const openCreateModel = (provider?: Provider, model_type?: string) => {
  console.log(provider)
  console.log(model_type)
  if (provider && provider.provider) {
    createModelRef.value?.open(provider, model_type)
  } else {
    selectProviderRef.value?.open()
  }
}

const list_model = () => {
  const params = active_provider.value?.provider ? { provider: active_provider.value.provider } : {}
  ModelApi.getModel({ ...model_search_form.value, ...params }, list_model_loading).then((ok) => {
    model_list.value = ok.data
    const v = model_list.value.map((m) => ({ id: m.user_id, username: m.username }))
    if (user_options.value.length === 0) {
      user_options.value = Array.from(new Map(v.map((item) => [item.id, item])).values())
    }
  })
}

const search_type_change = () => {
  model_search_form.value = { name: '', create_user: '', permission_type: '', model_type: '' }
}

onMounted(() => {
  ModelApi.getProvider(loading).then((ok) => {
    active_provider.value = allObj
    provider_list.value = [allObj, ...ok.data]

    const local_provider = [
      'model_ollama_provider',
      'model_local_provider',
      'model_xinference_provider',
      'model_vllm_provider'
    ]
    ok.data.forEach((item) => {
      if (local_provider.indexOf(item.provider) > -1) {
        local_provider_list.value.push(item)
      } else {
        online_provider_list.value.push(item)
      }
    })
    online_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
    local_provider_list.value.sort((a, b) => a.provider.localeCompare(b.provider))
    list_model()
  })
})
</script>

<style lang="scss" scoped>
.template-manage {
  &__left {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }

  .model-list-height {
    height: calc(var(--create-dataset-height) - 30px);
  }

  .model-list-height-left {
    height: calc(var(--create-dataset-height) - 40px);
  }

  .all-mode {
    padding: 10px 16px;
  }

  .all-mode-active {
    background: var(--el-color-primary-light-9);
    border-radius: 4px;
    color: var(--el-color-primary);
    font-weight: 500;
  }

  .template-collapse {
    border-top: none !important;
    border-bottom: none !important;

    :deep(.el-collapse-item__header) {
      border-bottom: none !important;
      padding-left: 16px;
      font-size: 14px;
      height: 40px;
      &:hover {
        background: var(--app-text-color-light-1);
        border-radius: 4px;
      }
    }

    :deep(.el-collapse-item) {
      margin-top: 2px;
    }

    :deep(.common-list) {
      li {
        padding-left: 30px !important;
        &:hover {
          background-color: #F5F7FA;
        }
      }
    }

    :deep(.el-collapse-item__wrap) {
      border-bottom: none !important;
    }
    :deep(.el-collapse-item__content) {
      padding-bottom: 0 !important;
    }
  }
}
</style>
<style lang="scss">
.template-page {
  padding: var(--app-view-padding) !important;
  height: 100%;
  box-sizing: border-box;

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
    height: calc(100%);
    background-color: #ffffff;

    .el-scrollbar__wrap {
      overflow: auto
    }

    > .el-scrollbar__wrap {
      overflow: hidden;

      .el-scrollbar__view {
        height: 100%;
        overflow: hidden;
        .content-container__main,.main-calc-height {
          height: 100%;
        }
      }
    }

    .el-input {
      .el-input__wrapper {
        border-radius: 16px;
      }
    }

    .team-manage__tabs {
      margin-top: 0 !important;
    }
  }

  .toolboxs {
    > h4 {
      height: 60px;
      line-height: 60px;
      border-bottom: 1px solid #E9ECF2;
      padding-left: 20px;
      font-weight: 600;
      font-size: 18px;
      color: #081126;
    }

    .toolbar {
      height: 56px;
      line-height: 56px;
      padding: 0 20px;
    }
  }

  .model-list-height {
    .el-scrollbar__view {
      overflow-y: auto !important;
    }
  }
}
</style>
<style lang="scss">
.template-page {
  .el-collapse-item__arrow {
    color: #A8B4C8 !important;
  }
  .template-collapse .el-collapse-item__header:hover {
    background-color: #F5F7FA !important;
  }
}
</style>