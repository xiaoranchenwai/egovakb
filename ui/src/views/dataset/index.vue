<template>
  <div class="full-container">
    <el-row :gutter="0">
      <el-col :span="expand ? 4 : 0" class="h-full">
        <div class="left-container">
          <GroupDrawer @update:selectedGroup="handleGroupSelect"></GroupDrawer>
        </div>
      </el-col>
      <el-col :span="expand ? 20 : 24" :class="{ expand: !expand }">
        <div class="toggle-btn" @click="onToggleShow">
          <el-icon>
            <CaretLeft v-if="expand" />
            <CaretRight v-else />
          </el-icon>
        </div>

        <div class="dataset-list-container">
          <div class="ds-list-contaier">
            <div class="flex-between condition">
              <div>
                <el-button round @click.stop='openCreateDialog' style="color:#3388FF;width:108px">
                  <el-icon>
                    <Plus />
                  </el-icon>
                  创建知识库
                </el-button>
                <el-button round @click.stop="openImportDialog" style="color:#3388FF;width:108px;margin-left:8px">
                  <el-icon>
                    <Upload />
                  </el-icon>
                  导入知识库
                </el-button>
              </div>
              <div class="flex-between condition">
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
                <el-input v-model="searchValue" @change="searchHandle"
                  :placeholder="$t('common.search')" 
                  class="w-240 combine-input" style="max-width: 240px" clearable >
                  <template #append>
                    <el-button :icon="Search" />
                  </template>
                </el-input>
              </div>
            </div>

            <el-tabs v-model='activeName' class='demo-tabs' @tab-click='onTabClick'>
              <el-tab-pane v-for='item in tabPanes' :label='item.label' :name='item.value'>
                <div class='content' v-loading.fullscreen.lock='paginationConfig.current_page === 1 && loading'>
                  <div class='abs'>
                    <InfiniteScroll :size="datasetList.length" :total="paginationConfig.total"
                      :page_size="paginationConfig.page_size" v-model:current_page="paginationConfig.current_page"
                      @load="getList" :loading="loading">
                      <el-row :gutter="15">
                        <template v-for="(item, index) in filteredDatasets" :key="index">
                          <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
                            <CardBox :title="item.name" :description="item.desc" class="application-card cursor"
                              @click="router.push({ path: `/dataset/${item.id}/document` })">
                              <template #icon>
                                <AppAvatar v-if="item.type === '1'" class="mr-8 avatar-purple" shape="square" :size="48">
                                  <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                                </AppAvatar>
                                <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="48">
                                  <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                                </AppAvatar>
                              </template>
                              <div class="status-tag">
                                <el-tag class="green-tag" v-if="item.type === '0'" style="height: 24px">{{ $t('views.dataset.general') }}</el-tag>
                                <el-tag class="orange-tag" v-else-if="item.type === '1'" type="warning"
                                  style="height: 24px">{{ $t('views.dataset.web') }}</el-tag>
                              </div>

                              <template #description>
                                <el-text line-clamp="3">
                                  {{ item.desc || item.problem_optimization_prompt }}
                                </el-text>
                              </template>

                              <div class='info flex-between'>
                                <div class="flex-between">
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
                                <div class="footer-content flex-between">
                                  <div class="ellipsis flex" style="max-width: fit-content;display: flex;">
                                    <span class="bold">{{ item?.document_count || 0 }}</span>
                                    <div>{{ $t('views.dataset.document_count') }}</div>
                                  
                                    <el-divider direction="vertical" style="margin: 0 5px"/>

                                    <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                                    {{ $t('common.character') }}
                                    <el-divider direction="vertical" style="margin: 0 5px"/>

                                    <span class="bold">{{ item?.application_mapping_count || 0 }}</span>
                                    <span :title="$t('views.dataset.relatedApp_count')">{{ $t('views.dataset.relatedApp_count') }}</span>
                                  </div>
                                  <div @click.stop>
                                    <el-dropdown trigger="click" popper-class="app-dropdown">
                                      <el-button text @click.stop>
                                        <el-icon>
                                          <MoreFilled color="#A8B4C8"/>
                                        </el-icon>
                                      </el-button>
                                      <template #dropdown>
                                        <el-dropdown-menu>
                                          <el-dropdown-item
                                            icon="Refresh"
                                            @click.stop="syncDataset(item)"
                                            v-if="item.type === '1'"
                                            >{{ $t('views.dataset.setting.sync') }}</el-dropdown-item
                                          >
                                          <el-dropdown-item @click="reEmbeddingDataset(item)">
                                            <AppIcon
                                              iconName="app-document-refresh"
                                              style="font-size: 16px"
                                            ></AppIcon>
                                            {{ $t('views.dataset.setting.vectorization') }}</el-dropdown-item
                                          >
                                          <el-dropdown-item
                                            icon="Connection"
                                            @click.stop="openGenerateDialog(item)"
                                            >{{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
                                          >
                                          <el-dropdown-item
                                            icon="Setting"
                                            @click.stop="router.push({ path: `/dataset/${item.id}/setting` })"
                                          >
                                            {{ $t('common.setting') }}</el-dropdown-item
                                          >
                                          <el-dropdown-item @click.stop="export_dataset(item)">
                                            <AppIcon iconName="app-export"></AppIcon
                                            >{{ $t('views.document.setting.export') }} Excel</el-dropdown-item
                                          >
                                          <!-- <el-dropdown-item @click.stop="export_zip_dataset(item)">
                                            <AppIcon iconName="app-export"></AppIcon
                                            >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                                          > -->
                                          <!-- <el-dropdown-item @click.stop="moveToGroup(item)">
                                            <AppIcon iconName="app-move"></AppIcon>移动到分组</el-dropdown-item> -->
                                          <el-dropdown-item icon="Delete" @click.stop="deleteDataset(item)">{{
                                            $t('common.delete')
                                          }}</el-dropdown-item>
                                        </el-dropdown-menu>
                                      </template>
                                    </el-dropdown>
                                  </div>
                                </div>
                              </template>
                            </CardBox>
                          </el-col>
                        </template>
                      </el-row>
                    </InfiniteScroll>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>

            <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
            <CreateDatasetDialog ref="CreateDatasetDialogRef" />
            <GenerateRelatedDialog ref="GenerateRelatedDialogRef" />
            <!-- 移动到分组对话框 -->
            <el-dialog
              v-model="moveDialogVisible"
              title="移动到分组"
              width="500px"
              destroy-on-close
            >
              <div v-loading="moveLoading">
                <el-form label-width="5em">
                  <el-form-item label="选择分组:">
                    <el-select 
                      v-model="selectedGroupId"
                      filterable
                      placeholder="请选择分组"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="group in availableGroups"
                        :key="group.id"
                        :label="group.name"
                        :value="group.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
              <template #footer>
                <el-button @click="moveDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="confirmMove" :loading="confirmMoveLoading">确定</el-button>
              </template>
            </el-dialog>

            <!-- 导入知识库对话框 -->
            <el-dialog
              v-model="importDialogVisible"
              title="导入知识库"
              width="520px"
              destroy-on-close
            >
              <div v-loading="importLoading">
                <el-form label-width="6em">
                  <el-form-item label="目标知识库">
                    <el-select
                      v-model="importDatasetId"
                      filterable
                      placeholder="请选择知识库"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="opt in allDatasetOptions"
                        :key="opt.value"
                        :label="opt.label"
                        :value="opt.value"
                      />
                    </el-select>
                    <div class="mt-8" style="color:#A8B4C8">不选择目标知识库将创建新的知识库</div>
                  </el-form-item>
                  <el-form-item label="选择文件">
                    <el-upload
                      action=""
                      :auto-upload="false"
                      drag
                      :limit="1"
                      :multiple="false"
                      accept=".xlsx"
                      :file-list="importFileList"
                      :on-change="onImportFileChange"
                      :on-remove="onUploadRemove"
                      :on-exceed="onUploadExceed"
                      style="width: 100%"
                    >
                      <div class="el-upload__text">将文件拖到此处，或点击上传</div>
                      <template #tip>
                        <div class="mt-8" style="color:#A8B4C8">仅支持由导出功能生成的 .xlsx 文件；一次仅可选择一个</div>
                      </template>
                    </el-upload>
                  </el-form-item>
                </el-form>
              </div>
              <template #footer>
                <el-button @click="importDialogVisible = false">取消</el-button>
                <el-button type="primary" :loading="importLoading" @click="confirmImport">上传并导入</el-button>
              </template>
            </el-dialog>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import SyncWebDialog from '@/views/dataset/component/SyncWebDialog.vue'
import CreateDatasetDialog from './component/CreateDatasetDialog.vue'
import GroupDrawer from './component/GroupDrawer.vue'
import datasetApi from '@/api/dataset'
import groupApi from '@/api/group'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import { numberFormat } from '@/utils/utils'
import { ValidType, ValidCount } from '@/enums/common'
import { datetimeFormat } from '@/utils/time'
import { t } from '@/locales'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import { ElMessage } from 'element-plus'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { Search, Upload } from '@element-plus/icons-vue';

const { user, common } = useStore()
const router = useRouter()

const CreateDatasetDialogRef = ref()
const SyncWebDialogRef = ref()
const loading = ref(false)
const datasetList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})
const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()
function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'dataset', row.id)
  }
}

const searchValue = ref('');
const expand = ref<boolean>(true);
const selectedGroup = ref<any>(null);

// 移动到分组相关
const moveDialogVisible = ref(false);
const moveLoading = ref(false);
const confirmMoveLoading = ref(false);
const selectedGroupId = ref('');
const availableGroups = ref<any[]>([]);
const datasetToMove = ref<any>(null);

const tabPanes = ref<Array<any>>([
  { label: '全部', value: 'all' },
  { label: '通用型', value: 'common' },
  { label: '高级应用', value: 'senior' }
])
const activeName = ref('all')

function onTabClick(tab: any, event: any) {
  console.log(tab.props.name)
}

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])

const selectUserId = ref('all')

// 根据分组和搜索关键字过滤知识库
const filteredDatasets = computed(() => {
  let datasets = datasetList.value
  
  // 按分组过滤
  if (selectedGroup.value) {
    if (selectedGroup.value.target_type === 'GROUP') {
      // 如果选择的是分组，显示该分组下的所有知识库
      const groupDatasets = selectedGroup.value.children?.filter((item: any) => item.target_type === 'DATASET') || []
      const datasetIds = groupDatasets.map((item: any) => item.target_id)
      datasets = datasets.filter(dataset => datasetIds.includes(dataset.id))
    } else if (selectedGroup.value.target_type === 'DATASET') {
      // 如果选择的是知识库，只显示该知识库
      datasets = datasets.filter(dataset => dataset.id === selectedGroup.value.target_id)
    }
  }
  
  return datasets
})

function onToggleShow() {
  expand.value = !expand.value;
}

function handleGroupSelect(group: any) {
  selectedGroup.value = group;
  // 重置分页
  paginationConfig.current_page = 1;
  datasetList.value = [];
  getList();
}

function openCreateDialog() {
  CreateDatasetDialogRef.value.open()
}

function refresh() {
  MsgSuccess(t('views.dataset.tip.syncSuccess'))
}

function reEmbeddingDataset(row: any) {
  datasetApi.putReEmbeddingDataset(row.id).then(() => {
    MsgSuccess(t('views.dataset.tip.vectorizationSuccess'))
  })
}

function syncDataset(row: any) {
  SyncWebDialogRef.value.open(row.id)
}

const export_dataset = (item: any) => {
  datasetApi.exportDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const export_zip_dataset = (item: any) => {
  datasetApi.exportZipDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}

function deleteDataset(row: any) {
  MsgConfirm(
    `${t('views.dataset.delete.confirmTitle')}${row.name} ?`,
    `${t('views.dataset.delete.confirmMessage1')} ${row.application_mapping_count} ${t('views.dataset.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.delDataset(row.id, loading).then(() => {
        const index = datasetList.value.findIndex((v) => v.id === row.id)
        datasetList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

// 移动知识库到分组
function moveToGroup(dataset: any) {
}

// 确认移动知识库到分组
function confirmMove() {
  if (!selectedGroupId.value || !datasetToMove.value) {
    ElMessage.warning('请选择分组');
    return;
  }
  
  confirmMoveLoading.value = true;
  
  groupApi.createGroupDetails({
    group: selectedGroupId.value,
    target_type: 'DATASET',
    target_id: datasetToMove.value.id
  }).then(() => {
    ElMessage.success('移动成功');
    moveDialogVisible.value = false;
    // 如果当前正在查看分组，则刷新数据
    if (selectedGroup.value) {
      datasetList.value = [];
      paginationConfig.current_page = 1;
      getList();
    }
  }).catch(error => {
    console.error('移动知识库失败', error);
    ElMessage.error('移动知识库失败');
  }).finally(() => {
    confirmMoveLoading.value = false;
  });
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'dataset', selectUserId.value)
  }
  datasetList.value = []
  paginationConfig.current_page = 1
  getList()
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value })
  }
  datasetApi.getDataset(paginationConfig, params, loading).then((res) => {
    res.data.records.forEach((item: any) => {
      if (item.username) {
        
      } else {
        if (user.userInfo && item.user_id === user.userInfo.id) {
          item.username = user.userInfo.username
        } else {
          item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
        }
      }
    })
    paginationConfig.total = res.data.total
    datasetList.value = [...datasetList.value, ...res.data.records]
  })
}

function getUserList() {
  applicationApi.getUserList('DATASET', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'dataset')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
      getList()
    }
  })
}

onMounted(() => {
  console.log('onMounted, dataset 1')
  getUserList()
  console.log('onMounted, dataset 2')
})

/**
 * 打开“导入知识库”对话框。
 * - 拉取全部知识库，供选择导入目标。
 * - 若当前在分组中选中了具体知识库，则预选中该知识库。
 */
const importDialogVisible = ref(false)
const importLoading = ref(false)
const importDatasetId = ref<string | null>(null)
const importFile = ref<File | null>(null)
const importFileList = ref<any[]>([])
const allDatasetOptions = ref<Array<{ label: string; value: string }>>([])

function openImportDialog() {
  importDialogVisible.value = true
  // 重置文件选择
  importFile.value = null
  importFileList.value = []
  datasetApi.getAllDataset(loading).then((res) => {
    allDatasetOptions.value = (res.data || []).map((d: any) => ({ label: d.name, value: d.id }))
    // 若当前选中了具体知识库，则预选中
    if (selectedGroup.value && selectedGroup.value.target_type === 'DATASET') {
      importDatasetId.value = selectedGroup.value.target_id
    }
  })
}

/**
 * el-upload 选择/拖拽文件事件处理。
 * - 回调参数为 (uploadFile, uploadFiles)
 * - 仅接受 .xlsx 文件；不符合时清空选择并提示。
 */
function onImportFileChange(uploadFile: any, uploadFiles: any[]) {
  const name: string = uploadFile?.name || uploadFile?.raw?.name || ''
  const isXlsx = !!name && name.toLowerCase().endsWith('.xlsx')
  if (!isXlsx) {
    ElMessage.warning('请选择 .xlsx 格式的文件')
    importFile.value = null
    importFileList.value = []
    return
  }
  importFile.value = uploadFile?.raw ?? null
  importFileList.value = uploadFiles?.slice(0, 1) || []
}

/**
 * el-upload 移除文件事件处理。
 */
function onUploadRemove() {
  importFile.value = null
  importFileList.value = []
}

/**
 * el-upload 超出文件数量限制事件处理。
 */
function onUploadExceed() {
  ElMessage.warning('一次只能选择一个文件')
}

/**
 * 执行知识库导入。
 * - 校验选择的目标知识库与文件。
 * - 使用 `datasetApi.importDataset` 上传文件并导入。
 * - 成功后关闭对话框并刷新列表。
 */
/**
 * 执行知识库导入。
 * - 若选择了目标知识库：仅导入 文档、分段、问题
 * - 若未选择目标知识库：创建新的知识库，名称为 dataset.name + 导入时间
 */
function confirmImport() {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的 Excel 文件')
    return
  }
  importLoading.value = true
  const promise = importDatasetId.value
    ? datasetApi.importDataset(importDatasetId.value, importFile.value, importLoading)
    : datasetApi.importDatasetNew(importFile.value, importLoading)
  promise
    .then((res) => {
      if (importDatasetId.value) {
        ElMessage.success('导入成功')
      } else {
        const name = res?.data?.dataset_name || ''
        ElMessage.success(`已创建新知识库「${name}」并导入成功`)
      }
      importDialogVisible.value = false
      // 刷新列表
      datasetList.value = []
      paginationConfig.current_page = 1
      getList()
    })
    .catch((err) => {
      console.error('导入知识库失败', err)
      ElMessage.error('导入知识库失败')
    })
    .finally(() => {
      importLoading.value = false
    })
}
</script>

<style lang="scss" scoped>
.full-container {
  width: 100%;
  height: 100%;
  position: relative;

  .el-row {
    height: 100%;

    .el-col {
      position: relative;
      transition: all 0.2s;
    }

    .el-col-24 {
      .icon {
        left: 0;
      }
    }
  }

  .left-container {
    width: 100%;
    height: 100%;
    position: relative;
    background-color: var(--app-view-bg-color);
  }

  .toggle-btn {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 64px;
    background: #A8B4C8;
    border-radius: 0 8px 8px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 10;
    color: #fff;

    &:hover {
      background: var(--el-color-primary);
    }
  }

  .demo-tabs {
    
  }

  .dataset-list-container {
    width: 100%;
    height: 100%;
    position: relative;
    box-sizing: border-box;
    padding: 20px;

    .ds-list-contaier {
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

    .delete-button {
      position: absolute;
      right: 12px;
      top: 15px;
      height: auto;
    }

    .footer-content {
      .bold {
        color: var(--app-text-color);
      }
    }

    :deep(.el-divider__text) {
      background: var(--app-layout-bg-color);
    }
  }
}

.expand {
  .dataset-list-container {
    .el-col-xl-6 {
      flex: 0 0 25%;
      max-width: 25%;
    }
  }
}

.ds-list-contaier {
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
            height: 62px;
            max-height: 62px;
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
      }
    }
  }

  .application-card {
    height: 250px;

    .status-tag {
      position: absolute;
      right: 20px;
      top: 30px;

      .green-tag {
        height: 24px !important;
        padding: 0 6px;
        background-color: #E6FFF4;
        color: #11C79B;
        border: none;
      }

      .orange-tag {
        @extend .green-tag;
        background-color: #FFF4E6;
        color: #FF6600;
      }
    }
  }
}

</style>

<style lang="scss">
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

  .card-footer {
    .el-button {
      &:hover {
        background-color: #F5F7FA !important;
      }
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

.combine-input {
  .el-input__wrapper {
    border-radius: 16px 0 0 16px !important;
    .el-input {
      --el-input-placeholder-color: #A8B4C8;
    }
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