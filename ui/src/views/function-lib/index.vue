<template>
  <div class="function-lib-list-container">
    <div class="fl-list-container">
      <el-tabs v-model="functionType" @tab-change="tabChangeHandle">
        <el-tab-pane :label="$t('views.functionLib.title')" name="PUBLIC"></el-tab-pane>
        <el-tab-pane :label="$t('views.functionLib.internalTitle')" name="INTERNAL"></el-tab-pane>
      </el-tabs>
      <div class="flex-between condition">
        <div class="flex-between">
          <el-button round @click.stop='openCreateDialog()' v-if="functionType === 'PUBLIC'">
            <el-icon>
              <Plus />
            </el-icon>
            {{ $t('views.functionLib.createFunction') }}
          </el-button>
          <el-divider direction="vertical" v-if="functionType === 'PUBLIC'" />
          <el-upload ref="elUploadRef" :file-list="[]" action="#" multiple :auto-upload="false" :show-file-list="false"
            :limit="1" :on-change="(file: any, fileList: any) => importFunctionLib(file)" class="card-add-button"
            v-if="functionType === 'PUBLIC'">
            <div class="flex align-center cursor p-8">
              <AppIcon iconName="app-import" class="mr-8"></AppIcon>
              {{ $t('views.functionLib.importFunction') }}
            </div>
          </el-upload>
        </div>
        <div class="flex-between">
          <el-select
            v-if="functionType === 'PUBLIC'"
            v-model="selectUserId"
            class="mr-12"
            style="max-width: 240px; width: 150px"
            @change="searchHandle"
          >
            <el-option
              v-for="item in userOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input
            v-model="searchValue"
            @change="searchHandle"
            :placeholder="$t('views.functionLib.searchBar.placeholder')"
            suffix-icon="Search"
            class="w-240"
            style="max-width: 240px"
            clearable
          />
        </div>
      </div>

      <div class="content" 
        v-loading.fullscreen.lock="
          (paginationConfig.current_page === 1 && loading) || changeStateloading
        "
      >
        <InfiniteScroll
          :size="functionLibList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row :gutter="15">
            <el-col
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="6"
              v-for="(item, index) in functionLibList"
              :key="index"
              class="mb-16"
            >
            <CardBox
              v-if="functionType === 'PUBLIC'"
              :title="item.name"
              :description="item.desc"
              class="function-lib-card"
              @click="openCreateDialog(item)"
              :class="item.permission_type === 'PUBLIC' && !canEdit(item) ? '' : 'cursor'"
            >
              <template #icon>
                <AppAvatar
                  v-if="isAppIcon(item?.icon)"
                  shape="square"
                  :size="32"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="item?.icon" alt="" />
                </AppAvatar>
                <AppAvatar
                  v-else-if="item?.name"
                  :name="item?.name"
                  pinyinColor
                  shape="square"
                  :size="32"
                  class="mr-8"
                />
              </template>
              <div class="status-tag">
                <el-tag
                  class="green-tag"
                  v-if="item.permission_type === 'PUBLIC'"
                  style="height: 22px"
                >
                  {{ $t('common.public') }}</el-tag
                >
                <el-tag
                  class="orange-tag"
                  v-else-if="item.permission_type === 'PRIVATE'"
                  style="height: 22px"
                >
                  {{ $t('common.private') }}</el-tag
                >
              </div>
              <template #description>
                <el-text line-clamp="3">
                  {{ item.desc}}
                </el-text>
              </template>
              <div class='info flex-between'>
                <div class="flex align-center">
                  <el-avatar v-if="item.user_avatar" :src="item.user_avatar" :size='20'>
                  </el-avatar>
                  <el-avatar v-else src='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
                    :size='20' />
                  <el-text class="w-150px mb-2 username" truncated>
                    {{ item.username }}
                  </el-text>
                </div>
                <el-text class="w-150px mb-2 time time-right" truncated>
                  {{ datetimeFormat(item.create_time) }}
                </el-text>
              </div>
              <template #footer>
                <div>
                  <div @click.stop>
                    <el-switch
                      :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                      v-model="item.is_active"
                      @change="changeState($event, item)"
                      active-text="开" inactive-text="关" inline-prompt
                      class="mr-4"
                    />
                    <el-divider direction="vertical" />
                    <el-dropdown trigger="click">
                      <el-button text @click.stop>
                        <el-icon><MoreFilled color="#A8B4C8"/></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item
                            v-if="item.template_id"
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            @click.stop="addInternalFunction(item, true)"
                          >
                            <el-icon><EditPen /></el-icon>
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="!item.template_id"
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            @click.stop="openCreateDialog(item)"
                          >
                            <el-icon><EditPen /></el-icon>
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            v-if="!item.template_id"
                            @click.stop="copyFunctionLib(item)"
                          >
                            <AppIcon iconName="app-copy"></AppIcon>
                            {{ $t('common.copy') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            v-if="item.init_field_list?.length > 0"
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            @click.stop="configInitParams(item)"
                          >
                            <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                            {{ $t('common.param.initParam') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            @click.stop="configPermission(item)"
                          >
                            <el-icon><User /></el-icon>
                            {{ $t('views.functionLib.functionForm.form.permission_type.label') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            v-if="!item.template_id"
                            @click.stop="exportFunctionLib(item)"
                          >
                            <AppIcon iconName="app-export"></AppIcon>
                            {{ $t('common.export') }}
                          </el-dropdown-item>
                          <el-dropdown-item
                            :disabled="item.permission_type === 'PUBLIC' && !canEdit(item)"
                            @click.stop="deleteFunctionLib(item)"
                          >
                            <el-icon><Delete /></el-icon>
                            {{ $t('common.delete') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </CardBox>
            <CardBox
              v-if="functionType === 'INTERNAL'"
              :title="item.name"
              :description="item.desc"
              class="function-lib-card"
              @click="openDescDrawer(item)"
              :class="item.permission_type === 'PUBLIC' && !canEdit(item) ? '' : 'cursor'"
            >
              <template #icon>
                <AppAvatar
                  v-if="isAppIcon(item?.icon)"
                  shape="square"
                  :size="32"
                  style="background: none"
                  class="mr-8"
                >
                  <img :src="item?.icon" alt="" />
                </AppAvatar>
                <AppAvatar
                  v-else-if="item?.name"
                  :name="item?.name"
                  pinyinColor
                  shape="square"
                  :size="32"
                  class="mr-8"
                />
              </template>
              <template #footer>
                <div class="footer-content flex-between">
                  <div>{{ $t('common.author') }}: 管理员</div>
                  <div @click.stop>
                    <el-button type="primary" link @click="addInternalFunction(item)">
                      {{ $t('common.add') }}
                    </el-button>
                  </div>
                </div>
              </template>
            </CardBox>
            </el-col>
          </el-row>
        </InfiniteScroll>
      </div>
    </div>

    <FunctionFormDrawer ref="FunctionFormDrawerRef" @refresh="refresh" :title="title" />
    <PermissionDialog ref="PermissionDialogRef" @refresh="refresh" />
    <AddInternalFunctionDialog
      ref="AddInternalFunctionDialogRef"
      @refresh="confirmAddInternalFunction"
    />
    <InitParamDrawer ref="InitParamDrawerRef" @refresh="refresh" />
    <InternalDescDrawer ref="InternalDescDrawerRef" @addFunction="addInternalFunction" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch, nextTick } from 'vue'
import { cloneDeep, get } from 'lodash'
import functionLibApi from '@/api/function-lib'
import FunctionFormDrawer from './component/FunctionFormDrawer.vue'
import { MsgSuccess, MsgConfirm, MsgError } from '@/utils/message'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import { t } from '@/locales'
import PermissionDialog from '@/views/function-lib/component/PermissionDialog.vue'
import InitParamDrawer from '@/views/function-lib/component/InitParamDrawer.vue'
import InternalDescDrawer from '@/views/function-lib/component/InternalDescDrawer.vue'
import { isAppIcon } from '@/utils/application'
import InfiniteScroll from '@/components/infinite-scroll/index.vue'
import CardBox from '@/components/card-box/index.vue'
import AddInternalFunctionDialog from '@/views/function-lib/component/AddInternalFunctionDialog.vue'
import { datetimeFormat } from '@/utils/time'

const { user } = useStore()

const loading = ref(false)

const InternalDescDrawerRef = ref()
const FunctionFormDrawerRef = ref()
const PermissionDialogRef = ref()
const AddInternalFunctionDialogRef = ref()
const InitParamDrawerRef = ref()

const functionLibList = ref<any[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

const searchValue = ref('')
const title = ref('')
const changeStateloading = ref(false);

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')
const elUploadRef = ref<any>()

const functionType = ref('PUBLIC')

watch(
  functionType,
  (val) => {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    functionLibList.value = []
    getList()
  },
  { immediate: true }
)

function tabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
}

const canEdit = (row: any) => {
  if (user.userInfo?.role === 'ADMIN') {
    return true
  }
  return user.userInfo?.id === row?.user_id
}

function openCreateDialog(data?: any) {
  // 有template_id的不允许编辑，是模板转换来的
  if (data?.template_id) {
    return
  }
  // console.log(data)
  title.value = data ? t('views.functionLib.editFunction') : t('views.functionLib.createFunction')
  if (data) {
    if (data?.permission_type !== 'PUBLIC' || canEdit(data)) {
      functionLibApi.getFunctionLibById(data?.id, changeStateloading).then((res) => {
        FunctionFormDrawerRef.value.open(res.data)
      })
    }
  } else {
    FunctionFormDrawerRef.value.open(data)
  }
}

async function openDescDrawer(row: any) {
  const index = row.icon.replace('icon.png', 'detail.md')
  const response = await fetch(index)
  const content = await response.text()
  InternalDescDrawerRef.value.open(content, row)
}

function addInternalFunction(data?: any, isEdit?: boolean) {
  AddInternalFunctionDialogRef.value.open(data, isEdit)
}

function confirmAddInternalFunction(data?: any, isEdit?: boolean) {
  if (isEdit) {
    functionLibApi.putFunctionLib(data?.id as string, data, loading).then((res) => {
      MsgSuccess(t('common.saveSuccess'))
      searchHandle()
    })
  } else {
    functionLibApi
      .addInternalFunction(data.id, { name: data.name }, changeStateloading)
      .then((res) => {
        MsgSuccess(t('common.addSuccess'))
        searchHandle()
      })
  }
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'function', selectUserId.value)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  functionLibList.value = []
  getList()
}

async function changeState(bool: Boolean, row: any) {
  if (!bool) {
    MsgConfirm(
      `${t('views.functionLib.disabled.confirmTitle')}${row.name} ?`,
      t('views.functionLib.disabled.confirmMessage'),
      {
        confirmButtonText: t('views.functionLib.setting.disabled'),
        confirmButtonClass: 'danger'
      }
    )
      .then(() => {
        const obj = {
          is_active: bool
        }
        functionLibApi.putFunctionLib(row.id, obj, changeStateloading).then((res) => { })
      })
      .catch(() => {
        row.is_active = true
      })
  } else {
    const res = await functionLibApi.getFunctionLibById(row.id, changeStateloading)
    if (
      !res.data.init_params &&
      res.data.init_field_list &&
      res.data.init_field_list.length > 0 &&
      res.data.init_field_list.filter((item: any) => item.default_value && item.show_default_value).length !==
        res.data.init_field_list.length
    ) {
      InitParamDrawerRef.value.open(res.data, bool)
      row.is_active = false
      return
    }
    const init_params = res.data.init_field_list.reduce((acc: any, item: any) => {
      acc[item.field] = item.default_value
      return acc
    }, {})
    const obj = {
      is_active: bool,
      init_params: init_params,
      init_field_list: res.data.init_field_list
    }
    functionLibApi.putFunctionLib(row.id, obj, changeStateloading).then((res) => { })
  }
}

function deleteFunctionLib(row: any) {
  MsgConfirm(
    `${t('views.functionLib.delete.confirmTitle')}${row.name} ?`,
    t('views.functionLib.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      functionLibApi.delFunctionLib(row.id, loading).then(() => {
        const index = functionLibList.value.findIndex((v) => v.id === row.id)
        functionLibList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => { })
}

function copyFunctionLib(row: any) {
  title.value = t('views.functionLib.copyFunction')
  const obj = cloneDeep(row)
  delete obj['id']
  obj['name'] = obj['name'] + `  ${t('views.functionLib.functionForm.title.copy')}`
  FunctionFormDrawerRef.value.open(obj)
}

function exportFunctionLib(row: any) {
  functionLibApi.exportFunctionLib(row.id, row.name, loading).catch((e: any) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}

function configPermission(item: any) {
  PermissionDialogRef.value.open(item)
}

function configInitParams(item: any) {
  functionLibApi.getFunctionLibById(item?.id, changeStateloading).then((res) => {
    InitParamDrawerRef.value.open(res.data)
  })
}

function importFunctionLib(file: any) {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  functionLibApi
    .importFunctionLib(formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        searchHandle()
      }
    })
    .catch((e: any) => {
      if (e.code === 400) {
        MsgConfirm(t('common.tip'), t('views.application.tip.professionalMessage'), {
          cancelButtonText: t('common.confirm'),
          confirmButtonText: t('common.professional')
        }).then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
      }
    })
}

async function getList() {
  if (userOptions.value?.length === 0) {
    await getUserList()
  }
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(functionType.value && { function_type: functionType.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value })
  }
  functionLibApi.getFunctionLib(paginationConfig, params, loading).then((res: any) => {
    res.data.records.forEach((item: any) => {
      if (user.userInfo && item.user_id === user.userInfo.id) {
        item.username = user.userInfo.username
      } else {
        item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
      }
    })
    functionLibList.value = [...functionLibList.value, ...res.data.records]
    paginationConfig.total = res.data.total
  })
}

function refresh(data: any) {
  if (data) {
    const index = functionLibList.value.findIndex((v) => v.id === data.id)
    if (user.userInfo && data.user_id === user.userInfo.id) {
      data.username = user.userInfo.username
    } else {
      data.username = userOptions.value.find((v) => v.value === data.user_id)?.label
    }
    functionLibList.value.splice(index, 1, data)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  functionLibList.value = []
  getList()
}

async function getUserList() {
  const res = await applicationApi.getUserList('FUNCTION', loading)
  if (res.data) {
    userOptions.value = res.data.map((item: any) => {
      return {
        label: item.username,
        value: item.id
      }
    })
    if (user.userInfo) {
      const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'function')
      if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
        selectUserId.value = selectUserIdValue
      }
    }
  }
}

onMounted(() => {

})
</script>
<style lang="scss" scoped>
.application-card-add {
  width: 100%;
  font-size: 14px;
  min-height: var(--card-min-height);
  border: 1px dashed var(--el-border-color);
  background: var(--el-disabled-bg-color);
  border-radius: 8px;
  box-sizing: border-box;

  &:hover {
    border: 1px solid var(--el-card-bg-color);
    background-color: var(--el-card-bg-color);
  }

  .card-add-button {
    &:hover {
      border-radius: 4px;
      background: var(--app-text-color-light-1);
    }

    :deep(.el-upload) {
      display: block;
      width: 100%;
      color: var(--el-text-color-regular);
    }
  }
}

.application-card {
  .status-tag {
    position: absolute;
    right: 16px;
    top: 15px;
  }
}

.function-lib-list-container {
  width: 100%;
  height: 100%;
  position: relative;
  box-sizing: border-box;
  padding: 20px;

  .fl-list-container {
    width: 100%;
    height: 100%;
    position: relative;
    background-color: var(--app-view-bg-color);

    .condition {
      height: 56px;
      line-height: 56px;
      padding: 0 20px;
      border-bottom: 1px solid #E9ECF2;
    }

    .content {
      width: 100%;
      height: calc(100% - 130px);
      position: relative;
      padding: 20px;
      overflow-y: auto !important;
      box-sizing: border-box !important;

      .abs {
        width: 100%;
        height: 100%;
        position: absolute;
        overflow-y: auto;
      }
    }

  }

  .delete-button {
    position: absolute;
    right: 12px;
    top: 15px;
    height: auto;
  }

  :deep(.el-divider__text) {
    background: var(--app-layout-bg-color);
  }

  .status-tag {
    position: absolute;
    right: 20px;
    top: 30px;
    display: flex;

    .green-tag {
      height: 24px !important;
      padding: 0 6px;
      background-color: #E6FFF4 !important;
      color: #11C79B !important;
      border: none;
    }

    .orange-tag {
      @extend .green-tag;
      background-color: #FFF4E6 !important;
      color: #FF6600 !important;
    }
  }
}
</style>
<style lang="scss">
.function-lib-list-container {
  .el-tabs {
    .el-tabs__nav-wrap {
      padding-left: var(--app-view-padding,20px);
      .el-tabs__nav {
        margin-left: 0!important;
      }
    }
  }
  .condition {
    .el-input__wrapper {
      border-radius: 16px;
    }
  }

  .el-card {
    --el-card-padding: 20px;
    border-radius: 4px;
    border: 1px solid #E9ECF2;

    .title {
      height: 24px;
      line-height: 24px;
      font-size: 16px;
      font-weight: 600;

      .el-text {
        font-weight: 400;
        font-size: 14px;
        color: #6B7A99;
      }
    }

    &:hover {
      box-shadow: 0 5px 20px 0 #0043ca1a;
    }

    .description {
      height: 88px;
      max-height: 88px;
      position: relative;
      font-weight: 400;
      font-size: 14px;
      color: #223355;
      line-height: 22px;      
    }

    .info {
      height: 58px;
      line-height: 58px;
      position: relative;
      font-weight: 400;
      font-size: 14px;
      color: #6B7A99;
      display: flex;
      align-items: center;
      border-bottom: 1px solid #E9ECF2;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      .username {
        font-weight: 400;
        font-size: 14px;
        color: #A8B4C8;
        margin-left: 4px;
      }

      .time {
        margin-left: 4px;
        margin-right: 5px;

      }
    }

    .card-footer {
      text-align: right;
      bottom: 6px;
    }
  }

  .function-lib-card {
    height: 250px;
  }
}
.function-footer {
  display: flex !important;
  justify-content: flex-end !important;
  align-items: center !important;
}
</style>