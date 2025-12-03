<template>
  <div class='statistic-page'>
    <LayoutContainer >
      <div class="p-24">
        <!-- 搜索区域美化 -->
        <div class="search-section mb-16 p-16 bg-white rounded-lg">
          <div class="flex-between">
            <div class="flex-start">
              <el-select 
                v-model="dimension" 
                :placeholder="$t('views.statistics.selectDimension')"
                class="w-160 mr-12"
                @change="searchHandle"
              >
                <el-option 
                  :label="$t('views.statistics.userDimension')" 
                  value="user" 
                />
                <el-option 
                  :label="$t('views.statistics.groupDimension')" 
                  value="group" 
                />
              </el-select>
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                :start-placeholder="$t('views.statistics.startTime')"
                :end-placeholder="$t('views.statistics.endTime')"
                value-format="YYYY-MM-DD HH:mm:ss"
                format="YYYY-MM-DD HH:mm:ss"
                clearable
                :shortcuts="shortcuts"
              />

            </div>
            <div>
              <el-button type="primary" class="ml-12" @click="getList">
                <el-icon class='mr-4'><Search /></el-icon>
                {{ $t('common.query') }}
              </el-button>
              <el-button type="success" @click="exportData">
                <el-icon class='mr-4'><Download /></el-icon>
                {{ $t('common.export') }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 表格美化 -->
        <el-card shadow="never">
          <app-table
            :data="tableData"
            v-loading="loading"
            :border="true"
            stripe
            class="statistic-table"
          >
            <el-table-column :label="$t('common.index')">
                <template #default="{ $index }">
                    {{ $index + 1}}
                </template>
            </el-table-column>
            <el-table-column 
              :prop="dimension === 'user' ? 'username' : 'group_name'" 
              :label="dimension === 'user' ? $t('views.user.userForm.form.username.label') : $t('views.statistics.groupName')" 
            />
            <el-table-column 
              v-if="dimension === 'user'"
              prop="nick_name" 
              :label="$t('views.user.userForm.form.nick_name.label')" 
            />
            <el-table-column 
              v-if="dimension === 'group'"
              prop="member_count" 
              :label="$t('views.statistics.memberCount')" 
            />
            <el-table-column :label="$t('views.statistics.appCount')" sortable :sort-method="sortByTotalApp">
              <template #default="{ row }">
                <div class="count-info">
                  <div class="created">
                    <span class="label">{{ $t('views.statistics.created') }}:</span>
                    <span class="value">{{ row.app_created_count }}</span>
                  </div>
                  <div class="updated">
                    <span class="label">{{ $t('views.statistics.updated') }}:</span>
                    <span class="value">{{ row.app_updated_count }}</span>
                  </div>
                  <div class="total">
                    <span class="label">{{ $t('common.total') }}:</span>
                    <span class="value">{{ row.app_created_count + row.app_updated_count }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.datasetCount')" sortable :sort-method="sortByTotalDataset">
              <template #default="{ row }">
                <div class="count-info">
                  <div class="created">
                    <span class="label">{{ $t('views.statistics.created') }}:</span>
                    <span class="value">{{ row.dataset_created_count }}</span>
                  </div>
                  <div class="updated">
                    <span class="label">{{ $t('views.statistics.updated') }}:</span>
                    <span class="value">{{ row.dataset_updated_count }}</span>
                  </div>
                  <div class="total">
                    <span class="label">{{ $t('common.total') }}:</span>
                    <span class="value">{{ row.dataset_created_count + row.dataset_updated_count }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.documentCount')" sortable :sort-method="sortByTotalDocument">
              <template #default="{ row }">
                <div class="count-info">
                  <div class="created">
                    <span class="label">{{ $t('views.statistics.created') }}:</span>
                    <span class="value">{{ row.document_created_count }}</span>
                  </div>
                  <div class="updated">
                    <span class="label">{{ $t('views.statistics.updated') }}:</span>
                    <span class="value">{{ row.document_updated_count }}</span>
                  </div>
                  <div class="total">
                    <span class="label">{{ $t('common.total') }}:</span>
                    <span class="value">{{ row.document_created_count + row.document_updated_count }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.operation')" width="80" fixed="right">
              <template #default="{ row }">
                <el-button 
                  v-if="dimension === 'user'"
                  type="primary" 
                  link
                  @click="showDetail(row)"
                >
                  {{ $t('common.detail') }}
                </el-button>
              </template>
            </el-table-column>
          </app-table>
          
          <!-- 分页组件 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>
    </LayoutContainer>

    <!-- 添加详情对话框组件 -->
    <el-dialog
      v-model="detailVisible"
      :title="$t('views.statistics.userDetail')"
      width="800px"
    >
      <div v-if="currentDetail" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('views.user.userForm.form.username.label')">
            {{ currentDetail.username }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('views.user.userForm.form.nick_name.label')">
            {{ currentDetail.nick_name }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h3>{{ $t('views.statistics.appDetail') }}</h3>
          <div class="detail-summary">
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.created') }}:</span>
              <span class="value created">{{ getCreatedCount(currentDetail.apps) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.updated') }}:</span>
              <span class="value updated">{{ getUpdatedCount(currentDetail.apps) }}</span>
            </div>
          </div>
          <el-table :data="currentDetail.apps" border stripe>
            <el-table-column prop="name" :label="$t('views.statistics.name')" />
            <el-table-column :label="$t('views.statistics.status')" width="150">
              <template #default="{ row }">
                <div class="status-tags">
                  <el-tag v-if="row.is_created" type="success" size="small">{{ $t('views.statistics.created') }}</el-tag>
                  <el-tag v-if="row.is_updated" type="primary" size="small">{{ $t('views.statistics.updated') }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.createTime')">
              <template #default="{ row }">
                <div v-if="row.is_created" class="time-info">
                {{ datetimeFormat(row.create_time) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.updateTime')">
              <template #default="{ row }">
                <div v-if="row.is_updated" class="time-info">
                  {{ datetimeFormat(row.update_time) }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-section">
          <h3>{{ $t('views.statistics.datasetDetail') }}</h3>
          <div class="detail-summary">
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.created') }}:</span>
              <span class="value created">{{ getCreatedCount(currentDetail.datasets) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.updated') }}:</span>
              <span class="value updated">{{ getUpdatedCount(currentDetail.datasets) }}</span>
            </div>
          </div>
          <el-table :data="currentDetail.datasets" border stripe>
            <el-table-column prop="name" :label="$t('views.statistics.name')" />
            <el-table-column :label="$t('views.statistics.status')" width="150">
              <template #default="{ row }">
                <div class="status-tags">
                  <el-tag v-if="row.is_created" type="success" size="small">{{ $t('views.statistics.created') }}</el-tag>
                  <el-tag v-if="row.is_updated" type="primary" size="small">{{ $t('views.statistics.updated') }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.createTime')">
              <template #default="{ row }">
                <div v-if="row.is_created" class="time-info">
                {{ datetimeFormat(row.create_time) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.updateTime')">
              <template #default="{ row }">
                <div v-if="row.is_updated" class="time-info">
                  {{ datetimeFormat(row.update_time) }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-section">
          <h3>{{ $t('views.statistics.documentDetail') }}</h3>
          <div class="detail-summary">
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.created') }}:</span>
              <span class="value created">{{ getCreatedCount(currentDetail.documents) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">{{ $t('views.statistics.updated') }}:</span>
              <span class="value updated">{{ getUpdatedCount(currentDetail.documents) }}</span>
            </div>
          </div>
          <el-table :data="currentDetail.documents" border stripe>
            <el-table-column prop="name" :label="$t('views.statistics.name')" />
            <el-table-column :label="$t('views.statistics.status')" width="150">
              <template #default="{ row }">
                <div class="status-tags">
                  <el-tag v-if="row.is_created" type="success" size="small">{{ $t('views.statistics.created') }}</el-tag>
                  <el-tag v-if="row.is_updated" type="primary" size="small">{{ $t('views.statistics.updated') }}</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.createTime')">
              <template #default="{ row }">
                <div v-if="row.is_created" class="time-info">
                {{ datetimeFormat(row.create_time) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.statistics.updateTime')">
              <template #default="{ row }">
                <div v-if="row.is_updated" class="time-info">
                  {{ datetimeFormat(row.update_time) }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import statisticsApi from '@/api/statistics'
import type { StatisticsData, StatisticsResponse } from '@/api/statistics'
import "@/layout/layout-template/index.scss"
import { useI18n } from 'vue-i18n'
import { Platform, DataLine, Document, Search, Download } from '@element-plus/icons-vue'
import { datetimeFormat } from '@/utils/time'

const { t } = useI18n()
const loading = ref(false)
const tableData = ref<StatisticsData[]>([])
const searchValue = ref('')
const dimension = ref<'user' | 'group'>('user')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 设置默认时间范围为最近一周
const end = new Date()
const start = new Date()
start.setTime(start.getTime() - 3600 * 1000 * 24 * 3)

// 修复时区问题：将UTC时间转换为本地时间
const formatLocalDateTime = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const dateRange = ref<[string, string] | null>([
  formatLocalDateTime(start),
  formatLocalDateTime(end)
])

// 修改总计统计数据的结构
const totalStats = ref({
  appsCreated: 0,
  appsUpdated: 0,
  datasetsCreated: 0,
  datasetsUpdated: 0,
  documentsCreated: 0,
  documentsUpdated: 0
})

// 将快捷选项提取为变量
const shortcuts = [
  {
    text: '今天',
    value: () => {
      const start = new Date(new Date().setHours(0, 0, 0, 0))
      const end = new Date(new Date().setHours(23, 59, 59, 999))
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  },
  {
    text: '昨天',
    value: () => {
      const start = new Date(new Date().setHours(0, 0, 0, 0))
      const end = new Date(new Date().setHours(23, 59, 59, 999))
      start.setTime(start.getTime() - 3600 * 1000 * 24)
      end.setTime(end.getTime() - 3600 * 1000 * 24)
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  },
  {
    text: '前天',
    value: () => {
      const start = new Date(new Date().setHours(0, 0, 0, 0))
      const end = new Date(new Date().setHours(23, 59, 59, 999))
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 2)
      end.setTime(end.getTime() - 3600 * 1000 * 24 * 2)
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  },
  {
    text: '最近三天',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 3)
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  },
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [formatLocalDateTime(start), formatLocalDateTime(end)]
    },
  }
]

function handleDateChange(val: [string, string] | null) {
  if (val) {
    dateRange.value = val
  } else {
    dateRange.value = null
  }
}

function searchHandle() {
  getList()
}

function getList() {
  const params: any = {}
  
  if (searchValue.value) {
    params.username = searchValue.value
  }
  
  if (dateRange.value && dateRange.value.length === 2) {
    params.start_time = dateRange.value[0]
    params.end_time = dateRange.value[1]
  }

  params.dimension = dimension.value
  params.current_page = currentPage.value
  params.page_size = pageSize.value
  
  return statisticsApi.getStatistics(params, loading).then((res: any) => {
    const data: StatisticsResponse = res.data
    tableData.value = data.records
    total.value = data.total
    currentPage.value = data.current
    pageSize.value = data.size
    
    // 计算总计数据
    totalStats.value = {
      appsCreated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.app_created_count, 0),
      appsUpdated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.app_updated_count, 0),
      datasetsCreated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.dataset_created_count, 0),
      datasetsUpdated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.dataset_updated_count, 0),
      documentsCreated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.document_created_count, 0),
      documentsUpdated: data.records.reduce((sum: number, item: StatisticsData) => sum + item.document_updated_count, 0)
    }
  })
}

// 分页处理
function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  getList()
}

function handleCurrentChange(page: number) {
  currentPage.value = page
  getList()
}

// 添加排序方法
interface SortableRow {
  [key: string]: any;
}

// 根据创建数和更新数之和进行排序
function sortByTotal(a: SortableRow, b: SortableRow, type: string): number {
  const aTotal = a[`${type}_created_count`] + a[`${type}_updated_count`];
  const bTotal = b[`${type}_created_count`] + b[`${type}_updated_count`];
  return bTotal - aTotal; // 默认降序排列（从大到小）
}

// 添加具体的排序函数
function sortByTotalApp(a: SortableRow, b: SortableRow): number {
  return sortByTotal(a, b, 'app');
}

function sortByTotalDataset(a: SortableRow, b: SortableRow): number {
  return sortByTotal(a, b, 'dataset');
}

function sortByTotalDocument(a: SortableRow, b: SortableRow): number {
  return sortByTotal(a, b, 'document');
}

// 修改过滤器的类型定义
interface StatItem {
  name: string;
  create_time: string;
  update_time: string;
  is_created: boolean;
  is_updated: boolean;
}

// 添加详情对话框控制变量
const detailVisible = ref(false)

interface DetailData {
  username: string;
  nick_name: string;
  apps: StatItem[];
  datasets: StatItem[];
  documents: StatItem[];
}

const currentDetail = ref<DetailData | null>(null)

// 显示详情方法
const showDetail = async (row: any) => {
  const params = {
    username: row.username,
    start_time: dateRange.value?.[0],
    end_time: dateRange.value?.[1]
  }
  
  loading.value = true
  try {
    const res = await statisticsApi.getStatisticsDetail(params)
    currentDetail.value = res.data
    detailVisible.value = true
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 添加导出功能
function exportData() {
  // 准备CSV数据
  const headers = [
    dimension.value === 'user' ? t('views.user.userForm.form.username.label') : t('views.statistics.groupName'),
    dimension.value === 'user' ? t('views.user.userForm.form.nick_name.label') : t('views.statistics.memberCount'),
    `${t('views.statistics.appCount')} - ${t('views.statistics.created')}`,
    `${t('views.statistics.appCount')} - ${t('views.statistics.updated')}`,
    `${t('views.statistics.appCount')} - ${t('common.total')}`,
    `${t('views.statistics.datasetCount')} - ${t('views.statistics.created')}`,
    `${t('views.statistics.datasetCount')} - ${t('views.statistics.updated')}`,
    `${t('views.statistics.datasetCount')} - ${t('common.total')}`,
    `${t('views.statistics.documentCount')} - ${t('views.statistics.created')}`,
    `${t('views.statistics.documentCount')} - ${t('views.statistics.updated')}`,
    `${t('views.statistics.documentCount')} - ${t('common.total')}`,
  ].join(',');

  // 添加数据行
  const rows = tableData.value.map(item => {
    return [
      dimension.value === 'user' ? item.username : item.group_name,
      dimension.value === 'user' ? item.nick_name : item.member_count,
      item.app_created_count,
      item.app_updated_count,
      item.app_created_count + item.app_updated_count,
      item.dataset_created_count,
      item.dataset_updated_count,
      item.dataset_created_count + item.dataset_updated_count,
      item.document_created_count,
      item.document_updated_count,
      item.document_created_count + item.document_updated_count,
    ].join(',');
  });

  // 合并CSV内容
  const csvContent = [headers, ...rows].join('\n');
  
  // 创建Blob对象并下载
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  // 生成文件名：statistics_YYYY-MM-DD.csv
  const now = new Date();
  const date = now.toISOString().split('T')[0];
  const fileName = `statistics_${date}.csv`;
  
  link.href = url;
  link.setAttribute('download', fileName);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// 辅助函数：获取创建数量
function getCreatedCount(items: StatItem[] | undefined): number {
  if (!items) return 0;
  return items.filter(item => item.is_created).length;
}

// 辅助函数：获取更新数量
function getUpdatedCount(items: StatItem[] | undefined): number {
  if (!items) return 0;
  return items.filter(item => item.is_updated).length;
}

onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.statistics-card {
  .card-header {
    font-size: 16px;
    color: #606266;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }
  
  .card-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 8px;
    
    .stats-info {
      .created, .updated {
        margin-bottom: 8px;
        
        .label {
          font-size: 14px;
          color: #909399;
          margin-right: 8px;
        }
        
        .value {
          font-size: 20px;
          font-weight: bold;
        }
      }
      
      .created .value {
        color: #67C23A; // 绿色表示创建
      }
      
      .updated .value {
        color: #409EFF; // 蓝色表示更新
      }
    }
    
    .icon {
      font-size: 32px;
      color: #909399;
      opacity: 0.7;
    }
  }

  &:hover {
    .icon {
      color: #409EFF;
      opacity: 1;
    }
  }
}

.search-section {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.statistics-table {
  tr {
    cursor: pointer;
    &:hover {
      background-color: #f5f7fa;
    }
  }
}

.el-card {
  --el-card-padding: calc(var(--app-base-px)) !important;
}

.app-table {
  // height: calc(100% - 586px) !important;
}

.count-info {
  .created, .updated, .total {
    display: flex;
    align-items: center;
    margin: 4px 0;
    
    .label {
      color: #909399;
      margin-right: 8px;
    }
    
    .value {
      font-weight: bold;
    }
  }
  
  .created .value {
    color: #67C23A;
  }
  
  .updated .value {
    color: #409EFF;
  }
  
  .total .value {
    color: #E6A23C; // 橙色表示总计
  }
}

.detail-content {
  .detail-section {
    margin-top: 24px;
    
    h3 {
      margin-bottom: 16px;
      font-size: 16px;
      color: #606266;
    }
  }
}

.detail-section {
  .detail-summary {
    display: flex;
    gap: 24px;
    margin-bottom: 16px;
    
    .summary-item {
      display: flex;
      align-items: center;
      
      .label {
        color: #909399;
        margin-right: 8px;
      }
      
      .value {
        font-size: 16px;
        font-weight: bold;
        
        &.created {
          color: #67C23A;
        }
        
        &.updated {
          color: #409EFF;
        }
      }
    }
  }
  
  .status-tags {
    display: flex;
    gap: 8px;
  }
}

.time-info {
  display: flex;
  align-items: center;
  margin: 4px 0;
  
  .label {
    color: #909399;
    margin-right: 8px;
  }
  
  .value {
    color: #606266;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}
</style> 
<style lang="scss">
.content-container,.el-scrollbar__view,.content-container__main,.el-card__body {
  height: 100%;
  >.p-24 {
    height: 100%;
    box-sizing: border-box;
    >.el-card {
      height: calc(100% - 55px);
      position: relative;
      display: flex;
      flex-direction: column;
      
      .el-card__body {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        
        .app-table {
          flex: 1;
          overflow: hidden;
        }
        
        .pagination-container {
          flex-shrink: 0;
          margin-top: 20px;
          padding: 20px 0;
        }
      }
    }
  }
}

.statistic-table {
  height: 100% !important;
  .el-table__body-wrapper {
    flex: 1;
    overflow: auto;
  }
}

.statistic-page {
  height: 100%;
  padding: var(--app-view-padding) !important;
  box-sizing: border-box;
  .content-container {
    padding: 0 !important;
  }
}
</style>
