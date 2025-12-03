<template>
  <el-card class="module-info-card" shadow="never">
    <template #header>
      <div class="card-header">
        <div class="flex-between ">
          <div class="flex">
            <h2 class="text-xl font-bold">{{ moduleInfo.name }}</h2>
          </div>
          <div>
            <el-button type="default" @click="showEditDialog" v-if="hasEditPermission">编辑</el-button>
            <el-button type="default" @click="handleDeleteModule"  v-if="hasEditPermission">删除</el-button>
            <el-text v-if="!hasEditPermission">
              <el-icon>
                <InfoFilled/>
              </el-icon>
              没有编辑权限，只能发布服务
            </el-text>
          </div>
        </div>
      </div>
    </template>
    <div class="flex items-start h-full flex-col">
      <div class="flex-1 w-full">
        <el-descriptions border :column="2" class="module-info-descriptions">
          <el-descriptions-item label="简介" class="description-item" :span="2">
            <el-tooltip :content="moduleInfo.description" placement="top" :show-after="200" max-width="400"
                        :enterable="false">
              <div class="description-content">
                {{ moduleInfo.description }}
              </div>
            </el-tooltip>
          </el-descriptions-item>
          <el-descriptions-item label="分类" :span="2">
            {{ moduleInfo.category_name }}
          </el-descriptions-item>
          <el-descriptions-item label="访问权限" :span="2">
            {{ moduleInfo.is_public ? '公开' : '私有' }}
          </el-descriptions-item>

          <el-descriptions-item label="创建人">
            {{ moduleInfo.author || moduleInfo.username }}
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ moduleInfo.version }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ moduleInfo.created_at }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ moduleInfo.updated_at }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </el-card>
</template>

<script lang="ts" setup>
import { defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import type { McpModuleInfo } from '@/api/type/mcp-square'

const props = defineProps<{
  moduleInfo: McpModuleInfo
  hasEditPermission: boolean
}>()

const emit = defineEmits<{
  (e: 'showEditDialog'): void
  (e: 'deleteModule'): void
}>()

const router = useRouter()

// 根据模块类型获取图标
function getModuleIcon(module: McpModuleInfo) {
  // 根据模块类型或名称返回不同的图标
  if (!module?.name) return 'Tools'

  if (module.name.toLowerCase().includes('tavily')) {
    return 'Search'
  } else if (module.name.toLowerCase().includes('fetch')) {
    return 'Link'
  } else if (module.name.toLowerCase().includes('github')) {
    return 'Platform'
  } else {
    return 'Tools'
  }
}

// 返回列表页
function goBack() {
  router.push('/mcp/marketplace')
}

// 显示编辑对话框
function showEditDialog() {
  emit('showEditDialog')
}

// 处理删除模块
function handleDeleteModule() {
  emit('deleteModule')
}
</script>

<style lang="scss">
.module-info-card {
  border-radius: 0px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid rgba(235, 235, 235, 0.8);
  transition: all 0.3s ease;
  overflow: hidden;
  //background: linear-gradient(135deg, #ffffff, #f8fcff);
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

    .card-header,.flex-between {
      width: 100%;
      margin-bottom: 0;
      h2 {
        font-size: 14px;
        color: #081126;
      }
    }
  }

  .el-card__body {

  }

  .el-button+.el-button {
    margin-left: 8px !important;
  }
}

.module-info-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12) !important;
  transform: translateY(-2px);
}

.description-content {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
  max-height: 3em;
}

.module-info-descriptions .el-descriptions__cell {
  min-width: 100px;
  max-width: 50%;
  word-break: break-word;
}

.module-info-descriptions .el-descriptions__label {
  border-color: #DDE1EB !important;
  font-weight: 400 !important;
}

.module-info-descriptions .el-descriptions__content {
  color: #223355;
}

.module-info-meta {
  background: rgba(245, 250, 255, 0.7);
  padding: 16px;
  border-radius: 12px;
  width: 100%;
  border: 1px solid rgba(220, 240, 255, 0.8);
  margin-top: auto;
}

.module-meta-item {
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.module-meta-item:last-child {
  margin-bottom: 0;
}

.module-meta-item strong {
  color: #303133;
  margin-right: 8px;
  min-width: 70px;
}

.return-btn {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.tag-item {
  border-radius: 20px;
  padding: 0 12px;
  height: 24px;
  line-height: 22px;
  margin-right: 8px;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.tag-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}
</style>