<template>
  <el-card shadow="never" class="service-card">
    <template #header>
      <div class="card-header">
        <h3 class="text-lg font-bold">MCP服务发布</h3>
        <div class="service-actions" v-if="!loadingServices">
          <span class="mr-3 text-gray-600">服务数量: <a>{{ services.length }}</a></span>
          <el-button @click="handlePublishService()">
            发布内置服务
          </el-button>
        </div>
      </div>
    </template>

    <div class="service-content">
      <div v-if="loadingServices" class="text-center py-2">
        <el-skeleton :rows="1" animated/>
      </div>
      <div v-else-if="services.length === 0" class="text-center py-4 flex-1 flex items-center justify-center">
        <el-empty description="暂无服务" :image-size="60">
          <template #description>
            <p class="text-gray-500">还没有发布服务，点击上方按钮发布</p>
          </template>
        </el-empty>
      </div>
      <div v-else class="service-table-container">
        <el-table :data="services" style="width: 100%" size="small" class="service-table" max-height="198px"
                  :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266', fontWeight: 'bold' }">
          <el-table-column type="index" label="序号" width="60" align="center">
            <template #default="scope">
              {{ scope.$index + 1 }}
            </template>
          </el-table-column>
          <el-table-column label="服务名称" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.name }}
            </template>
          </el-table-column>
          <el-table-column label="创建时间" show-overflow-tooltip>
            <template #default="{row}">
              {{ row.created_at }}
            </template>
          </el-table-column>
          <el-table-column prop="sse_url" label="SSE URL" show-overflow-tooltip>
            <template #default="{row}">
              {{ row.sse_url }}
            </template>
          </el-table-column>
          <el-table-column prop="is_public" label="访问权限">
            <template #default="scope">
              <el-tag :type="scope.row.is_public ? 'success' : 'warning'" size="small">
                {{ scope.row.is_public ? '公开' : '私有' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)" size="small">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="{row}">
              <div class="inline">
                <el-dropdown trigger="click" class="mr-8">
                  <a>复制</a>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit_app">
                        <a @click.stop="copyUrl(row.sse_url)">
                          <el-icon>
                            <DocumentCopy/>
                          </el-icon>
                          复制URL到剪贴板</a>
                      </el-dropdown-item>
                      <el-dropdown-item>
                        <a @click.stop="copyAsEgovakbUrl(row.sse_url)">
                          <el-icon>
                            <DocumentCopy/>
                          </el-icon>
                          复制egovakb格式</a>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
                <el-dropdown trigger="click">
                  <a>更多</a>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit_app">
                        <a @click.stop="viewServiceParams(row)" class="action-button">
                          <el-icon>
                            <Setting/>
                          </el-icon>
                          <span>参数</span>
                        </a>
                      </el-dropdown-item>

                      <el-dropdown-item command="start_app">

                        <a v-if="row.status !== 'running'" @click.stop="handleStartService(row.service_uuid)"
                           class="action-button">
                          <el-icon>
                            <VideoPlay/>
                          </el-icon>
                          <span>启动</span>
                        </a>

                        <a v-if="row.status === 'running'" @click.stop="handleStopService(row.service_uuid)"
                           class="action-button">
                          <el-icon>
                            <VideoPause/>
                          </el-icon>
                          <span>停止</span>
                        </a>

                      </el-dropdown-item>

                      <el-dropdown-item>
                        <a @click.stop="handleUninstallService(row.service_uuid)" class="action-button">
                          <el-icon>
                            <Delete/>
                          </el-icon>
                          <span>卸载</span>
                        </a>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </el-card>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits } from 'vue'
import { DocumentCopy, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { copyTextToClipboard } from '@/utils/copy'
import type { McpServiceInfo } from '@/api/type/mcp-service'

const props = defineProps<{
  moduleId: number
  services: McpServiceInfo[]
  loadingServices: boolean
}>()

const emit = defineEmits<{
  (e: 'publishService'): void
  (e: 'uninstallService', uuid: string): void
  (e: 'stopService', uuid: string): void
  (e: 'startService', uuid: string): void
  (e: 'viewServiceParams', service: McpServiceInfo): void
}>()

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'success'
    case 'stopped':
      return 'warning'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'stopped':
      return '已停止'
    case 'error':
      return '错误'
    default:
      return status
  }
}

// 复制URL到剪贴板
const copyUrl = (url: string) => {
  copyTextToClipboard(url, 'URL已复制到剪贴板')
}

// 复制为egovakb格式的URL
const copyAsEgovakbUrl = (url: string) => {
  // 创建egovakb格式的JSON
  const egovakbFormat = JSON.stringify({
    'mcp-sse': {
      'url': url,
      'transport': 'sse'
    }
  }, null, 2)

  // 复制到剪贴板
  copyTextToClipboard(egovakbFormat, 'egovakb格式URL已复制到剪贴板')
}

// 处理发布服务
const handlePublishService = () => {
  emit('publishService')
}

// 卸载服务
const handleUninstallService = (serviceUuid: string) => {
  emit('uninstallService', serviceUuid)
}

// 停止服务
const handleStopService = (serviceUuid: string) => {
  emit('stopService', serviceUuid)
}

// 启动服务
const handleStartService = (serviceUuid: string) => {
  emit('startService', serviceUuid)
}

// 查看服务参数
const viewServiceParams = (service: McpServiceInfo) => {
  emit('viewServiceParams', service)
}
</script>

<style lang="scss">
.service-card {
  border-radius: 0px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  //background: linear-gradient(135deg, #ffffff, #f8f9ff);
  height: 100%;
  display: flex;
  flex-direction: column;

  .el-card__header {
    width: 100%;
    height: 56px;
    position: relative;
    padding: 0 var(--el-card-padding);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-header {
      width: 100%;
      margin-bottom: 0;
      display: flex;
      align-items: center;

      h3 {
        font-size: 14px;
        color: #081126;
      }

      a {
        color: #3388ff;
      }
    }
  }

  .el-card__body {
    .inline {
      display: flex;
      flex-direction: row;
      align-items: center;

      a {
        line-height: 14px;
        color: #3388FF;
      }
    }
  }
}

.service-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.service-table-container {
  flex: 1;
  overflow: auto;
}

.service-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-actions {
  display: flex;
  align-items: center;
}

.service-table {
  margin-top: 0px;
}
</style> 