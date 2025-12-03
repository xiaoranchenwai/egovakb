<template>
  <div class="module-form mcp-module-form">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" label-position="left">
      <el-form-item label="服务名称:" prop="name">
        <el-input v-model.trim="form.name" placeholder="请输入服务名称" clearable></el-input>
      </el-form-item>

      <el-form-item label="服务描述:" prop="description">
        <textarea v-model="form.description" rows="3" placeholder="请输入服务描述" class="el-textarea__inner"
          style="width: 100%; border-radius: 4px; border: 1px solid #DCDFE6; padding: 10px;" clearable></textarea>
      </el-form-item>

      <el-row :gutter="0">
        <el-col :span="12">
          <el-form-item label="版本信息:" prop="version" class="required-dot">
            <el-input v-model.trim="form.version" placeholder="请输入版本号，例如：1.0.0" clearable></el-input>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="服务分类:" prop="category_id" class="required-dot">
            <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%" clearable>
              <el-option v-for="category in localCategories" :key="category.id" :label="category.name"
                :value="category.id"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="服务详情:" class="required-dot">
        <div class="markdown-editor-container">
          <div class="tabs-container flex-between">
            <div class="left-box">
              <textarea v-model="form.markdown_docs" rows="8" placeholder="请输入服务详情（支持Markdown格式）"
                class="el-textarea__inner markdown-editor" clearable></textarea>
            </div>
            <div class="right-box">
              <div class="markdown-preview-container">
                <VueMarkdownRender v-if="form.markdown_docs" :source="form.markdown_docs" class="markdown-body" />
                <el-empty v-else description="暂无内容" />
              </div>
            </div>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="参数配置:" class="required-dot">
        <div class="config-schema-container">
          <div class="config-schema-help">
            <el-alert type="info" :closable="false" show-icon title="配置模板说明"
              description="定义服务发布时需要用户配置的参数。用户可以添加、编辑和删除参数配置。" />
          </div>

          <!-- 参数配置表格 -->
          <div class="config-params-table">
            <div class="table-header">
              <span>参数配置列表</span>
              <a class="add-param-btn" @click="addConfigParam">
                <el-icon>
                  <Plus />
                </el-icon>
                添加参数
              </a>
            </div>

            <el-table :data="configParams" border style="width: 100%" empty-text="暂无参数配置">
              <el-table-column prop="key" label="参数名" width="120">
                <template #default="{ row }">
                  <span>{{ row.key }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="title" label="显示名称" width="120">
                <template #default="{ row }">
                  <span>{{ row.title || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getTypeTagType(row.type)" size="small">{{ getTypeLabel(row.type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="required" label="必填" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                    {{ row.required ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" min-width="150">
                <template #default="{ row }">
                  <span>{{ row.description || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row, $index }">
                  <el-button type="primary" size="small" text @click="editConfigParam(row, $index)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" text @click="deleteConfigParam($index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="代码:" prop="code">
        <CodemirrorEditor v-model="form.code" title="模块代码" style="height: 300px" />
      </el-form-item>

      <el-form-item label="访问权限:">
        <el-radio-group v-model="form.is_public">
          <el-radio :label="true">公开</el-radio>
          <el-radio :label="false">私有</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <div class="form-actions">
      <el-button @click="cancel">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="loading">{{ submitButtonText }}</el-button>
    </div>

    <!-- 参数编辑对话框 -->
    <el-drawer direction="rtl" v-model="paramDialogVisible" :title="paramDialogMode === 'add' ? '添加参数' : '编辑参数'"
      width="50%" :destroy-on-close="true">
      <el-form ref="paramFormRef" :model="paramForm" :rules="paramRules" label-width="100px" label-position="left">
        <el-form-item label="参数名:" prop="key">
          <el-input v-model="paramForm.key" placeholder="请输入参数名（英文，如：api_key）" :disabled="paramDialogMode === 'edit'" />
        </el-form-item>

        <el-form-item label="显示名称:" prop="title">
          <el-input v-model="paramForm.title" placeholder="请输入显示名称（如：API密钥）" />
        </el-form-item>

        <el-form-item label="参数类型:" prop="type">
          <el-select v-model="paramForm.type" placeholder="请选择参数类型" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="密码" value="password" />
            <el-option label="布尔值" value="boolean" />
          </el-select>
        </el-form-item>

        <el-form-item label="是否必填:" class="required-dot">
          <el-switch v-model="paramForm.required" />
        </el-form-item>

        <el-form-item label="描述信息:" class="required-dot">
          <el-input v-model="paramForm.description" type="textarea" :rows="3" placeholder="请输入参数描述信息" />
        </el-form-item>

        <el-form-item label="占位符:" class="required-dot">
          <el-input v-model="paramForm.placeholder" placeholder="请输入输入框占位符文本" />
        </el-form-item>

        <el-form-item label="默认值:" v-if="paramForm.type !== 'password'" class="required-dot">
          <el-input v-if="paramForm.type === 'string'" v-model="paramForm.default" placeholder="请输入默认值" />
          <el-input-number v-else-if="paramForm.type === 'integer'" v-model="paramForm.default" placeholder="请输入默认值"
            style="width: 100%" />
          <el-switch v-else-if="paramForm.type === 'boolean'" v-model="paramForm.default" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="paramDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfigParam">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineProps, defineEmits, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import VueMarkdownRender from 'vue-markdown-render'
import CodemirrorEditor from '@/components/codemirror-editor/index.vue'
import type { McpModuleInfo } from '@/api/type/mcp-square'
import type { McpGroup } from '@/api/type/mcp-group'

import mcpGroupApi from '@/api/mcp-group'

// 参数配置项类型定义
interface ConfigParam {
  key: string
  type: 'string' | 'integer' | 'password' | 'boolean'
  title: string
  description: string
  required: boolean
  placeholder?: string
  default?: any
}

const props = defineProps<{
  moduleInfo?: McpModuleInfo
  categories: McpGroup[]
  loading: boolean
  isEdit?: boolean
}>()

const emit = defineEmits<{
  (e: 'submit', formData: any): void
  (e: 'cancel'): void
  (e: 'categoriesLoaded', categories: McpGroup[]): void
}>()

const formRef = ref<any>(null)
const markdownActiveTab = ref('edit')
const loadingCategories = ref(false)
const localCategories = ref<McpGroup[]>([])

// 监听props中的categories变化
watch(() => props.categories, (newCategories) => {
  if (newCategories && newCategories.length > 0) {
    localCategories.value = newCategories
  }
}, { immediate: true })

// 表单数据
const form = ref<{
  name: string
  description: string
  version: string
  category_id: number | null
  markdown_docs: string
  code: string
  config_schema: Record<string, any> | null
  is_public: boolean
}>({
  name: '',
  description: '',
  version: '',
  category_id: null,
  markdown_docs: '',
  code: '',
  config_schema: null,
  is_public: true
})

// 参数配置列表
const configParams = ref<ConfigParam[]>([])

// 参数编辑对话框相关
const paramDialogVisible = ref(false)
const paramDialogMode = ref<'add' | 'edit'>('add')
const paramEditIndex = ref(-1)
const paramFormRef = ref<any>(null)

// 参数表单数据
const paramForm = ref<ConfigParam>({
  key: '',
  type: 'string',
  title: '',
  description: '',
  required: false,
  placeholder: '',
  default: undefined
})

// 参数表单验证规则
const paramRules = {
  key: [
    { required: true, message: '请输入参数名', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '参数名只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入显示名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择参数类型', trigger: 'change' }
  ]
}

// 监听configParams变化，自动更新form.config_schema
watch(configParams, (newParams) => {
  if (newParams.length === 0) {
    form.value.config_schema = null
  } else {
    const schema: Record<string, any> = {}
    newParams.forEach(param => {
      schema[param.key] = {
        type: param.type,
        title: param.title,
        description: param.description,
        required: param.required,
        ...(param.placeholder && { placeholder: param.placeholder }),
        ...(param.default !== undefined && param.default !== '' && { default: param.default })
      }
    })
    form.value.config_schema = schema
  }
}, { deep: true })

// 获取类型标签样式
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    'string': 'primary',
    'integer': 'success',
    'password': 'warning',
    'boolean': 'info'
  }
  return typeMap[type] || 'primary'
}

// 获取类型显示标签
const getTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    'string': '字符串',
    'integer': '整数',
    'password': '密码',
    'boolean': '布尔值'
  }
  return labelMap[type] || type
}

// 添加参数
const addConfigParam = () => {
  paramDialogMode.value = 'add'
  paramEditIndex.value = -1
  paramForm.value = {
    key: '',
    type: 'string',
    title: '',
    description: '',
    required: false,
    placeholder: '',
    default: undefined
  }
  paramDialogVisible.value = true
}

// 编辑参数
const editConfigParam = (param: ConfigParam, index: number) => {
  paramDialogMode.value = 'edit'
  paramEditIndex.value = index
  paramForm.value = { ...param }
  paramDialogVisible.value = true
}

// 删除参数
const deleteConfigParam = (index: number) => {
  configParams.value.splice(index, 1)
  ElMessage.success('参数删除成功')
}

// 保存参数配置
const saveConfigParam = async () => {
  if (!paramFormRef.value) return

  try {
    await paramFormRef.value.validate()

    // 检查参数名是否重复（编辑模式下排除自身）
    const existingIndex = configParams.value.findIndex(p => p.key === paramForm.value.key)
    if (existingIndex !== -1 && existingIndex !== paramEditIndex.value) {
      ElMessage.error('参数名已存在，请使用其他名称')
      return
    }

    if (paramDialogMode.value === 'add') {
      configParams.value.push({ ...paramForm.value })
      ElMessage.success('参数添加成功')
    } else {
      configParams.value[paramEditIndex.value] = { ...paramForm.value }
      ElMessage.success('参数更新成功')
    }

    paramDialogVisible.value = false
  } catch (error) {
    console.error('参数表单验证失败', error)
  }
}

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入服务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入服务描述', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入代码', trigger: 'blur' }
  ]
}

// 提交按钮文本
const submitButtonText = computed(() => props.isEdit ? '更新' : '创建')

// 初始化表单数据
onMounted(() => {
  if (props.moduleInfo) {
    form.value = {
      name: props.moduleInfo.name || '',
      description: props.moduleInfo.description || '',
      version: props.moduleInfo.version || '',
      category_id: props.moduleInfo.category_id || null,
      markdown_docs: props.moduleInfo.markdown_docs || '',
      code: props.moduleInfo.code || '',
      config_schema: props.moduleInfo.config_schema || null,
      is_public: props.moduleInfo.is_public === false ? false : true
    }

    // 初始化configParams
    if (props.moduleInfo.config_schema) {
      try {
        const schema = props.moduleInfo.config_schema
        configParams.value = Object.entries(schema).map(([key, config]: [string, any]) => ({
          key,
          type: config.type || 'string',
          title: config.title || '',
          description: config.description || '',
          required: config.required || false,
          placeholder: config.placeholder || '',
          default: config.default
        }))
      } catch (error) {
        console.error('解析config_schema失败', error)
        configParams.value = []
      }
    }
  }

  // 如果分类列表为空，则加载分类
  if (props.categories.length === 0) {
    loadCategories()
  }
})

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 构建提交数据
    const formData = {
      name: form.value.name,
      description: form.value.description,
      version: form.value.version,
      category_id: form.value.category_id,
      markdown_docs: form.value.markdown_docs,
      code: form.value.code,
      config_schema: form.value.config_schema,
      is_public: form.value.is_public
    }

    emit('submit', formData)
  } catch (error) {
    console.error('表单验证失败', error)
    ElMessage.error('请检查表单填写是否正确')
  }
}

// 取消操作
const cancel = () => {
  emit('cancel')
}

// 加载分类列表
const loadCategories = async () => {
  if (localCategories.value.length > 0) return

  loadingCategories.value = true
  try {
    const response = await mcpGroupApi.listGroup(loadingCategories)
    if (response && response.data) {
      localCategories.value = response.data
      emit('categoriesLoaded', response.data)
    }
  } catch (error) {
    console.error('加载分类失败', error)
    ElMessage.error('加载分类失败')
  } finally {
    loadingCategories.value = false
  }
}

defineExpose({
  submitForm
})
</script>

<style lang="scss" scoped>
.module-form {
  padding: 20px 0;
}

.form-actions {
  margin-top: 20px;
  text-align: right;
}

.markdown-editor-container {
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  width: 100%;
}

.markdown-editor {
  width: 60%;
  border-radius: 4px;
  border: 1px solid #DCDFE6;
  padding: 10px;
  font-family: monospace;
}

.markdown-preview-container {
  padding: 10px;
  height: 12em;
  border-radius: 4px;
  border: 1px solid #DCDFE6;
  overflow-y: auto;
}

.markdown-body {
  padding: 10px;
}

.config-schema-container {
  width: 100%;
}

.config-schema-help {
  margin-bottom: 12px;
}

.config-params-table {
  margin-top: 12px;
}

.table-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;

  .add-param-btn {
    color: #3388FF;
    margin-left: 10px;
    display: flex;
    flex-direction: row;
    align-items: center;
  }
}
</style>
<style lang="scss">
.mcp-module-form {
  .markdown-editor-container {
    .left-box {
      width: 60%;
      border-right: 1px solid #DCDFE6;

      .markdown-editor {
        width: 100% !important;
        border: none !important;

        max-height: 190px !important;
      }
    }

    .right-box {
      width: 40%;
    }

    .left-box,
    .right-box {
      position: relative;
    }

    .markdown-preview-container {
      border: none !important;
      max-height: 190px !important;
    }
  }

  .el-alert__description {
    color: #6B7A99 !important;
  }

  .config-schema-help {
    .el-alert--info.is-light {
      background-color: #F5F7FA !important;
    }
    .el-icon {
      color: #3388FF !important;
    }
  }

  .el-form-item__label {
    padding-right: 8px !important;
    text-align: right!important;
    justify-content: flex-end !important;
  }

  .el-drawer__footer {
    border-top: none !important;
  }

  > .el-form {
    .el-textarea__inner {
      box-shadow: none !important;
    }
  }
}
</style>