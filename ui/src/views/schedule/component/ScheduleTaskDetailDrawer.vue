<template>
  <el-drawer v-model="visible" size="60%" @close="closeHandle">
    <template #header>
      <h4>{{ $t('views.schedule.taskDetail') }}</h4>
    </template>
    <div>
      <el-scrollbar>
        <div class="p-8">
          <el-tabs v-model="activeTab">
            <!-- <el-tab-pane :label="$t('views.schedule.taskInfo')" name="info">
              <el-form v-loading="loading" label-position="left" label-width="10em">
                <el-form-item :label="$t('views.schedule.taskName')">
                  <ReadWrite
                    @change="editTask('name', $event)"
                    :data="taskDetail.name || ''"
                    :showEditIcon="true"
                    :maxlength="64"
                  />
                </el-form-item>
                <el-form-item :label="$t('views.schedule.description')">
                  <ReadWrite
                    @change="editTask('desc', $event)"
                    :data="taskDetail.desc || ''"
                    :showEditIcon="true"
                    :maxlength="128"
                  />
                </el-form-item>
                <el-form-item :label="$t('views.schedule.cronExpression')">
                  <ReadWrite
                    @change="editTask('cron_expression', $event)"
                    :data="taskDetail.cron_expression || ''"
                    :showEditIcon="true"
                    :maxlength="64"
                  />
                </el-form-item>
                <el-form-item :label="$t('views.schedule.function')">
                  <el-select 
                    v-model="taskDetail.function_lib_id" 
                    @change="changeFunctionLib"
                    :placeholder="$t('views.schedule.tip.selectFunction')"
                  >
                    <el-option
                      v-for="item in functionList"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item :label="$t('views.schedule.parameters')">
                  <el-input
                    v-model="paramsString"
                    type="textarea"
                    :rows="5"
                    @change="changeParams"
                  />
                </el-form-item>
                <el-form-item :label="$t('views.schedule.status')">
                  <el-switch v-model="taskDetail.is_active" @change="changeStatus" />
                </el-form-item>
                <el-form-item :label="$t('views.schedule.nextRun')" v-if="taskStatus">
                  <el-tag :type="taskStatus.status === 'SCHEDULED' ? 'success' : 'info'">
                    {{ taskStatus.status === 'SCHEDULED' ? $t('views.schedule.scheduled') : $t('views.schedule.notScheduled') }}
                  </el-tag>
                  <span v-if="taskStatus.next_run_time" class="ml-2">
                    {{ taskStatus.next_run_time }}
                  </span>
                </el-form-item>
                <el-form-item :label="$t('views.schedule.lastExecution')" v-if="taskStatus && taskStatus.last_execution">
                  <el-tag :type="getStatusType(taskStatus.last_execution.status)">
                    {{ getStatusText(taskStatus.last_execution.status) }}
                  </el-tag>
                  <span v-if="taskStatus.last_execution.start_time" class="ml-2">
                    {{ datetimeFormat(taskStatus.last_execution.start_time) }}
                  </span>
                </el-form-item>
              </el-form>
            </el-tab-pane> -->
            <el-tab-pane :label="$t('views.schedule.executionRecords')" name="records">
              <el-form v-loading="loading" label-position="left" label-width="10em">
                <el-form-item :label="$t('views.schedule.lastExecution')+':'" v-if="taskStatus && taskStatus.last_execution">
                  <span v-if="taskStatus.last_execution.start_time" class="ml-2">
                    {{ datetimeFormat(taskStatus.last_execution.start_time) }}
                  </span>
                  <el-tag :type="getStatusType(taskStatus.last_execution.status)">
                    {{ getStatusText(taskStatus.last_execution.status) }}
                  </el-tag>
                </el-form-item>
                <el-form-item :label="$t('views.schedule.nextRun')+':'" v-if="taskStatus">
                  <span v-if="taskStatus.next_run_time" class="ml-2">
                    {{ taskStatus.next_run_time }}
                  </span>
                  <el-tag :type="taskStatus.status === 'SCHEDULED' ? 'success' : 'info'">
                    {{ taskStatus.status === 'SCHEDULED' ? $t('views.schedule.scheduled') : $t('views.schedule.notScheduled') }}
                  </el-tag>
                </el-form-item>
              </el-form>
              <div class="mb-4 flex-between">
                <div>
                  <el-select v-model="recordStatus" @change="loadRecords" style="width: 150px">
                    <el-option label="所有状态" value="" />
                    <el-option label="成功" value="SUCCESS" />
                    <el-option label="失败" value="FAILED" />
                    <el-option label="执行中" value="RUNNING" />
                  </el-select>
                </div>
                <el-button @click="loadRecords" type="primary" plain>
                  <el-icon><Refresh /></el-icon>
                  {{ $t('common.refresh') }}
                </el-button>
              </div>
              <el-table :data="recordList" style="width: 100%" v-loading="recordsLoading">
                <el-table-column prop="status" :label="$t('views.schedule.recordStatus')" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">
                      {{ getStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="start_time" :label="$t('views.schedule.startTime')" width="170">
                  <template #default="{ row }">
                    {{ datetimeFormat(row.start_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="end_time" :label="$t('views.schedule.endTime')" width="170">
                  <template #default="{ row }">
                    {{ row.end_time ? datetimeFormat(row.end_time) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="result" :label="$t('views.schedule.result')">
                  <template #default="{ row }">
                    <el-tooltip v-if="row.result" :content="row.result" placement="top">
                      <div class="truncate max-w-md">{{ row.result }}</div>
                    </el-tooltip>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="error_message" :label="$t('views.schedule.errorMessage')">
                  <template #default="{ row }">
                    <el-tooltip v-if="row.error_message" :content="row.error_message" placement="top">
                      <div class="truncate max-w-md text-red-500">{{ row.error_message }}</div>
                    </el-tooltip>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
              <div class="mt-4 text-right">
                <el-pagination
                  v-model:current-page="recordsPage.current_page"
                  v-model:page-size="recordsPage.page_size"
                  :page-sizes="[10, 20, 50, 100]"
                  layout="total, sizes, prev, pager, next"
                  :total="recordsPage.total"
                  @size-change="onRecordsSizeChange"
                  @current-change="onRecordsPageChange"
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-scrollbar>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import scheduleApi from '@/api/schedule'
import functionApi from '@/api/function-lib'
import { MsgSuccess, MsgError } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  taskId: string
}>()

const emit = defineEmits(['refresh'])

const visible = ref(false)
const loading = ref(false)
const recordsLoading = ref(false)
const activeTab = ref('records')
const taskDetail = ref<any>({})
const taskStatus = ref<any>(null)
const functionList = ref<any[]>([])
const recordList = ref<any[]>([])
const recordStatus = ref('')
const paramsString = ref('')

const recordsPage = reactive({
  current_page: 1,
  page_size: 10,
  total: 0
})

const getStatusType = (status: string) => {
  switch (status) {
    case 'SUCCESS':
      return 'success'
    case 'FAILED':
      return 'danger'
    case 'RUNNING':
      return 'warning'
    default:
      return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'SUCCESS':
      return '成功'
    case 'FAILED':
      return '失败'
    case 'RUNNING':
      return '执行中'
    default:
      return status
  }
}

const loadTaskDetail = () => {
  if (!props.taskId) return
  
  loading.value = true
  Promise.all([
    // scheduleApi.getScheduleTaskDetail(props.taskId),
    scheduleApi.getScheduleTaskStatus(props.taskId)
  ]).then(([statusRes]) => {
    // taskDetail.value = detailRes.data
    taskStatus.value = statusRes.data
    
    // 处理参数显示
    try {
      paramsString.value = JSON.stringify(taskDetail.value.params || {}, null, 2)
    } catch (e) {
      paramsString.value = '{}'
    }
    
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

const loadFunctions = () => {
  functionApi.getAllFunctionLib({}, loading).then((res) => {
    functionList.value = res.data || []
  })
}

const loadRecords = () => {
  recordsLoading.value = true
  scheduleApi.getScheduleTaskRecordsByPage(
    props.taskId,
    recordsPage,
    recordStatus.value ? { status: recordStatus.value } : undefined,
    recordsLoading
  ).then((res) => {
    recordList.value = res.data.records
    recordsPage.total = res.data.total
    recordsLoading.value = false
  }).catch(() => {
    recordsLoading.value = false
  })
}

const onRecordsSizeChange = () => {
  recordsPage.current_page = 1
  loadRecords()
}

const onRecordsPageChange = () => {
  loadRecords()
}

const editTask = (field: string, value: any) => {
  if (!value && field !== 'desc') {
    MsgError(t('views.schedule.tip.valueRequired'))
    return
  }
  
  const updateData = { [field]: value }
  scheduleApi.putScheduleTask(props.taskId, updateData, loading).then(() => {
    MsgSuccess(t('common.modifySuccess'))
    loadTaskDetail()
    emit('refresh')
  })
}

const changeStatus = () => {
  editTask('is_active', taskDetail.value.is_active)
}

const changeFunctionLib = () => {
  editTask('function_lib_id', taskDetail.value.function_lib_id)
}

const changeParams = () => {
  try {
    const params = JSON.parse(paramsString.value)
    editTask('params', params)
  } catch (error) {
    MsgError(t('views.schedule.tip.invalidJson'))
  }
}

const closeHandle = () => {
  emit('refresh')
}

const open = () => {
  loadFunctions()
  loadTaskDetail()
  loadRecords()
  visible.value = true
}

watch(() => props.taskId, () => {
  if (visible.value) {
    loadTaskDetail()
    recordsPage.current_page = 1
    loadRecords()
  }
})

defineExpose({
  open
})
</script>

<style lang="scss" scoped>
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
:deep(.el-tabs) {
    .el-tabs__header {
      .el-tabs__nav-scroll {
        .el-tabs__nav {
          margin-left: 20px !important;
        }
      }
    }
}
</style> 