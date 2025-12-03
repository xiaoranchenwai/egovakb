<template>
  <div class='application-list-container'>
    <div class='app-list-container'>
      <div class='flex-between condition'>
        <div class='flex-between'>
          <el-button round @click.stop='openCreateDialog' style="color:#3388FF;width:88px">
            <el-icon color="#3388FF" style="margin-right: 2px;">
              <Plus />
            </el-icon>
            {{ $t('common.create') }}
          </el-button>
          <el-divider direction='vertical' />
          <el-upload ref='elUploadRef' :file-list='[]' action='#' multiple :auto-upload='false' :show-file-list='false'
            :limit='1' :on-change='(file: any, fileList: any) => importApplication(file)' class='card-add-button'>
            <div class='flex align-center cursor p-8'>
              <AppIcon iconName='app-import' class='mr-8'></AppIcon>
              {{ $t('views.application.importApplication') }}
            </div>
          </el-upload>
        </div>
        <div>
          <el-select
            v-model="selectUserId"
            class="mr-12"
            @change="searchHandle"
            style="max-width: 240px; width: 150px"
            filterable
            placeholder="选择用户"
            clearable
          >
            <el-option
              v-for="item in userOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input v-model='searchValue' @change='searchHandle' :placeholder="$t('common.search')"
            class='w-240 combine-input' style='min-width: 240px' clearable >
            <template #append>
              <el-button :icon="Search" />
            </template>
          </el-input>
        </div>
      </div>

      <el-tabs v-model='activeName' class='demo-tabs' @tab-click='onTabClick'>
        <el-tab-pane v-for='item in tabPanes' :key='item.value' :label='item.label' :name='item.value'>
          <div class='content' v-loading.fullscreen.lock='paginationConfig.current_page === 1 && loading'>
            <div class='abs'>
              <InfiniteScroll :size='applicationList.length' :total='paginationConfig.total'
                :page_size='paginationConfig.page_size' :current_page='paginationConfig.current_page'
                @update:current_page='(page: number) => paginationConfig.current_page = page' @load='getList' :loading='loading'>
                <el-row :gutter='15'>
                  <el-col :xs='24' :sm='12' :md='12' :lg='8' :xl='6' v-for='(item, index) in dataList' :key='index'
                    class='mb-16'>
                    <CardBox :title='item.name' :description='item.desc' class='application-card cursor' @click='
                      router.push({ path: `/application/${item.id}/${item.type}/overview` })
                      '>
                      <template #icon>
                        <AppAvatar v-if='isAppIcon(item?.icon)' shape='square' :size='48' style='background: none'
                          class='mr-8'>
                          <img :src='item?.icon' alt='' />
                        </AppAvatar>
                        <AppAvatar v-else-if='item?.name' :name='item?.name' pinyinColor shape='square' :size='48'
                          class='mr-8' />
                      </template>
                      <div class='status-tag'>
                        <div v-if="item.group_name" class="group-tag">
                            <el-tag size="small" class="group-name-tag">{{ item.group_name }}</el-tag>
                        </div>
                        <el-tag class='orange-tag' type='warning' v-if='isWorkFlow(item.type)' style='height: 24px'>高级编排
                        </el-tag>
                        <el-tag class='green-tag' v-else style='height: 24px'>简单配置</el-tag>
                      </div>
                      <template #description>
                        <el-text line-clamp="3">
                          {{ item.desc || item.problem_optimization_prompt }}
                        </el-text>
                      </template>

                      <div class='info flex'>
                        <el-avatar v-if="item.user_avatar" :src="item.user_avatar" :size='20'>
                        </el-avatar>
                        <el-avatar v-else src='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
                          :size='20' />
                        <el-text class="w-150px mb-2 username" truncated>
                          {{ item.username }}
                        </el-text>
                        <el-text class="w-150px mb-2 time time-right" truncated>
                          {{ datetimeFormat(item.create_time) }}
                        </el-text>
                      </div>
                      <template #footer>
                        <div>
                          <el-tooltip effect='dark' :content="$t('views.application.setting.demo')" placement='top'>
                            <el-button text @click.stop @click='getAccessToken(item.id)'>
                              <AppIcon class='app-view'></AppIcon>
                            </el-button>
                          </el-tooltip>
                          <el-divider direction='vertical' />
                          <el-tooltip effect='dark' :content="$t('common.setting')" placement='top'>
                            <el-button text @click.stop='settingApplication(item)'>
                              <AppIcon class='setting'></AppIcon>
                            </el-button>
                          </el-tooltip>
                          <el-divider direction='vertical' />
                          <span @click.stop>
                            <el-dropdown trigger='click' popper-class="app-dropdown">
                              <el-button text @click.stop>
                                <el-icon>
                                  <MoreFilled color="#A8B4C8"/>
                                </el-icon>
                              </el-button>
                              <template #dropdown>
                                <el-dropdown-menu>
                                  <el-dropdown-item v-if='is_show_copy_button(item)' @click='copyApplication(item)'>
                                    <AppIcon iconName='app-copy'></AppIcon>
                                    {{ $t('common.copy') }}
                                  </el-dropdown-item>
                                  <el-dropdown-item @click.stop='exportApplication(item)'>
                                    <AppIcon iconName='app-export'></AppIcon>

                                    {{ $t('common.export') }}
                                  </el-dropdown-item>
                                  <el-dropdown-item icon='Delete' @click.stop='deleteApplication(item)'>{{
                                    $t('common.delete') }}</el-dropdown-item>
                                </el-dropdown-menu>
                              </template>
                            </el-dropdown>
                          </span>
                        </div>
                      </template>
                    </CardBox>
                  </el-col>
                </el-row>
              </InfiniteScroll>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <CreateApplicationDialog ref='CreateApplicationDialogRef' />
      <CopyApplicationDialog ref='CopyApplicationDialogRef' />
    </div>
  </div>
</template>
<script setup lang='ts'>
import { ref, onMounted, reactive, onBeforeMount, computed, watch } from 'vue'
import applicationApi from '@/api/application'
import CreateApplicationDialog from './component/CreateApplicationDialog.vue'
import CopyApplicationDialog from './component/CopyApplicationDialog.vue'
import { MsgSuccess, MsgConfirm, MsgAlert, MsgError } from '@/utils/message'
import { isAppIcon } from '@/utils/application'
import { useRouter, useRoute } from 'vue-router'
import { isWorkFlow } from '@/utils/application'
import { ValidType, ValidCount } from '@/enums/common'
import { t } from '@/locales'
import useStore from '@/stores'
import http from '@/api/http-utils'
import { datetimeFormat } from '@/utils/time'
import { Search } from '@element-plus/icons-vue';

const props = defineProps<{
  selectedGroup: any
}>()

const __FILE__ = 'ApplicationList'
const elUploadRef = ref<any>()
const { application, user, common } = useStore()
const router = useRouter()
const route = useRoute()

const CopyApplicationDialogRef = ref()
const CreateApplicationDialogRef = ref()
const loading = ref(false)
const groupList = ref<any>([])
const applicationList = ref<any[]>([])

const dataList = computed(() => {
  switch (activeName.value) {
    case 'ALL':
      return applicationList.value
    case 'SIMPLE':
    case 'WORK_FLOW':
      return applicationList.value.filter((g: any) => g.type === activeName.value)
    default:
      return applicationList.value
  }
})

const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')

const searchValue = ref('')

const tabPanes = computed(() => {
  const allCount = paginationConfig.total;
  const simpleCount = applicationList.value.filter(app => app.type === 'SIMPLE').length;
  const workflowCount = applicationList.value.filter(app => app.type === 'WORK_FLOW').length;

  return [
    { label: `全部 (${allCount})`, value: 'ALL' },
    { label: `简单应用 (${simpleCount})`, value: 'SIMPLE' },
    { label: `高级应用 (${workflowCount})`, value: 'WORK_FLOW' }
  ];
})
const activeName = ref('ALL')

function onTabClick(tab: any, event: any) {
  console.log(tab.props.name)
}

function copyApplication(row: any) {
  application.asyncGetApplicationDetail(row.id, loading).then((res: any) => {
    CopyApplicationDialogRef.value.open({ ...res.data, model_id: res.data.model })
  })
}

const is_show_copy_button = (row: any) => {
  console.log(user, user?.userInfo?.id, row.user_id, user?.userInfo?.id === row.user_id)

  return user.userInfo ? user.userInfo.id == row.user_id : false
}

function settingApplication(row: any) {
  if (isWorkFlow(row.type)) {
    // router.push({ path: `/application/${ row.id }/workflow` });
    router.push({ path: `/application/${row.id}/WORK_FLOW/flow` })
  } else {
    router.push({ path: `/application/${row.id}/${row.type}/setting` })
  }
}

const exportApplication = (application: any) => {
  applicationApi.exportApplication(application.id, application.name, loading).catch((e) => {
    if (e.response.status !== 403) {
      e.response.data.text().then((res: string) => {
        MsgError(`${t('views.application.tip.ExportError')}:${JSON.parse(res).message}`)
      })
    }
  })
}
const importApplication = (file: any) => {
  const formData = new FormData()
  formData.append('file', file.raw, file.name)
  elUploadRef.value.clearFiles()
  applicationApi
    .importApplication(formData, loading)
    .then(async (res: any) => {
      if (res?.data) {
        searchHandle()
      }
    })
    .catch((e) => {
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

function openCreateDialog() {
  CreateApplicationDialogRef.value.open()
}

function searchHandle() {
  activeName.value = 'ALL'
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'application', selectUserId.value)
  }
  applicationList.value = []
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  getList()
}

function getAccessToken(id: string) {
  application.asyncGetAccessToken(id, loading).then((res: any) => {
    window.open(application.location + res?.data?.access_token)
    // const accessToken = res?.data?.access_token || '';
    // router.push({ path: `/application/ai/${accessToken}` });
  })
}

function deleteApplication(row: any) {
  MsgConfirm(
    // @ts-ignore
    `${t('views.application.delete.confirmTitle')}${row.name} ?`,
    t('views.application.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      applicationApi.delApplication(row.id, loading).then(() => {
        const index = applicationList.value.findIndex((v) => v.id === row.id)
        applicationList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {
    })
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value }),
    ...(props.selectedGroup && { group_id: props.selectedGroup.id })
  }
  if (props.selectedGroup) {
    console.log('getList params', params)
    applicationApi.getAllAppilcation(params, loading).then((res: { data:  any[]}) => {
      console.log('getList res', res.data)
      res.data.forEach((item: any) => {
          if (item.username) {
            // 用户名已存在，不需要处理
          } else {
            if (user.userInfo && item.user_id === user.userInfo.id) {
              item.username = user.userInfo.username
            } else {
              item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
            }
          }
        })
        applicationList.value = [...applicationList.value, ...res.data]
        paginationConfig.total = res.data.length
    })
  } else {
    console.log('getList params', params)
    applicationApi
      .getApplication(paginationConfig, params, loading)
      .then((res: { data: { records: any[]; total: number } }) => {
        console.log('getList res', res.data)
        res.data.records.forEach((item: any) => {
          if (item.username) {
            // 用户名已存在，不需要处理
          } else {
            if (user.userInfo && item.user_id === user.userInfo.id) {
              item.username = user.userInfo.username
            } else {
              item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
            }
          }
        })
        applicationList.value = [...applicationList.value, ...res.data.records]
        paginationConfig.total = res.data.total
      })
  }
}

function getUserList() {
  applicationApi.getUserList('APPLICATION', loading).then((res: { data: any[] }) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'application')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
      getList()
    }
  })
}

onMounted(() => {
  const { reload } = route.query || {}
  console.log(reload)
  if (reload === '1') {
    router.push({ query: {} })
    setTimeout(() => {
      location.reload()
    }, 300)
  } else {
    getUserList()
  }
})

// 监听分组变化
watch(() => props.selectedGroup, (newVal) => {
  // console.log('oldVal', props.selectedGroup, 'newVal', newVal)
  searchHandle()
})
</script>
<style lang='scss' scoped>
.application-list-container {
  width: 100%;
  height: 100%;
  position: relative;
  box-sizing: border-box;
  padding: 20px;

  .app-list-container {
    width: 100%;
    height: 100%;
    position: relative;
    background-color: var(--app-view-bg-color);

    .condition {
      height: 56px;
      line-height: 56px;
      padding: 0 20px;
      border-bottom: 1px solid #e9ecf2;

      .el-input__wrapper {
        border-radius: 16px;
      }
    }

    .el-tabs {
      height: calc(100% - 57px);
      --el-tabs-header-height: 50px;

      .content {
        width: 100%;
        height: 100%;
        position: relative;

        .abs {
          width: 100%;
          height: 100%;
          position: absolute;
          overflow-y: auto;
        }
      }
    }
  }
}

.application-card {
  height: 250px;

  .status-tag {
    position: absolute;
    right: 20px;
    top: 30px;
    display: flex;

    .green-tag {
      height: 24px !important;
      padding: 0 6px;
      background-color: #e6fff4;
      color: #11c79b;
      border: none;
    }

    .orange-tag {
      @extend .green-tag;
      background-color: #fff4e6;
      color: #ff6600;
    }
  }

  .group-tag {
    margin-left: 10px;
    display: flex;
    align-items: center;
    margin-right: 5px;

    .group-name-tag {
      background-color: #f0f7ff;
      color: #3e7de9;
      border: none;
      padding: 0 8px;
      height: 25px;
      line-height: 20px;
      font-size: 12px;
      // border-radius: 5px;
    }
  }
}

.dropdown-custom-switch {
  padding: 5px 11px;
  font-size: 14px;
  font-weight: 400;

  span {
    margin-right: 26px;
  }
}
</style>
<style lang='scss'>
.expand {
  .application-list-container {
    .el-col-xl-6 {
    }
  }
}

.app-list-container {
  .el-col-xl-6 {
  }

  .condition {
    .el-input__wrapper {
      border-radius: 16px;
    }
  }

  .el-tabs {
    .el-tabs__header {
      .el-tabs__nav-scroll {
        .el-tabs__nav {
          margin-left: 40px;

          .el-tabs__item {
            cursor: pointer;
          }
        }
      }
    }

    .el-tabs__content {
      .el-tab-pane {
        padding: 8px 20px 20px 20px;
        width: 100%;
        height: 100%;
        position: relative;
        box-sizing: border-box;

        .el-card {
          --el-card-padding: 20px;
          border-radius: 4px;
          border: 1px solid #e9ecf2;
          .el-card__body {
            .card-header {
              padding-top: 12px;
            }
          }
          .title {
            height: 24px;
            line-height: 24px;
            font-size: 16px;
            font-weight: 600;

            .el-text {
              font-weight: 400;
              font-size: 14px;
              color: #6b7a99;
            }
          }

          &:hover {
            box-shadow: 0 5px 20px 0 #0043ca1a;
          }

          .description {
            padding-top: 10px;
            height: 72px;
            // max-height: 62px;
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
            color: #6b7a99;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #e9ecf2;

            .username {
              font-weight: 400;
              font-size: 14px;
              color: #a8b4c8;
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
      }
    }
  }

  .card-footer {
    .el-button {
      &:hover {
        background-color: #F5F7FA !important;
      }
    }
  }
}

.chat-container {
  position: absolute;
  top: 20px;
  left: 20px;
  width: calc(100% - 40px);
  height: calc(100% - 40px);
  z-index: 99;

  .chat-pc {
    width: 100%;
    height: 100%;
    position: relative;
  }
}

.time-right {
  position: absolute;
  right: 0;
}

.combine-input {
  .el-input__wrapper {
    border-radius: 16px 0 0 16px !important;
  }
  .el-input-group__append {
    border-top-right-radius: 16px !important;
    border-bottom-right-radius: 16px !important;
    background-color: transparent;
  }
}

.app-dropdown {
  box-shadow: 0 2px 24px 0 #F5F7FA !important;
}

</style>
