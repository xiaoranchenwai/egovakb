<template>
  <LayoutContainer class="overview-container">
    <el-scrollbar>
      <div class="main-calc-height">
        <div class="white mb-16">
          <h4 class="title-decoration-1">
            <img src="../../assets/application/info.png" alt="" />
            {{ $t('views.applicationOverview.appInfo.header') }}
          </h4>
          <el-card shadow="never" class="overview-card" v-loading="loading">
            <div v-if="false" class="title flex align-center">
              <div class="edit-avatar mr-12" @mouseenter="showEditIcon = true" @mouseleave="showEditIcon = false">
                <AppAvatar v-if="isAppIcon(detail?.icon)" shape="square" :size="32" style="background: none">
                  <img :src="detail?.icon" alt="" />
                </AppAvatar>
                <AppAvatar v-else-if="detail?.name" :name="detail?.name" pinyinColor shape="square" :size="32" />
                <AppAvatar v-if="showEditIcon" shape="square" class="edit-mask" :size="32" @click="openEditAvatar">
                  <el-icon>
                    <EditPen />
                  </el-icon>
                </AppAvatar>
              </div>

              <h4>{{ detail?.name }}</h4>
            </div>

            <el-row :gutter="20">
              <el-col :span="12">
                <div class="box p-16">
                  <div class="flex flex-between">
                    <el-text class="bold g70" type="info">前端服务WebApp</el-text>
                    <el-switch v-model="accessToken.is_active" class="ml-8" inline-prompt style="width:48px"
                      :active-text="$t('views.applicationOverview.appInfo.openText')"
                      :inactive-text="$t('views.applicationOverview.appInfo.closeText')"
                      @change="changeState($event)" />
                  </div>

                  <div class="url-height flex align-center">
                    <span>开箱即用的前端页面，可嵌入至第三方应用</span>
                  </div>

                  <div class="g60 flex align-center">
                    <span class="vertical-middle lighter break-all ellipsis-1"> 公开访问URL: </span>
                    <div class="flex input align-center">
                      <span class="vertical-middle lighter break-all ellipsis-1">
                        {{ shareUrl }}
                      </span>

                      <el-button type="primary" text @click="copyClick(shareUrl)">
                        <AppIcon iconName="app-copy"></AppIcon>
                      </el-button>
                      <el-button @click="refreshAccessToken" type="primary" text style="margin-left: 1px">
                        <el-icon>
                          <RefreshRight />
                        </el-icon>
                      </el-button>
                    </div>
                  </div>
                  <div class="right">
                    <el-button @click="openDisplaySettingDialog" round>
                      {{ $t('views.applicationOverview.appInfo.displaySetting') }}
                    </el-button>
                    <el-button @click="openLimitDialog" round>
                      {{ $t('views.applicationOverview.appInfo.accessControl') }}
                    </el-button>
                    <el-button :disabled="!accessToken?.is_active" @click="openDialog" round>
                      {{ $t('views.applicationOverview.appInfo.embedInWebsite') }}
                    </el-button>
                    <el-button :disabled="!accessToken?.is_active" round @click.stop="onViewChat">
                      <a v-if="false && accessToken?.is_active" :href="shareUrl" target="_blank">
                        {{ $t('views.applicationOverview.appInfo.demo') }}
                      </a>
                      <span v-else> {{ $t('views.applicationOverview.appInfo.demo') }}</span>
                    </el-button>
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="box p-16">
                  <div class="flex">
                    <el-text type="info" class="bold g70"
                      >{{ $t('views.applicationOverview.appInfo.apiAccessCredentials') }}
                    </el-text>
                  </div>

                  <div class="url-height">
                    <span>可集成至第三方应用的后端即服务</span>
                  </div>
                  <div class="g60 flex align-center">
                    <span class="flex">
                      <el-text style="width: 110px">API 文档： </el-text>
                    </span>
                    <el-button
                      type="primary"
                      link
                      @click="toUrl(apiUrl)"
                      class="vertical-middle lighter break-all"
                    >
                      {{ apiUrl }}
                    </el-button>
                  </div>
                  <div class="flex align-center">
                    <span class="flex">
                      <el-text style="width: 100px">API访问凭证：</el-text>
                    </span>
                    <div class="flex input align-center">
                      <span class="vertical-middle lighter break-all ellipsis-1">{{ baseUrl + id }}
                      </span>

                      <el-button type="primary" text @click="copyClick(baseUrl + id)">
                        <AppIcon iconName="app-copy"></AppIcon>
                      </el-button>
                    </div>
                  </div>

                  <div class="right">
                    <el-button @click="openAPIKeyDialog" round>{{
                      $t('views.applicationOverview.appInfo.apiKey')
                    }}</el-button>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div class="white">
          <h4 class="title-decoration-1 mt-16">
            <img src="../../assets/application/detect.png" alt="" />
            {{ $t('views.applicationOverview.monitor.monitoringStatistics') }}
          </h4>
          <div class="mb-16" v-show="false">
            <el-select v-model="history_day" class="mr-12 w-120" @change="changeDayHandle">
              <el-option v-for="item in dayOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-date-picker v-if="history_day === 'other'" v-model="daterangeValue" type="daterange"
              :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
              :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')" format="YYYY-MM-DD"
              value-format="YYYY-MM-DD" @change="changeDayRangeHandle" />
          </div>
          <div v-loading="statisticsLoading">
            <StatisticsCharts :data="statisticsData" />
          </div>
        </div>
      </div>
    </el-scrollbar>
    <EmbedDialog ref="EmbedDialogRef" :data="detail" :api-input-params="mapToUrlParams(apiInputParams)" />
    <APIKeyDialog ref="APIKeyDialogRef" />
    <LimitDialog ref="LimitDialogRef" @refresh="refresh" />
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshIcon" />
    <XPackDisplaySettingDialog ref="XPackDisplaySettingDialogRef" @refresh="refresh" />
    <!-- <XPackDisplaySettingDialog ref="XPackDisplaySettingDialogRef" @refresh="refresh" v-if="user.isEnterprise()" /> -->
    <!-- <DisplaySettingDialog ref="DisplaySettingDialogRef" @refresh="refresh" v-else /> -->

    <div v-if='showChat' class='chat-container'>
      <ChatView v-model:visible='showChat' :applicationAvailable='applicationAvailable'
        :application_profile='application_profile'></ChatView>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EmbedDialog from './component/EmbedDialog.vue'
import APIKeyDialog from './component/APIKeyDialog.vue'
import LimitDialog from './component/LimitDialog.vue'
import DisplaySettingDialog from './component/DisplaySettingDialog.vue'
import XPackDisplaySettingDialog from './component/XPackDisplaySettingDialog.vue'
import EditAvatarDialog from './component/EditAvatarDialog.vue'
import StatisticsCharts from './component/StatisticsCharts.vue'
import applicationApi from '@/api/application'
import overviewApi from '@/api/application-overview'
import { nowDate, beforeDay } from '@/utils/time'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { copyClick } from '@/utils/clipboard'
import { isAppIcon } from '@/utils/application'
import useStore from '@/stores'
import { t } from '@/locales';
import ChatView from "../application/chat.vue";

const { user, application } = useStore()
const route = useRoute();
const router = useRouter();
const {
  params: { id }
} = route as any

const apiUrl = window.location.origin + '/doc/chat/'

const baseUrl = window.location.origin + '/api/application/'

const DisplaySettingDialogRef = ref()
const XPackDisplaySettingDialogRef = ref()
const EditAvatarDialogRef = ref()
const LimitDialogRef = ref()
const APIKeyDialogRef = ref()
const EmbedDialogRef = ref()

const accessToken = ref<any>({})
const detail = ref<any>(null)

const loading = ref(false);

const showChat = ref<boolean>(false);
const applicationAvailable = ref<boolean>(true);
const application_profile = ref<any>({});

const urlParams = computed(() =>
  mapToUrlParams(apiInputParams.value) ? '?' + mapToUrlParams(apiInputParams.value) : ''
)
const shareUrl = computed(
  () => application.location + accessToken.value.access_token + urlParams.value
)

const dayOptions = [
  {
    value: 7,
    // @ts-ignore
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days')
  },
  {
    value: 30,
    label: t('views.applicationOverview.monitor.pastDayOptions.past30Days')
  },
  {
    value: 90,
    label: t('views.applicationOverview.monitor.pastDayOptions.past90Days')
  },
  {
    value: 183,
    label: t('views.applicationOverview.monitor.pastDayOptions.past183Days')
  },
  {
    value: 'other',
    label: t('views.applicationOverview.monitor.pastDayOptions.other')
  }
]

const history_day = ref<number | string>(7)

// 日期组件时间
const daterangeValue = ref('')

// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: ''
})

const statisticsLoading = ref(false)
const statisticsData = ref([])

const showEditIcon = ref(false)
const apiInputParams = ref([])

function toUrl(url: string) {
  window.open(url, '_blank')
}

function openDisplaySettingDialog() {
  // if (user.isEnterprise()) {
    XPackDisplaySettingDialogRef.value?.open(accessToken.value, detail.value)
  // } else {
  //   DisplaySettingDialogRef.value?.open(accessToken.value, detail.value)
  // }
}

function openEditAvatar() {
  EditAvatarDialogRef.value.open(detail.value)
}

function changeDayHandle(val: number | string) {
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val)
    daterange.value.end_time = nowDate
    getAppStatistics()
  }
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getAppStatistics()
}

function getAppStatistics() {
  overviewApi.getStatistics(id, daterange.value, statisticsLoading).then((res: any) => {
    statisticsData.value = res.data
  })
}

function refreshAccessToken() {
  MsgConfirm(
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm1'),
    t('views.applicationOverview.appInfo.refreshToken.msgConfirm2'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel')
    }
  )
    .then(() => {
      const obj = {
        access_token_reset: true
      }
      // @ts-ignore
      const str = t('views.applicationOverview.appInfo.refreshToken.refreshSuccess')
      updateAccessToken(obj, str)
    })
    .catch(() => { })
}

function changeState(bool: Boolean) {
  const obj = {
    is_active: !bool
  }
  const str = obj.is_active ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  updateAccessToken(obj, str)
    .then(() => {
      return true
    })
    .catch(() => {
      return false
    })
}

async function updateAccessToken(obj: any, str: string) {
  applicationApi.putAccessToken(id as string, obj, loading).then((res) => {
    accessToken.value = res?.data
    MsgSuccess(str)
  })
}

function openLimitDialog() {
  LimitDialogRef.value.open(accessToken.value)
}

function openAPIKeyDialog() {
  APIKeyDialogRef.value.open()
}

function openDialog() {
  EmbedDialogRef.value.open(accessToken.value?.access_token)
}

function getAccessToken() {
  application.asyncGetAccessToken(id, loading).then((res: any) => {
    accessToken.value = res?.data
  })
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    detail.value = res.data
    detail.value.work_flow?.nodes
      ?.filter((v: any) => v.id === 'base-node')
      .map((v: any) => {
        apiInputParams.value = v.properties.api_input_field_list
          ? v.properties.api_input_field_list.map((v: any) => {
              return {
                name: v.variable,
                value: v.default_value
              }
            })
          : v.properties.input_field_list
            ? v.properties.input_field_list
                .filter((v: any) => v.assignment_method === 'api_input')
                .map((v: any) => {
                  return {
                    name: v.variable,
                    value: v.default_value
                  }
                })
            : []
      })
  })
}

function refresh() {
  getAccessToken()
}

function refreshIcon() {
  getDetail()
}

function mapToUrlParams(map: any[]) {
  const params = new URLSearchParams()

  map.forEach((item: any) => {
    params.append(encodeURIComponent(item.name), encodeURIComponent(item.value))
  })

  return params.toString() // 返回 URL 查询字符串
}

onMounted(() => {
  getDetail()
  getAccessToken()
  changeDayHandle(history_day.value)
});

function onViewChat() {
  window.open(shareUrl.value)
}

function getAppProfile() {
  return application.asyncGetAppProfile(loading).then((res: any) => {
    // show_history.value = res.data?.show_history
    application_profile.value = res.data || {}
  })
}

function getChatAccessToken(token: string) {
  return application.asyncAppAuthentication(token, loading).then(() => {
    return getAppProfile()
  })
}

function getChatInfos(accessToken: string) {
  return new Promise((resolve, reject) => {
    user.changeUserType(2)
    Promise.all([user.asyncGetProfile(), getChatAccessToken(accessToken)]).then(() => {
      resolve(true)
    })
      .catch(() => {
        applicationAvailable.value = false
        resolve(false)
      })
  })

}
</script>
<style lang="scss" scoped>
.overview-card {
  position: relative;

  .active-button {
    position: absolute;
    right: 16px;
    top: 21px;
  }

  .g70 {
    color: #081126;
  }

  .g60 {
    font-size: 14px;
    color: #223355;
  }
}
</style>
<style lang="scss">
.overview-container {
  width: 100%;
  height: 100%;
  position: relative;
  box-sizing: border-box;
  padding: 20px;
  padding: var(--app-view-padding) !important;
  .el-switch {
    --el-switch-on-color: #3388FF;
  }
  
  .el-scrollbar__view,
  .content-container__main {
    width: 100%;
    height: 100%;
    position: relative;
  }

  .content-container__main {
    background-color: transparent !important;

    .white {
      background-color: var(--app-view-bg-color);

      .title-decoration-1 {
        height: 54px;
        line-height: 54px;
        position: relative;
        padding-left: calc(var(--app-base-px) * 2);
        display: flex;
        align-items: center;

        > img {
          margin-right: 10px;
        }

        &::before {
          display: none;
        }
      }

      .el-card {
        border: none;

        .el-card__body {
          padding: 0 20px 20px 20px;

          .box {
            width: 100%;
            height: 186px;
            position: relative;
            border: 1px solid #e9ecf2;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-radius: 4px;
            color: #223355;

            .bold {
              font-weight: 700;
              font-size: 16px;
              color: #081126;
            }

            .url-height {
              font-size: 14px;
              color: #6B7A99;
            }

            .input {
              height: 32px;
              background: #ffffff;
              border: 1px solid #dde1eb;
              border-radius: 4px;
              margin-left: 10px;
              padding-left: 10px;
              padding-right: 10px;
            }

            .right {
              display: flex;
              flex-direction: row;
              justify-content: flex-end;
              align-items: center;

              .el-button {
                --el-text-color-regular: #223355;
              }
            }
          }
        }
      }
    }
  }

  .chat-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 99;

    .chat-pc {
      width: 100%;
      height: 100%;
      position: relative;
    }
  }
}
</style>
