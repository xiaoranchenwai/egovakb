<template>
  <div class="custom-log">
    <LayoutContainer :header="$t('views.log.title')">
      <div class="table">
        <div class="condition">
          <el-row class="time flex align-center">
            <el-text type="info" class="g60">时间范围：</el-text>
            <el-select
              v-model="history_day"
              class="mr-12"
              @change="changeDayHandle"
              style="width: 180px"
            >
              <el-option
                v-for="item in dayOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-date-picker v-model="daterangeValue" type="daterange"
              :start-placeholder="$t('views.applicationOverview.monitor.startDatePlaceholder')"
              :end-placeholder="$t('views.applicationOverview.monitor.endDatePlaceholder')" format="YYYY-MM-DD"
              value-format="YYYY-MM-DD" @change="changeDayRangeHandle" />
            <el-button round :type="isDay7 ? 'primary' : ''" @click.stop="changeDayHandle(7)">近一周</el-button>
            <el-button round :type="isDay30 ? 'primary' : ''" @click.stop="changeDayHandle(30)">近一月</el-button>
            <el-button round :type="isDay90 ? 'primary' : ''" @click.stop="changeDayHandle(90)">近三月</el-button>
          </el-row>

          <el-row class="btns flex align-center flex-between">
            <div style="display: flex; align-items: center" class="float-right">
              <el-button round @click="dialogVisible = true">
                <el-icon><Close /></el-icon>
                {{
                $t('views.log.buttons.clearStrategy')
              }}</el-button>
              <el-button round @click="exportLog"><el-icon>
                  <Upload />
                </el-icon>{{ $t('common.export') }}</el-button>
              <!-- <el-button round><el-icon>
                  <Delete />
              </el-icon>批量删除</el-button> -->
              <el-button round @click="openDocumentDialog" :disabled="multipleSelection.length === 0">
                {{ $t('views.log.addToDataset') }}
              </el-button>
            </div>
            <div class="flex align-center">
              <el-select v-model="apiKeyId" placeholder="请选择API用户" clearable class="w-240" @change="getList">
                <el-option v-for="item in apiKeyList" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
              <el-input v-model="search" @change="getList" placeholder="请输入关键字" suffix-icon="Search" class="w-240"
                  style="margin-left: 10px" clearable />
            </div>
          </el-row>

        </div>

        <app-table :data="tableData" :pagination-config="paginationConfig" @sizeChange="getList" @changePage="getList"
          @row-click="rowClickHandle" v-loading="loading" :row-class-name="setRowClass"
          @selection-change="handleSelectionChange" class="log-table">
          <el-table-column type="selection" width="55" />
          <el-table-column
            prop="abstract"
            :label="$t('views.log.table.abstract')"
            show-overflow-tooltip
          />
          <el-table-column
            prop="chat_record_count"
            :label="$t('views.log.table.chat_record_count')"
            align="right"
          >
            <template #default="{ row }">
              <span class="mr-8" v-if="!row.chat_record_count"> - </span>
            </template>
          </el-table-column>
          <el-table-column prop="star_num" align="right">
            <template #header>
              <div>
                <span>{{ $t('views.log.table.feedback.label') }}</span>
                <el-popover :width="190" trigger="click" :visible="popoverVisible">
                  <template #reference>
                    <el-button style="margin-top: -2px" :type="filter.min_star || filter.min_trample ? 'primary' : ''"
                      link @click="popoverVisible = !popoverVisible">
                      <el-icon>
                        <Filter />
                      </el-icon>
                    </el-button>
                  </template>
                  <div class="filter">
                    <div class="form-item mb-16">
                      <div @click.stop>
                        {{ $t('views.log.table.feedback.star') }} >=
                        <el-input-number v-model="filter.min_star" :min="0" :step="1" :value-on-clear="0"
                          controls-position="right" style="width: 100px" size="small" step-strictly />
                      </div>
                    </div>
                    <div class="form-item mb-16">
                      <div @click.stop>
                        {{ $t('views.log.table.feedback.trample') }} >=
                        <el-input-number v-model="filter.min_trample" :min="0" :step="1" :value-on-clear="0"
                          controls-position="right" style="width: 100px" size="small" step-strictly />
                      </div>
                    </div>
                  </div>
                  <div class="text-right">
                    <el-button size="small" @click="filterChange('clear')">{{
                    $t('common.clear')
                  }}</el-button>
                  <el-button type="primary" @click="filterChange" size="small">{{
                    $t('common.confirm')
                  }}</el-button>
                  </div>
                </el-popover>
              </div>
            </template>
            <template #default="{ row }">
              <span class="mr-8" v-if="!row.trample_num && !row.star_num"> - </span>
              <span class="mr-8" v-else>
                <span v-if="row.star_num">
                  <AppIcon iconName="app-like-color"></AppIcon>
                  {{ row.star_num }}
                </span>
                <span v-if="row.trample_num" class="ml-8">
                  <AppIcon iconName="app-oppose-color"></AppIcon>
                  {{ row.trample_num }}
                </span>
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="mark_sum" :label="$t('views.log.table.mark')" align="right" >
            <template #default="{ row }">
              <span class="mr-8" v-if="!row.mark_sum"> - </span>
            </template>
          </el-table-column>
          <el-table-column prop="asker" :label="$t('views.log.table.user')">
            <template #default="{ row }">
              {{ row.asker?.user_name }}
            </template>
          </el-table-column>
          <el-table-column label="API用户" width="180" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.api_key_name || "-" }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('views.log.table.recenTimes')" width="180">
            <template #default="{ row }">
              {{ datetimeFormat(row.update_time) }}
            </template>
          </el-table-column>

          <!-- <el-table-column label="操作" width="70" align="left">
          <template #default="{ row }">
            {{ datetimeFormat(row.update_time) }}
          </template>
        </el-table-column> -->
        </app-table>
      </div>
      <ChatRecordDrawer :next="nextChatRecord" :pre="preChatRecord" ref="ChatRecordRef" v-model:chatId="currentChatId"
        v-model:currentAbstract="currentAbstract" :application="detail" :pre_disable="pre_disable"
        :next_disable="next_disable" @refresh="refresh" />
      <el-dialog title="清除策略" v-model="dialogVisible" width="25%" :close-on-click-modal="false"
        :close-on-press-escape="false" modal-class="clear-modal">
        <span>删除</span>
        <el-input-number v-model="days" controls-position="right" min="1" max="100000" :value-on-clear="0" step-strictly
          style="width: 110px; margin-left: 8px; margin-right: 8px"></el-input-number>
        <span>天之前的对话记录</span>
        <template #footer>
          <div class="dialog-footer">
            <el-button @click="dialogVisible = false">{{ $t('layout.topbar.avatar.dialog.cancel') }}
            </el-button>
            <el-button type="primary" @click="saveCleanTime">
              {{ $t('layout.topbar.avatar.dialog.save') }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <el-dialog title="添加至知识库" v-model="documentDialogVisible" width="50%" :close-on-click-modal="false"
        :close-on-press-escape="false">
        <el-form ref="formRef" :model="form" label-position="left" label-width="7em" require-asterisk-position="left"
          :rules="rules" @submit.prevent>
          <el-form-item label="选择知识库:" prop="dataset_id">
            <el-select v-model="form.dataset_id" filterable placeholder="请选择知识库" :loading="optionLoading"
              @change="changeDataset">
              <el-option v-for="item in datasetList" :key="item.id" :label="item.name" :value="item.id">
                <span class="flex align-center">
                  <AppAvatar v-if="!item.dataset_id && item.type === '1'" class="mr-12 avatar-purple" shape="square"
                    :size="24">
                    <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  <AppAvatar v-else-if="!item.dataset_id && item.type === '0'" class="mr-12 avatar-blue" shape="square"
                    :size="24">
                    <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                  </AppAvatar>
                  {{ item.name }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="保存至文档:" prop="document_id">
            <el-select v-model="form.document_id" filterable placeholder="请选择文档" :loading="optionLoading"
              @change="changeDocument">
              <el-option v-for="item in documentList" :key="item.id" :label="item.name" :value="item.id">
                {{ item.name }}
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click.prevent="documentDialogVisible = false"> 取消 </el-button>
            <el-button type="primary" @click="submitForm(formRef)" :loading="documentLoading">
              保存
            </el-button>
          </span>
        </template>
      </el-dialog>
    </LayoutContainer>
  </div>

</template>
<script setup lang="ts">

import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import ChatRecordDrawer from './component/ChatRecordDrawer.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import logApi from '@/api/log'
import { beforeDay, datetimeFormat, nowDate } from '@/utils/time'
import useStore from '@/stores'
import type { Dict } from '@/api/type/common'
import { t } from '@/locales'
import type { FormInstance, FormRules } from 'element-plus'
import { ElTable } from 'element-plus'
import overviewApi from '@/api/application-overview'

const { application, log, document, user } = useStore()
const route = useRoute()
const {
  params: { id }
} = route as any

const emit = defineEmits(['refresh'])
const formRef = ref()

const dayOptions = [
  {
    value: 7,
    // @ts-ignore
    label: t('views.applicationOverview.monitor.pastDayOptions.past7Days') // 使用 t 方法来国际化显示文本
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
const daterangeValue = ref<any>('');
// 提交日期时间
const daterange = ref({
  start_time: '',
  end_time: ''
})

const multipleTableRef = ref<InstanceType<typeof ElTable>>()
const multipleSelection = ref<any[]>([])

const ChatRecordRef = ref()
const loading = ref(false)
const documentLoading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const dialogVisible = ref(false)
const documentDialogVisible = ref(false)
const days = ref<number>(180)
const tableData = ref<any[]>([])
const tableIndexMap = computed<Dict<number>>(() => {
  return tableData.value
    .map((row, index) => ({
      [row.id]: index
    }))
    .reduce((pre, next) => ({ ...pre, ...next }), {})
})
const history_day = ref<number | string>(7)

const isDay7 = computed(() => {
  return history_day.value === 7;
});
const isDay30 = computed(() => {
  return history_day.value === 30;
});
const isDay90 = computed(() => {
  return history_day.value === 90;
});

const apiKeyId = ref('')
const apiKeyList = ref<any[]>([])
const search = ref('')
const detail = ref<any>(null)

const currentChatId = ref<string>('')
const currentAbstract = ref<string>('')
const popoverVisible = ref(false)
const defaultFilter = {
  min_star: 0,
  min_trample: 0,
  comparer: 'and'
}
const filter = ref<any>({
  min_star: 0,
  min_trample: 0,
  comparer: 'and'
})

const form = ref<any>({
  dataset_id: '',
  document_id: ''
})

const rules = reactive<FormRules>({
  dataset_id: [
    { required: true, message: t('views.log.selectDatasetPlaceholder'), trigger: 'change' }
  ],
  document_id: [
    {
      required: true,
      message: t('views.log.documentPlaceholder'),
      trigger: 'change'
    }
  ]
})

const optionLoading = ref(false)
const documentList = ref<any[]>([])

function filterChange(val: string) {
  if (val === 'clear') {
    filter.value = cloneDeep(defaultFilter)
  }
  getList()
  popoverVisible.value = false
}

/**
 * 下一页
 */
const nextChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] + 1
  if (index >= tableData.value.length) {
    if (
      index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
      paginationConfig.total - 1
    ) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page + 1
    getList().then(() => {
      index = 0
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}
const pre_disable = computed(() => {
  let index = tableIndexMap.value[currentChatId.value] - 1
  return index < 0 && paginationConfig.current_page <= 1
})

const next_disable = computed(() => {
  let index = tableIndexMap.value[currentChatId.value] + 1
  return (
    index >= tableData.value.length &&
    index + (paginationConfig.current_page - 1) * paginationConfig.page_size >=
    paginationConfig.total - 1
  )
})
/**
 * 上一页
 */
const preChatRecord = () => {
  let index = tableIndexMap.value[currentChatId.value] - 1

  if (index < 0) {
    if (paginationConfig.current_page <= 1) {
      return
    }
    paginationConfig.current_page = paginationConfig.current_page - 1
    getList().then(() => {
      index = paginationConfig.page_size - 1
      currentChatId.value = tableData.value[index].id
      currentAbstract.value = tableData.value[index].abstract
    })
  } else {
    currentChatId.value = tableData.value[index].id
    currentAbstract.value = tableData.value[index].abstract
  }
}

function rowClickHandle(row: any, column?: any) {
  if (column && column.type === 'selection') {
    return
  }
  currentChatId.value = row.id
  currentAbstract.value = row.abstract
  ChatRecordRef.value.open()
}

const setRowClass = ({ row }: any) => {
  return currentChatId.value === row?.id ? 'highlight' : ''
}

const handleSelectionChange = (val: any[]) => {
  multipleSelection.value = val
}

// function deleteLog(row: any) {
//   MsgConfirm(`是否删除对话：${row.abstract} ?`, `删除后无法恢复，请谨慎操作。`, {
//     confirmButtonText: t('common.delete'),
//     confirmButtonClass: 'danger'
//   })
//     .then(() => {
//       loading.value = true
//       logApi.delChatLog(id as string, row.id, loading).then(() => {
//         MsgSuccess(t('common.deleteSuccess'))
//         getList()
//       })
//     })
//     .catch(() => {})
// }

function getApiKeyList() {
  overviewApi.getAPIKey(id as string, loading).then((res) => {
    apiKeyList.value = res.data
  })
}

function getList() {
  let obj: any = {
    start_time: daterange.value.start_time,
    end_time: daterange.value.end_time,
    ...filter.value
  }
  if (search.value) {
    obj = { ...obj, abstract: search.value}
  }
  if (apiKeyId.value) {
    obj = { ...obj, api_key_id: apiKeyId.value }
  }
  return log.asyncGetChatLog(id as string, paginationConfig, obj, loading).then((res: any) => {
    tableData.value = res.data.records
    if (currentChatId.value) {
      currentChatId.value = tableData.value[0]?.id
    }
    paginationConfig.total = res.data.total
  })
}

function getDetail(isLoading = false) {
  application
    .asyncGetApplicationDetail(id as string, isLoading ? loading : undefined)
    .then((res: any) => {
      detail.value = res.data
      days.value = res.data.clean_time
    })
}

const exportLog = () => {
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  if (detail.value) {
    let obj: any = {
      start_time: daterange.value.start_time,
      end_time: daterange.value.end_time,
      ...filter.value
    }
    if (search.value) {
      obj = { ...obj, abstract: search.value }
    }

    logApi.exportChatLog(detail.value.id, detail.value.name, obj, { select_ids: arr }, loading)
  }
}

function refresh() {
  getList()
}

function changeDayRangeHandle(val: string) {
  daterange.value.start_time = val[0]
  daterange.value.end_time = val[1]
  getList()
}

function changeDayHandle(val: number | string) {
  history_day.value = val;
  if (val !== 'other') {
    daterange.value.start_time = beforeDay(val);
    daterange.value.end_time = nowDate;

    daterangeValue.value = [daterange.value.start_time, daterange.value.end_time];

    getList()
  }
}

function saveCleanTime() {
  const obj = {
    clean_time: days.value
  }
  application
    .asyncPutApplication(id as string, obj, loading)
    .then(() => {
      MsgSuccess(t('common.saveSuccess'))
      dialogVisible.value = false
      getDetail(true)
    })
    .catch(() => {
      dialogVisible.value = false
    })
}

function changeDataset(dataset_id: string) {
  localStorage.setItem(id + 'chat_dataset_id', dataset_id)
  form.value.document_id = ''
  getDocument(dataset_id)
}

function changeDocument(document_id: string) {
  localStorage.setItem(id + 'chat_document_id', document_id)
}

const datasetList = ref<any[]>([])

function getDataset() {
  application.asyncGetApplicationDataset(id, documentLoading).then((res: any) => {
    datasetList.value = res.data
    if (localStorage.getItem(id + 'chat_dataset_id')) {
      form.value.dataset_id = localStorage.getItem(id + 'chat_dataset_id') as string
      if (!datasetList.value.find((v) => v.id === form.value.dataset_id)) {
        form.value.dataset_id = ''
        form.value.document_id = ''
      } else {
        getDocument(form.value.dataset_id)
      }
    }
  })
}

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  const arr: string[] = []
  multipleSelection.value.map((v) => {
    if (v) {
      arr.push(v.id)
    }
  })
  await formEl.validate((valid) => {
    if (valid) {
      const obj = {
        document_id: form.value.document_id,
        dataset_id: form.value.dataset_id,
        chat_ids: arr
      }
      logApi.postChatRecordLog(id, form.value.dataset_id, obj, documentLoading).then((res: any) => {
        multipleTableRef.value?.clearSelection()
        documentDialogVisible.value = false
      })
    }
  })
}

function getDocument(dataset_id: string) {
  document.asyncGetAllDocument(dataset_id, documentLoading).then((res: any) => {
    documentList.value = res.data
    if (localStorage.getItem(id + 'chat_document_id')) {
      form.value.document_id = localStorage.getItem(id + 'chat_document_id') as string
    }
    if (!documentList.value.find((v) => v.id === form.value.document_id)) {
      form.value.document_id = ''
    }
  })
}

function openDocumentDialog() {
  getDataset()
  formRef.value?.clearValidate()
  documentDialogVisible.value = true
}

onMounted(() => {
  getApiKeyList()
  changeDayHandle(history_day.value)
  getDetail()
})
</script>
<style lang="scss" scoped>
.log-table {
  :deep(tr) {
    cursor: pointer;
  }
}

.custom-log {
  width: 100%;
  height: 100%;
  position: relative;
  box-sizing: border-box;
  padding: 20px;

  .table {
    height: 100%;
    position: relative;
    box-sizing: border-box;
    padding: 0 20px 20px 20px;

    .condition {
      height: 116px;
      width: 100%;
      position: relative;
    }
  }
}
</style>
<style lang="scss">
.custom-log {

  .content-container {
    box-sizing: border-box;
    background-color: var(--app-view-bg-color);
    padding: 0;
    height: 100%;

    .content-container__header {
      height: 56px;
      line-height: 56px;
      position: relative;
      padding: 0 var(--app-view-padding);
      border-bottom: 1px solid #E9ECF2;
      font-weight: 500;
      font-size: 18px;
      color: #223355;
    }

    > .el-scrollbar {
      height: calc(100% - 56px);

      .el-scrollbar__view {
        height: 100%;

        .content-container__main {
          height: 100%;
        }
      }
    }
  }

  .table {
    .condition {
      .time {
        height: 60px;
        line-height: 60px;
        position: relative;
      }

      .el-date-editor {
        flex-grow: unset !important;
        margin-right: 20px;
      }

      .btns {
        height: 56px;
        line-height: 56px;
        position: relative;

        .el-input {
          .el-input__wrapper {
            border-radius: 15px;
          }
        }
      }
    }

    .app-table {
      height: calc(100% - 116px);
      position: relative;
      display: flex;
      flex-direction: column;

      .el-table--fit {
        flex: 1;
        width: 100%;

        .el-table__body-wrapper {
          overflow-y: auto !important;
        }
      }

      .app-table__pagination {}
    }
  }
}

.clear-modal {
  .el-dialog {
    &__body {
      padding-bottom: 20px !important;
    }
  }
}
</style>