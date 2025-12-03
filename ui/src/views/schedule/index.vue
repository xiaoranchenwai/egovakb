<template>
  <div class="schedule-task-container">
    <div class="st-list-container">
      <div class="flex-between condition">
        <div class="flex-between">
          <el-button round @click.stop="openCreateDialog">
            <el-icon><Plus /></el-icon>
            {{ $t('views.schedule.createTask') }}
          </el-button>
          <el-button round @click.stop="refresh">
            <el-icon><Refresh /></el-icon>
            {{ $t('common.refresh') }}
          </el-button>
        </div>
        <div class="flex-between">
          <el-select v-model="selectUserId" class="mr-12" style="max-width: 240px; width: 150px" @change="searchHandle"
            filterable
            placeholder="选择用户"
            clearable
          >
            <el-option v-for="item in userOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <el-input v-model="searchValue" @change="searchHandle"
            placeholder="搜索定时任务" suffix-icon="Search" class="w-240 custom"
            style="max-width: 240px" clearable />
        </div>
      </div>

      <div class="content" v-loading="loading">
        <InfiniteScroll 
          :size="taskList.length" 
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size" 
          v-model:current_page="paginationConfig.current_page" 
          @load="getScheduleList"
          :loading="loading"
        >
          <div class="hit-test-height" v-if="taskList.length === 0">
            <el-empty
                :image="emptyImg"
                description="没有搜索结果"
                style="padding-top: 160px"
                :image-size="125"
            />
          </div>
          <el-row v-else :gutter="15">
            <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="6" 
              v-for="(item, index) in taskList" 
              :key="index"
              class="mb-16"
            >
              <CardBox 
                :title="item.name" 
                :description="item.desc" 
                class="schedule-card cursor"
                @click="openEditDialog(item)"
              >
                <template #icon>
                  <AppAvatar :name='item?.name' pinyinColor shape='square' :size='48'
                  class='mr-8' />
                </template>
                
                
                <template #description>
                  <el-text truncated class="schedule-desc">{{ item.desc }}</el-text>
                  <div class="schedule-info mt-8">
                    <el-icon><Timer /></el-icon>
                    <el-text class="schedule-text">执行规则: {{ getCronDescription(item.cron_expression) }}</el-text>
                  </div>
                  <div class="schedule-info mt-4">
                    <el-icon><Calendar /></el-icon>
                    <el-text class="schedule-text" v-if="item.is_active">下次执行时间: {{ getNextRunTime(item.cron_expression) }}</el-text>
                    <el-text class="schedule-text" v-else>下次执行时间:未启用</el-text>
                  </div>
                </template>
                
                <div class='info flex'>
                  <el-avatar v-if="item?.user_avatar" :src="item?.user_avatar" :size='20'></el-avatar>
                  <el-avatar v-else src='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
                    :size='20' />
                  <el-text class="w-150px mb-2 username" truncated>
                    {{ item?.username || '未知' }}
                  </el-text>
                  <el-text class="w-150px mb-2 time time-right" truncated>
                    {{ datetimeFormat(item?.create_time) }}
                  </el-text>
                </div>

                <template #footer>
                  <div class="footer-content flex-between">
                    <div>
                      <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                        <el-button text @click.stop="deleteTask(item)" class="action-button delete-button">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip effect="dark" :content="$t('common.detail')" placement="top">
                        <el-button text @click.stop="openDetailDialog(item)" class="action-button detail-button">
                          <el-icon><View /></el-icon>
                        </el-button>
                      </el-tooltip>
                      <el-tooltip effect="dark" :content="$t('views.schedule.execute')" placement="top">
                        <el-button text @click.stop="executeTask(item)" class="action-button execute-button">
                          <el-icon><VideoPlay /></el-icon>
                        </el-button>
                      </el-tooltip>
                    </div>
                    <div @click.stop>
                      <el-switch
                        v-model="item.is_active"
                        @change="changeState($event, item)"
                        inline-prompt
                        :active-text="$t('views.applicationOverview.appInfo.openText')"
                        :inactive-text="$t('views.applicationOverview.appInfo.closeText')"
                      />
                    </div>
                  </div>
                </template>
              </CardBox>
            </el-col>
          </el-row>

        </InfiniteScroll>
      </div>
    </div>

    <ScheduleFormDrawer ref="ScheduleFormDrawerRef" @refresh="refresh" :title="title" />
    <ScheduleTaskDetailDrawer ref="ScheduleTaskDetailDrawerRef" :taskId="currentTaskId" @refresh="refresh" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watchEffect } from 'vue'
import { Plus, EditPen, Delete, Refresh, View, VideoPlay, Timer, Calendar } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import scheduleApi from '@/api/schedule'
import applicationApi from '@/api/application'
import ScheduleFormDrawer from './component/ScheduleFormDrawer.vue'
import ScheduleTaskDetailDrawer from './component/ScheduleTaskDetailDrawer.vue'
import type { ScheduleTaskData } from '@/api/type/schedule'
import useStore from '@/stores'
import dayjs from 'dayjs'
import { datetimeFormat } from '@/utils/time'
import cronstrue from 'cronstrue/i18n'
import CronExpressionParser from 'cron-parser'
import emptyImg from '@/assets/hit-test-empty.png'

const { t } = useI18n()
const { user } = useStore()
const loading = ref(false)
const taskList = ref<ScheduleTaskData[]>([])
const title = ref('')
const ScheduleFormDrawerRef = ref()
const ScheduleTaskDetailDrawerRef = ref()
const searchValue = ref('')
const selectUserId = ref('')
const currentTaskId = ref('')

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

function openCreateDialog() {
  title.value = t('views.schedule.createTask')
  try {
    // 确保组件已经挂载
    if (!ScheduleFormDrawerRef.value) {
      console.error('ScheduleFormDrawer 组件引用为空')
      // 强制重新获取组件引用
      setTimeout(() => {
        if (ScheduleFormDrawerRef.value) {
          ScheduleFormDrawerRef.value.open()
        }
      }, 100)
      return
    }
    ScheduleFormDrawerRef.value.open()
  } catch (error) {
    console.error('调用抽屉组件时出错:', error)
  }
}

function openDetailDialog(row: ScheduleTaskData) {
  currentTaskId.value = row.id
  ScheduleTaskDetailDrawerRef.value.open()
}

function openEditDialog(row: ScheduleTaskData) {
  title.value = t('views.schedule.editTask')
  ScheduleFormDrawerRef.value.open(row)
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'schedule', selectUserId.value)
  }
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  taskList.value = []
  getScheduleList()
}

function changeState(bool: boolean, row: ScheduleTaskData) {
  scheduleApi.putScheduleTask(row.id, { is_active: bool }, loading).then(() => {
    MsgSuccess(t('common.updateSuccess'))
    refresh()
  })
}

function deleteTask(row: ScheduleTaskData) {
  MsgConfirm(t('views.schedule.deleteConfirm'), '', {
    confirmButtonText: t('common.delete'),
    cancelButtonText: t('common.cancel'),
    type: 'warning'
  }).then(() => {
    scheduleApi.deleteScheduleTask(row.id, loading).then(() => {
      MsgSuccess(t('common.deleteSuccess'))
      getScheduleList()
    })
  })
}

function getScheduleList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value && { select_user_id: selectUserId.value === 'all' ? null : selectUserId.value })
  }
  
  scheduleApi.getScheduleTaskList(paginationConfig, params, loading).then((res) => {
    res.data.records.forEach((item: any) => {
      if (user.userInfo && item.user_id === user.userInfo.id) {
        item.username = user.userInfo.username
      } else {
        if (item?.username) {
          // pass
        } else {
          item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
        }
      }
    })
    taskList.value = [...taskList.value, ...res.data.records]
    paginationConfig.total = res.data.total
  })
}

function getUserList() {
  applicationApi.getUserList('SCHEDULE', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'schedule')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
      getScheduleList()
    }
  })
}

function refresh() {
  paginationConfig.current_page = 1
  paginationConfig.total = 0
  taskList.value = []
  getScheduleList()
}

// 获取CRON表达式的可读描述
function getCronDescription(cronExpression: string) {
  if (!cronExpression) return '未设置';
  
  try {
    // 规范化CRON表达式格式
    let cronExpr = cronExpression.trim();
    const parts = cronExpr.split(' ');
    
    // 确保至少有5个部分
    if (parts.length < 5) {
      while (parts.length < 5) {
        parts.push('*');
      }
      cronExpr = parts.join(' ');
    }
    
    // 添加秒字段（如果需要）
    const fullCronExpr = parts.length === 5 ? `0 ${cronExpr}` : cronExpr;
    
    return cronstrue.toString(fullCronExpr, { locale: 'zh_CN', use24HourTimeFormat: true, verbose: true });
  } catch (e) {
    console.error('解析CRON表达式失败:', cronExpression, e);
    return '无法解析的表达式';
  }
}

// 获取下一次执行时间
function getNextRunTime(cronExpression: string) {
  if (!cronExpression) return '未设置';
  
  try {
    // 规范化CRON表达式格式
    let cronExpr = cronExpression.trim();
    const parts = cronExpr.split(' ');
    
    // 确保至少有5个部分
    if (parts.length < 5) {
      while (parts.length < 5) {
        parts.push('*');
      }
      cronExpr = parts.join(' ');
    }
    
    // 添加秒字段（如果需要）
    const fullCronExpr = parts.length === 5 ? `0 ${cronExpr}` : cronExpr;
    
    // 使用正确的解析方法
    const interval = CronExpressionParser.parse(fullCronExpr);
    const next = interval.next().toDate();
    return datetimeFormat(next);
  } catch (e) {
    console.error('计算下次执行时间失败:', cronExpression, e);
    return '无法计算';
  }
}

// 添加执行任务的方法
function executeTask(row: ScheduleTaskData) {
  MsgConfirm(t('views.schedule.executeConfirm'), '', {
    confirmButtonText: t('common.confirm'),
    cancelButtonText: t('common.cancel'),
    type: 'info'
  }).then(() => {
    scheduleApi.executeScheduleTask(row.id, loading).then(() => {
      MsgSuccess(t('views.schedule.executeSuccess'))
    })
  })
}

onMounted(() => {
  getUserList()
})
</script>

<style lang="scss" scoped>
.schedule-task-container {
  width: 100%;
  height: 100%;
  position: relative;
  box-sizing: border-box;
  padding: 20px;

  .st-list-container {
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
      height: calc(100% - 56px);
      position: relative;
      padding: 20px;
      overflow-y: auto !important;
      box-sizing: border-box;
    }
  }

  .schedule-card {
    height: 250px;
    
    .status-tag {
      position: absolute;
      right: 20px;
      top: 30px;
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
  }

  .footer-content {
    .bold {
      color: var(--app-text-color);
    }
  }
  
  .time-right {
    position: absolute;
    right: 0;
  }
}

.schedule-task-container {
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
      height: 120px;
      max-height: 120px;
      position: relative;
      font-weight: 400;
      font-size: 14px;
      color: #223355;
      line-height: 22px;
      border-bottom: 1px solid #E9ECF2;
    }
  }
}

.action-button {
  margin: 0 4px;
  
  &:hover {
    transform: scale(1.1);
    transition: all 0.2s;
  }
}

.delete-button {
  &:hover {
    color: #f56c6c;
  }
}

.detail-button {
  &:hover {
    color: #409eff;
  }
}

.execute-button {
  &:hover {
    color: #67c23a;
  }
}
</style> 

<style lang="scss">
.schedule-task-container {  
  .el-input.custom {
    .el-input__wrapper {
      border-radius: 15px;
    }
  }
}
.el-card {
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

  .el-card__body {
    .card-header {
      padding-top: 12px;
    }
    .description {
      padding-top: 5px;
      height: 72px !important;
    }  
  }
}

.el-tabs {
  .el-tabs__header {
    .el-tabs__nav-scroll {
      .el-tabs__nav {
        margin-left: 40px !important;
        .el-tabs__item {
          cursor: pointer;
        }
      }
    }
  }
}
</style>

<style scoped>
.schedule-desc {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.schedule-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.schedule-text {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>