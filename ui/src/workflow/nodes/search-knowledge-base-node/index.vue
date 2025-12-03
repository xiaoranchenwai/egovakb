<template>
  <NodeContainer :nodeModel="nodeModel">
    <h5 class="title-decoration-1 mb-8">{{ $t('views.applicationWorkflow.nodeSetting') }}</h5>
    <el-card shadow="never" class="card-never">
      <el-form @submit.prevent :model="form_data" label-position="top" require-asterisk-position="left"
        label-width="auto" ref="KnowledgeBaseNodeFormRef">
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.url') + ':'"
          prop="knowledge_base_url" :rules="{
    message: $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.urlRequired'),
    trigger: 'blur',
    required: true
  }">
          <el-input v-model="form_data.knowledge_base_url"
            :placeholder="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.urlPlaceholder')" clearable />
        </el-form-item>

        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.key') + ':'"
          prop="knowledge_base_key" :rules="{
    message: $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.keyRequired'),
    trigger: 'blur',
    required: true
  }">
          <el-input v-model="form_data.knowledge_base_key"
            :placeholder="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.keyPlaceholder')" type="password"
            show-password clearable />
        </el-form-item>



        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.knowledgeBaseList') + ':'">
          <template #label>
            <div class="flex-between">
              <span>{{ $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.knowledgeBaseList') }}:</span>
              <el-button type="primary" link @click="refreshKnowledgeBaseList" :loading="knowledgeBaseLoading">
                <el-icon>
                  <Refresh />
                </el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-select v-model="form_data.knowledge_base_list"
              :placeholder="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.knowledgeBaseSelectPlaceholder')"
              clearable multiple class="w-full" value-key="id">
              <el-option v-for="item in knowledgeBaseList" :key="item.id" :label="item.name" :value="item">
                <div class="flex-between">
                  <span>{{ item.name }}</span>
                  <span v-if="isKnowledgeBaseSelected(item)" class="text-primary">✓ 已选择</span>
                </div>
              </el-option>
            </el-select>
            <!-- 显示已选择的知识库数量 -->
            <div v-if="form_data.knowledge_base_list && form_data.knowledge_base_list.length > 0" 
                 class="mt-2 text-sm text-gray-600">
              已选择 {{ form_data.knowledge_base_list.length }} 个知识库
            </div>
          </div>
        </el-form-item>
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchParam') + ':'">
          <template #label>
            <div class="flex-between">
              <span>{{ $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchParam') }}:</span>
              <el-button type="primary" link @click="openSearchParamDialog">
                <el-icon>
                  <Setting />
                </el-icon>
              </el-button>
            </div>
          </template>
          <div class="w-full">
            <el-row>
              <el-col :span="12" class="color-secondary lighter">{{
    $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchMode') }}</el-col>
              <el-col :span="12" class="lighter">{{ searchModeDisplayName }}</el-col>
              <el-col :span="12" class="color-secondary lighter">{{
    $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.topN') }}</el-col>
              <el-col :span="12" class="lighter">{{ form_data.top_n }}</el-col>
              <el-col :span="12" class="color-secondary lighter">{{
    $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.similarity') }}</el-col>
              <el-col :span="12" class="lighter">{{ form_data.similarity }}</el-col>
            </el-row>
          </div>
        </el-form-item>
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchQuestion.label') + ':'"
          prop="question_reference_address" :rules="{
    message: $t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchQuestion.requiredMessage'),
    trigger: 'blur',
    required: true
  }">
          <NodeCascader ref="nodeCascaderRef" :nodeModel="nodeModel" class="w-full"
            :placeholder="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchQuestion.placeholder')"
            v-model="form_data.question_reference_address" />
        </el-form-item>

        <el-form-item
          :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchQuestion.showHitBlock') + ':'">
          <el-switch v-model="form_data.show_hit_block" />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 搜索参数设置对话框 -->
    <el-dialog v-model="searchParamDialogVisible"
      :title="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchParamSetting')" width="500px"
      append-to-body draggable>
      <el-form :model="tempSearchSetting" label-width="100px">
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.searchMode')">
          <el-select v-model="tempSearchSetting.search_mode" class="w-full">
            <el-option label="向量语义搜索-最精确" value="embedding_vector" />
            <el-option label="全文搜索-最快" value="content" />
            <!-- <el-option label="PostgreSQL全文搜索-中等速度" value="search_vector" /> -->
            <!-- <el-option label="混合检索" value="hybrid" /> -->
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.topN')">
          <el-input v-model.number="tempSearchSetting.top_n" type="number" :min="1" :max="20" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="$t('views.applicationWorkflow.nodes.searchKnowledgeBaseNode.similarity')">
          <el-slider v-model="tempSearchSetting.similarity" :min="0" :max="1" :step="0.01" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="searchParamDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="saveSearchParam">{{ $t('common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </NodeContainer>
</template>
<script setup lang="ts">
import { set } from 'lodash'
import { app } from '@/main'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import NodeCascader from '@/workflow/common/NodeCascader.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const rules = {
  knowledge_base_url: [{ required: true, message: '请输入外部知识库服务地址', trigger: 'blur' }],
  knowledge_base_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }],
  knowledge_base_id_list: [{ required: true, message: '请选择知识库', trigger: 'change' }],
  search_mode: [{ required: true, message: '请选择检索模式', trigger: 'change' }],
  top_n: [
    { required: true, message: '请输入返回数量', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '返回数量必须在1-100之间', trigger: 'blur' }
  ],
  similarity: [
    { required: true, message: '请输入相似度', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '相似度必须在0-1之间', trigger: 'blur' }
  ]
}

const props = defineProps<{ nodeModel: any }>()
const nodeCascaderRef = ref()

// 定义搜索模式类型
type SearchMode = 'content' | 'search_vector' | 'embedding_vector' | 'hybrid' | 'fulltext' | 'vector'

// 检索模式中文名称映射
const searchModeLabels: Record<SearchMode, string> = {
  'content': '全文搜索-最快',
  'search_vector': 'PostgreSQL全文搜索-中等速度',
  'embedding_vector': '向量语义搜索-最精确',
  'hybrid': '混合检索',
  'fulltext': '全文搜索',
  'vector': '向量搜索'
}

// 获取检索模式的中文显示名称
const searchModeDisplayName = computed(() => {
  const searchMode = form_data.value.search_mode as SearchMode
  return searchModeLabels[searchMode] || form_data.value.search_mode
})

const form_data = computed({
  get: () => {
    if (!props.nodeModel.properties.node_data) {
      set(props.nodeModel.properties, 'node_data', {
        knowledge_base_url: '',
        knowledge_base_key: '',
        knowledge_base_list: [], // 存储完整的知识库对象 {id, name}
        search_mode: 'embedding_vector',
        top_n: 3,
        similarity: 0.5,
        max_paragraph_char_number: 5000,
        search_param_setting: {
          top_n: 3,
          similarity: 0.5,
          max_paragraph_char_number: 5000
        },
        question_reference_address: [],
        show_hit_block: false
      })
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const KnowledgeBaseNodeFormRef = ref<FormInstance>()
const knowledgeBaseList = ref<any>([])
const knowledgeBaseLoading = ref(false)
const searchParamDialogVisible = ref(false)
const tempSearchSetting = ref({
  search_mode: 'embedding_vector',
  top_n: 3,
  similarity: 0.5
})

// 刷新知识库列表
const refreshKnowledgeBaseList = async (showMessage = true) => {
  if (!form_data.value.knowledge_base_url || !form_data.value.knowledge_base_key) {
    if (showMessage) {
      ElMessage.warning('请先填写外部知识库服务地址和API密钥')
    }
    return
  }

  knowledgeBaseLoading.value = true
  try {
    const response = await fetch(`${form_data.value.knowledge_base_url}/api/v1/datasets-search/accessible-datasets`, {
      method: 'GET',
      headers: {
        'Authorization': form_data.value.knowledge_base_key,
        'User-Agent': 'MaxKB/1.0.0 (https://maxkb.cn)',
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()

    if (result.code === 0) {
      knowledgeBaseList.value = result.data.list || []
      
      // 初始化时，如果已有选择的知识库但不在当前列表中，需要合并
      if (form_data.value.knowledge_base_list && form_data.value.knowledge_base_list.length > 0) {
        const existingIds = knowledgeBaseList.value.map((item: any) => item.id)
        const selectedKnowledgeBases = form_data.value.knowledge_base_list.filter((selected: any) => 
          !existingIds.includes(selected.id)
        )
        if (selectedKnowledgeBases.length > 0) {
          knowledgeBaseList.value = [...knowledgeBaseList.value, ...selectedKnowledgeBases]
        }
      }
      
      if (showMessage) {
        ElMessage.success(`成功获取到 ${result.data.total || 0} 个可访问的知识库`)
      }
    } else {
      if (showMessage) {
        ElMessage.error(result.message || '获取知识库列表失败')
      }
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    if (showMessage) {
      ElMessage.error('获取知识库列表失败，请检查服务地址和网络连接')
    }
  } finally {
    knowledgeBaseLoading.value = false
  }
}

// 初始化知识库列表
const initializeKnowledgeBaseList = async () => {
  // 如果已有选择的知识库，先将它们添加到列表中
  if (form_data.value.knowledge_base_list && form_data.value.knowledge_base_list.length > 0) {
    knowledgeBaseList.value = [...form_data.value.knowledge_base_list]
  }
  
  // 如果有配置信息，尝试自动加载完整列表
  if (form_data.value.knowledge_base_url && form_data.value.knowledge_base_key) {
    await refreshKnowledgeBaseList(false) // 不显示消息
  }
}

// 检查知识库是否已被选择
const isKnowledgeBaseSelected = (knowledgeBase: any) => {
  if (!form_data.value.knowledge_base_list || form_data.value.knowledge_base_list.length === 0) {
    return false
  }
  return form_data.value.knowledge_base_list.some((selected: any) => selected.id === knowledgeBase.id)
}

// 打开搜索参数设置对话框
const openSearchParamDialog = () => {
  tempSearchSetting.value = {
    search_mode: form_data.value.search_mode || 'embedding_vector',
    top_n: form_data.value.top_n || 3,
    similarity: form_data.value.similarity || 0.5
  }
  searchParamDialogVisible.value = true
}

// 保存搜索参数
const saveSearchParam = () => {
  set(props.nodeModel.properties.node_data, 'search_mode', tempSearchSetting.value.search_mode)
  set(props.nodeModel.properties.node_data, 'top_n', tempSearchSetting.value.top_n)
  set(props.nodeModel.properties.node_data, 'similarity', tempSearchSetting.value.similarity)
  searchParamDialogVisible.value = false
}

const validate = () => {
  return Promise.all([
    nodeCascaderRef.value.validate(),
    KnowledgeBaseNodeFormRef.value?.validate()
  ]).catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  // 初始化知识库列表
  initializeKnowledgeBaseList()
})
</script>

<style scoped>
.w-full {
  width: 100%;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.color-secondary {
  color: var(--el-text-color-secondary);
}

.lighter {
  font-weight: normal;
}

.mb-8 {
  margin-bottom: 8px;
}

.card-never {
  border: none;
  box-shadow: none;
}

.title-decoration-1 {
  font-weight: 600;
  color: var(--el-text-color-primary);
}
</style>
