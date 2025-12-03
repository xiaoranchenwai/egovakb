<template>
  <div class="paragraph-chunk-container">
    <div v-if="chunkList && chunkList.length > 0" class="chunks-container">
      <div 
        v-for="(chunk, index) in chunkList" 
        :key="chunk.id" 
        class="chunk-item"
        :class="{ 
          'chunk-hover': hoveredChunkId === chunk.id,
          'chunk-hit': isChunkHighlighted(chunk),
          'editing': editingChunkId === chunk.id
        }"
        @mouseenter="handleHover(chunk.id, true)"
        @mouseleave="handleHover(chunk.id, false)"
        style="position: relative;"
      >
        <div 
          v-if="hoveredChunkId === chunk.id"
          class="character-count"
        >
          分块{{ index + 1 }} 字符数：{{ chunk.content.length }}
        </div>
        <el-tag 
          size="small" 
          :type="isChunkHighlighted(chunk) ? 'success' : (hoveredChunkId === chunk.id ? 'primary' : 'info')"
          class="chunk-tag"
        >C-{{ index + 1 }}</el-tag>
        
        <!-- 编辑模式 -->
        <div v-if="editingChunkId === chunk.id" class="chunk-edit-container">
          <el-input
            v-model="editingContent"
            type="textarea"
            :rows="4"
            :maxlength="1024"
            show-word-limit
            resize="vertical"
            placeholder="请输入分块内容"
          ></el-input>
          <div class="edit-actions">
            <el-button size="small" @click="cancelChunkEdit">取消</el-button>
            <el-button type="primary" size="small" @click="saveChunkEdit(chunk)">保存</el-button>
          </div>
        </div>
        
        <!-- 正常显示模式 -->
        <div v-else class="chunk-content" v-html="renderContent(chunk.content)"></div>
        
        <div v-if="isChunkHighlighted(chunk)" class="chunk-score">
          <span>得分 {{ getChunkScore(chunk) }}</span>
          <div class="score-progress-wrapper">
            <div class="score-progress" :style="{width: getScorePercentage(chunk) + '%'}"></div>
          </div>
        </div>
        
        <!-- 操作按钮组 -->
        <div v-if="hoveredChunkId === chunk.id" class="chunk-actions">
          <el-button
            class="action-button"
            type="primary"
            size="small"
            circle
            icon="Edit"
            @click.stop="handleEditChunk(chunk)"
            title="编辑分块"
          ></el-button>
          <el-button
            class="action-button"
            type="success"
            size="small"
            circle
            icon="Plus"
            @click.stop="handleAddSubChunk(chunk, index)"
            title="在此分块后添加新分块"
          ></el-button>
          <el-button
            class="action-button delete-button"
            type="danger"
            size="small"
            circle
            icon="Delete"
            @click.stop="handleDeleteChunk(chunk)"
            title="删除分块"
          ></el-button>
        </div>
      </div>
    </div>
    
    <!-- 新增分块区域 -->
    <div v-if="isAddingChunk" class="new-chunk-container">
      <div class="new-chunk-header">
        <el-tag type="success">新增分块</el-tag>
      </div>
      <el-input
        v-model="newChunkContent"
        type="textarea"
        :rows="4"
        :maxlength="1024"
        show-word-limit
        resize="vertical"
        placeholder="请输入新分块内容"
      ></el-input>
      <div class="new-chunk-actions">
        <el-button size="small" @click="cancelAddChunk">取消</el-button>
        <el-button type="primary" size="small" @click="saveNewChunk">新增</el-button>
      </div>
    </div>
    
    <!-- 空状态下的添加按钮 -->
    <div v-if="!chunkList || chunkList.length === 0" class="no-chunks">
      <el-empty :description="$t('views.paragraph.noChunks')">
        <el-button type="primary" @click="handleAddFirstChunk">添加分块</el-button>
      </el-empty>
    </div>
    
    <!-- 底部添加按钮 -->
    <div v-if="chunkList && chunkList.length > 0" class="add-chunk-bottom">
      <el-button type="primary" icon="Plus" @click="handleAddSubChunk(null)">添加分块</el-button>
    </div>
    
    <!-- 显示命中的分块内容 -->
    <div v-if="hasHighlightedChunks" class="highlighted-chunks-container">
      <div class="highlighted-title">
        <el-tag type="success">命中分块</el-tag>
      </div>
      <div 
        v-for="chunk in highlightedChunks" 
        :key="chunk.id"
        class="highlighted-chunk-item"
      >
        <div class="highlighted-header">
          <div class="highlighted-score-container">
            <div class="score-percentage">{{ getScorePercentage(chunk) }}%</div>
            <div class="highlighted-score">得分: {{ Number(chunk.score).toFixed(2) }}</div>
          </div>
          <el-button
            type="danger"
            size="small"
            icon="Delete"
            circle
            @click.stop="handleDeleteChunk(chunk)"
          ></el-button>
        </div>
        <div class="score-bar-container">
          <div class="score-bar" :style="{width: getScorePercentage(chunk) + '%'}"></div>
        </div>
        <div class="highlighted-content" v-html="renderContent(chunk.content)">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessageBox, ElMessage } from 'element-plus'
// 导入API
import chunkApi from '@/api/chunk'

// 添加国际化支持
const { t } = useI18n()

// 定义分块类型接口
interface ChunkItem {
  id: string
  content: string
  paragraph_id?: string
  document_id?: string
  dataset_id?: string
  chunk_index?: number
  char_length?: number
  create_time?: string
  update_time?: string
  [key: string]: any
}

interface ChunkDataItem {
  id: string
  content?: string
  score?: number
  [key: string]: any
}

const props = defineProps({
  chunkList: {
    type: Array as () => ChunkItem[],
    default: () => []
  },
  chunkData: {
    type: Object,
    default: () => ({})
  },
  paragraphId: {
    type: String,
    default: ''
  }
})

// 定义要发出的事件
const emit = defineEmits(['refresh-chunks'])

const hoveredChunkId = ref('')
const editingChunkId = ref('')
const editingContent = ref('')
const isAddingChunk = ref(false)
const newChunkContent = ref('')
const insertAfterIndex = ref(-1)

const handleHover = (chunkId: string, isHovered: boolean) => {
  if (!editingChunkId.value && !isAddingChunk.value) {
    hoveredChunkId.value = isHovered ? chunkId : ''
  }
}

// 处理编辑分块
const handleEditChunk = (chunk: ChunkItem) => {
  editingChunkId.value = chunk.id
  editingContent.value = chunk.content
}

// 取消编辑
const cancelChunkEdit = () => {
  editingChunkId.value = ''
  editingContent.value = ''
}

// 保存编辑的分块
const saveChunkEdit = async (chunk: ChunkItem) => {
  const { id, document_id, dataset_id } = chunk
  
  if (!id || !document_id || !dataset_id) {
    ElMessage.error('保存失败：缺少必要参数')
    return
  }
  
  try {
    const loading = ref(true)
    const data = {
      content: editingContent.value,
      char_length: editingContent.value.length
    }
    
    const result = await chunkApi.putChunk(dataset_id, document_id, id, data, loading)
    
    if (result && (result.code === 0 || result.code === 200)) {
      ElMessage.success('分块更新成功')
      // 触发刷新事件
      emit('refresh-chunks')
      // 退出编辑模式
      cancelChunkEdit()
    } else {
      ElMessage.error((result && result.message) || '保存失败')
    }
  } catch (error: any) {
    console.error('更新分块出错:', error)
    ElMessage.error('更新分块失败：' + (error.message || '未知错误'))
  }
}

// 处理添加子分块
const handleAddSubChunk = (chunk: ChunkItem | null, index?: number) => {
  isAddingChunk.value = true
  newChunkContent.value = ''
  
  // 如果提供了索引，表示在特定位置后添加
  if (index !== undefined) {
    insertAfterIndex.value = index
  } else {
    // 如果没有提供索引，则添加到最后
    insertAfterIndex.value = props.chunkList.length - 1
  }
}

// 处理添加第一个分块
const handleAddFirstChunk = () => {
  isAddingChunk.value = true
  newChunkContent.value = ''
  insertAfterIndex.value = -1
}

// 取消添加
const cancelAddChunk = () => {
  isAddingChunk.value = false
  newChunkContent.value = ''
  insertAfterIndex.value = -1
}

// 保存新分块
const saveNewChunk = async () => {
  if (!newChunkContent.value.trim()) {
    ElMessage.warning('分块内容不能为空')
    return
  }
  
  if (!props.chunkList || props.chunkList.length === 0) {
    // 如果没有分块，需要获取文档和知识库ID
    if (!props.paragraphId) {
      ElMessage.error('保存失败：缺少必要参数')
      return
    }
    
    // 这里可能需要根据实际情况调整，如何获取document_id和dataset_id
    // 可能需要通过props传入或者通过其他API获取
    ElMessage.error('保存失败：无法创建第一个分块，请联系管理员')
    return
  }
  
  // 使用现有分块的文档和知识库ID
  const referenceChunk = props.chunkList[0]
  const { document_id, dataset_id } = referenceChunk
  
  if (!document_id || !dataset_id) {
    ElMessage.error('保存失败：缺少必要参数')
    return
  }
  
  try {
    const loading = ref(true)
    
    // 计算新分块的索引
    let chunk_index = 0
    if (insertAfterIndex.value >= 0 && insertAfterIndex.value < props.chunkList.length) {
      // 当前选中分块后的索引 + 1
      chunk_index = (props.chunkList[insertAfterIndex.value].chunk_index || 0) + 1
      
      // 如果不是最后一个，取当前和下一个的中间值
      if (insertAfterIndex.value < props.chunkList.length - 1) {
        const nextIndex = props.chunkList[insertAfterIndex.value + 1].chunk_index || 0
        chunk_index = Math.floor((chunk_index + nextIndex) / 2)
      }
    }
    
    const data = {
      content: newChunkContent.value,
      char_length: newChunkContent.value.length,
      chunk_index,
      paragraph_id: props.paragraphId || referenceChunk.paragraph_id
    }
    
    // 确保传入的paragraph_id不为undefined
    const paragraphId = props.paragraphId || referenceChunk.paragraph_id
    if (!paragraphId) {
      ElMessage.error('保存失败：缺少段落ID')
      return
    }
    
    const result = await chunkApi.postChunk(dataset_id, document_id, paragraphId, data, loading)
    
    if (result && (result.code === 0 || result.code === 200)) {
      ElMessage.success('新分块创建成功')
      // 触发刷新事件
      emit('refresh-chunks')
      // 退出添加模式
      cancelAddChunk()
    } else {
      ElMessage.error((result && result.message) || '创建失败')
    }
  } catch (error: any) {
    console.error('创建分块出错:', error)
    ElMessage.error('创建分块失败：' + (error.message || '未知错误'))
  }
}

// 处理删除分块
const handleDeleteChunk = async (chunk: ChunkItem) => {
  const { id, document_id, dataset_id } = chunk
  
  // 确保必需的参数不为空
  if (!id || !document_id || !dataset_id) {
    ElMessage.error('删除失败：缺少必要参数')
    return
  }
  
  // 弹出确认对话框
  ElMessageBox.confirm(
    '确定要删除这个分块吗？删除后该部分对应的向量内容也会删除，后续无法检索到该段内容',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    } 
  ).then(async () => {
    try {
      const loading = ref(true)
      // 使用导入的API对象调用方法
      const result = await chunkApi.delChunk(dataset_id, document_id, id, loading)
      
      if (result && (result.code === 0 || result.code === 200)) {
        // 删除成功
        ElMessage.success('分块删除成功')
        // 触发刷新事件，立即通知父组件重新加载数据
        emit('refresh-chunks')
      } else {
        ElMessage.error((result && result.message) || '删除失败')
      }
    } catch (error: any) {
      console.error('删除分块出错:', error)
      ElMessage.error('删除分块失败：' + (error.message || '未知错误'))
    }
  }).catch(() => {
    // 用户取消删除
    ElMessage.info('删除操作已取消')
  })
}

// 获取命中的分块列表
const highlightedChunks = computed(() => {
  if (!props.chunkData) return []
  
  if (Array.isArray(props.chunkData)) {
    return props.chunkData
  } else if (props.chunkData.id) {
    return [props.chunkData]
  }
  
  return []
})

// 是否有命中的分块
const hasHighlightedChunks = computed(() => {
  return highlightedChunks.value.length > 0
})

// 检查当前分块是否被高亮（是否包含在chunkData中）
const isChunkHighlighted = (chunk: ChunkItem) => {
  if (!props.chunkData) return false
  
  // 处理对象类型
  if (typeof props.chunkData === 'object') {
    // 如果是数组
    if (Array.isArray(props.chunkData)) {
      return props.chunkData.some((item: any) => item.id === chunk.id)
    } 
    // 如果是单个对象
    else if (props.chunkData.id) {
      return props.chunkData.id === chunk.id
    }
  }
  
  return false
}

// 从chunkData中获取分块的得分
const getChunkScore = (chunk: ChunkItem) => {
  if (!props.chunkData) return '0.00'
  
  // 处理对象类型
  if (typeof props.chunkData === 'object') {
    // 如果是数组
    if (Array.isArray(props.chunkData)) {
      const chunkInfo = props.chunkData.find((item: any) => item.id === chunk.id)
      return chunkInfo?.score ? Number(chunkInfo.score).toFixed(2) : '0.00'
    } 
    // 如果是单个对象
    else if (props.chunkData.id === chunk.id) {
      return props.chunkData.score ? Number(props.chunkData.score).toFixed(2) : '0.00'
    }
  }
  
  return '0.00'
}

// 计算分数的百分比（将分数转换为0-100的数值）
const getScorePercentage = (chunk: any) => {
  const score = parseFloat(getChunkScore(chunk))
  // 假设分数范围是0-1，转换为百分比
  return Math.min(Math.round(score * 100), 100)
}

// 处理内容中的Markdown图片链接
const renderContent = (content: string) => {
  if (!content) return ''
  
  // 匹配Markdown图片链接 [](/api/image/xxx)
  const imgRegex = /\[\]\(\/api\/image\/([a-zA-Z0-9-]+)\)/g
  
  // 将链接替换为<img>标签
  return content.replace(imgRegex, (match, imageId) => {
    return `<img src="/api/image/${imageId}" class="chunk-image" alt="嵌入图片" />`
  })
}
</script>

<style scoped lang="scss">
.paragraph-chunk-container {
  margin-bottom: 24px;
}

.chunks-container {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.chunk-item {
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: flex-start;
  position: relative;
  border: 1px solid transparent;
  min-width: 200px;
  
  &.chunk-hover:not(.chunk-hit) {
    background-color: #ecf5ff;
    border-color: #409eff;
  }
  
  &.chunk-hit {
    background-color: #f0f9eb;
    border-color: #67c23a;
    box-shadow: 0 0 8px rgba(103, 194, 58, 0.2);
  }
  
  &.editing {
    background-color: #f5f7fa;
    border-color: #409eff;
    box-shadow: 0 0 8px rgba(64, 158, 255, 0.2);
    width: 100%;
  }
}

.chunk-tag {
  margin-right: 8px;
  flex-shrink: 0;
  font-size: 12px;
}

.chunk-content {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  position: relative;
  
  .chunk-hit & {
    font-weight: 500;
  }
}

.character-count {
  position: absolute;
  top: -30px;
  left: 10px;
  background-color: #409eff;
  color: white;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
  white-space: nowrap;
  pointer-events: none;
  font-weight: bold;
}

.chunk-score {
  margin-left: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #67c23a;
  background-color: #f0f9eb;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  display: flex;
  flex-direction: column;
  min-width: 80px;
  
  .score-progress-wrapper {
    margin-top: 3px;
    height: 4px;
    background-color: rgba(103, 194, 58, 0.2);
    border-radius: 2px;
    overflow: hidden;
  }
  
  .score-progress {
    height: 100%;
    background-color: #67c23a;
    border-radius: 2px;
  }
}

.highlighted-chunks-container {
  border: 1px solid #e1f3d8;
  border-radius: 4px;
  background-color: #f0f9eb;
  margin-bottom: 16px;
  overflow: hidden;
}

.highlighted-title {
  padding: 10px 16px;
  border-bottom: 1px solid #e1f3d8;
  background-color: #f0f9eb;
  font-weight: bold;
}

.highlighted-chunk-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e1f3d8;
  
  &:last-child {
    border-bottom: none;
  }
}

.highlighted-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.highlighted-index {
  color: #606266;
  font-weight: 500;
}

.highlighted-score-container {
  display: flex;
  align-items: center;
}

.score-percentage {
  font-size: 14px;
  font-weight: 700;
  color: #67c23a;
  margin-right: 8px;
}

.highlighted-score {
  color: #67c23a;
  font-weight: 600;
  background-color: #f0f9eb;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #c2e7b0;
}

.score-bar-container {
  height: 8px;
  background-color: rgba(103, 194, 58, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.score-bar {
  height: 100%;
  background-color: #67c23a;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.highlighted-content {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background-color: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
}

.no-chunks {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.chunk-image {
  max-width: 100%;
  border-radius: 4px;
  margin: 8px 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 操作按钮组 */
.chunk-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
}

.action-button {
  opacity: 0.8;
  transition: all 0.3s;
  
  &:hover {
    opacity: 1;
    transform: scale(1.1);
  }
}

/* 编辑容器样式 */
.chunk-edit-container {
  width: 100%;
}

.edit-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 新增分块容器样式 */
.new-chunk-container {
  border: 1px solid #409eff;
  border-radius: 4px;
  margin-bottom: 16px;
  overflow: hidden;
  background-color: #ecf5ff;
}

.new-chunk-header {
  padding: 10px 16px;
  border-bottom: 1px solid #d9ecff;
  background-color: #ecf5ff;
  font-weight: bold;
}

.new-chunk-actions {
  padding: 8px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 底部添加按钮 */
.add-chunk-bottom {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}
</style> 