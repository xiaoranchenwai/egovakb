<template>
  <div class="marketplace-detail-container">
    <header>
      <el-icon class="mr-8" @click="goBack">
        <ArrowLeftBold/>
      </el-icon>
      <h2>MCP模板详情</h2>
    </header>
    <main>
      <div v-if="loading" class="py-10">
        <el-skeleton :rows="10" animated/>
      </div>

      <div v-else>
        <!-- 顶部信息区域 - 使用flex布局水平排列两个卡片，添加相同高度 -->
        <div class="flex top-cards">
          <!-- 模块信息卡片 -->
          <div class="top-card">
            <ModuleInfo :moduleInfo="moduleInfo" :hasEditPermission="hasEditPermission" @showEditDialog="showEditDialog"
                        @deleteModule="handleDeleteModule"/>
          </div>

          <!-- 服务发布卡片 -->
          <div class="top-card">
            <ServicePublish :moduleId="moduleId" :services="services" :loadingServices="loadingServices"
                            @publishService="handlePublishService" @uninstallService="handleUninstallService"
                            @stopService="handleStopService" @startService="handleStartService"
                            @viewServiceParams="viewServiceParams"/>
          </div>
        </div>

        <!-- 标签页 - 添加固定高度和滚动条 -->
        <el-card shadow="never" class="tabs-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="服务详情" name="service-details">
              <div class="tab-content-container">
                <ServiceDetails :moduleInfo="moduleInfo"/>
              </div>
            </el-tab-pane>

            <el-tab-pane label="工具测试" name="tool-test">
              <div class="tab-content-container">
                <ToolTest :moduleId="moduleId" :moduleTools="moduleTools"/>
              </div>
            </el-tab-pane>

            <el-tab-pane label="代码查看/编辑" name="code-edit">
              <div class="tab-content-container">
                <CodeEditor :moduleId="moduleId" :code="moduleInfo.code" :hasEditPermission="hasEditPermission"
                            @saveCode="saveCode"/>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </main>

    <!-- 编辑模块对话框 -->
    <el-drawer v-model="editDialogVisible" title="编辑MCP服务" size="60%" :destroy-on-close="true" direction="rtl">
      <ModuleForm :moduleInfo="moduleInfo" :categories="categories" :loading="updating" :isEdit="true"
                  @submit="submitEditForm" @cancel="editDialogVisible = false" @categoriesLoaded="updateCategories"/>
    </el-drawer>

    <!-- 发布服务对话框 -->
    <el-drawer v-model="publishDialogVisible" title="配置并发布服务" width="50%" :destroy-on-close="true" direction="rtl">
      <el-form ref="configFormRef" :model="configForm" :rules="configRules" label-width="100px" label-position="top">
        <el-form-item label="服务名称" prop="service_name"
                      :rules="[{ required: true, message: '请输入服务名称', trigger: 'blur' }]">
          <el-input v-model="configForm.service_name" placeholder="请输入服务名称"></el-input>
        </el-form-item>
        <el-form-item label="是否公开" prop="is_public">
          <el-switch v-model="configForm.is_public" active-text="是" inactive-text="否" inline-prompt/>
        </el-form-item>
        <div v-if="!hasConfigSchema">
          <el-alert type="info" :closable="false" show-icon title="此模块没有需要配置的参数。" class="mb-4"/>
        </div>

        <template v-else>
          <el-alert type="warning" :closable="false" show-icon title="此模块需要配置以下参数才能发布" class="mb-4"/>

          <el-divider content-position="left">配置参数</el-divider>

          <div v-for="(schema, key) in moduleInfo.config_schema" :key="key" class="mb-4">
            <el-form-item :label="schema.title || key" :prop="`config_params.${key}`" label-position="left"
                          :rules="[{ required: schema.required, message: `请输入${schema.title || key}`, trigger: 'blur' }]">

              <!-- <div class="text-sm text-gray-500 mb-1">{{ schema.description }}</div> -->
              <div v-if="schema.type === 'integer'">
                <el-input v-model.number="configForm.config_params[key]" type="number"
                          :placeholder="schema.placeholder || `请输入${schema.title || key}`"/>
              </div>
              <div v-else>
                <el-input v-if="schema.type === 'password'" v-model="configForm.config_params[key]"
                          :placeholder="schema.placeholder || `请输入${schema.title || key}`"
                          :type="schema.type === 'password' ? 'password' : 'text'" show-password/>
                <el-input v-else v-model="configForm.config_params[key]"
                          :placeholder="schema.placeholder || `请输入${schema.title || key}`"/>
              </div>
            </el-form-item>
          </div>
        </template>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="publishDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitConfigForm" :loading="publishing">发布服务</el-button>
        </span>
      </template>
    </el-drawer>

    <!-- 服务参数查看/编辑对话框 -->
    <ServiceParamsDialog v-model="serviceParamsDialogVisible" :service="currentService"
                         :config-schema="moduleInfo.config_schema" :loading="updatingParams"
                         @confirm="updateServiceParamsFunc"
                         @cancel="serviceParamsDialogVisible = false"/>
  </div>
</template>

<script lang="ts" setup>

import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElNotification, ElMessage, ElMessageBox } from 'element-plus'
import mcpSquareApi from '@/api/mcp-square'
import mcpGroupApi from '@/api/mcp-group'
import mcpServiceApi from '@/api/mcp-service'
import type { McpModuleInfo, McpToolInfo } from '@/api/type/mcp-square'
import type { McpGroup } from '@/api/type/mcp-group'
import type { McpServiceInfo } from '@/api/type/mcp-service'

// 导入拆分后的组件
import ModuleInfo from '@/views/marketplace/components/ModuleInfo.vue'
import ServicePublish from '@/views/marketplace/components/ServicePublish.vue'
import ServiceDetails from '@/views/marketplace/components/ServiceDetails.vue'
import ToolTest from '@/views/marketplace/components/ToolTest.vue'
import CodeEditor from '@/views/marketplace/components/CodeEditor.vue'
import ModuleForm from '@/views/marketplace/components/ModuleForm.vue'
import ServiceParamsDialog from '@/components/service-params-dialog/index.vue'

const route = useRoute()
const router = useRouter()
const moduleId = computed(() => Number(route.params.id))

const loading = ref(true)
const moduleInfo = ref({} as McpModuleInfo)
const moduleTools = ref<McpToolInfo[]>([])
const activeTab = ref('service-details')

// 服务相关
const services = ref<McpServiceInfo[]>([])
const loadingServices = ref(false)

// 编辑相关
const editDialogVisible = ref(false)
const updating = ref(false)
const categories = ref<McpGroup[]>([])

// 当前用户信息
const currentUser = ref<{
  user_id: number | null
  username: string
  is_admin: boolean
}>({
  user_id: null,
  username: '',
  is_admin: false
})

// 检查是否有编辑权限
const hasEditPermission = computed(() => {
  // 优先使用后端返回的can_edit字段
  if (moduleInfo.value.can_edit !== undefined) {
    return moduleInfo.value.can_edit
  }

  // 兼容旧版本，如果后端没有返回can_edit字段，则使用原有逻辑
  // 如果是管理员，有编辑权限
  if (currentUser.value.is_admin) {
    return true
  }

  // 非管理员只能编辑自己创建的MCP服务
  return moduleInfo.value.user_id === currentUser.value.user_id
})

// 服务发布相关
const publishDialogVisible = ref(false)
const configFormRef = ref<any>()
const configForm = ref<{
  service_name: string
  is_public: boolean
  config_params: Record<string, any>
}>({
  service_name: '',
  is_public: false,
  config_params: {}
})
const configRules = ref<Record<string, any>>({})
const publishing = ref(false)
const configParams = ref<{
  key: string
  type: string
  title: string
  description: string
  required: boolean
  placeholder?: string
  default?: any
}[]>([])

// 判断是否有配置模式
const hasConfigSchema = computed(() => {
  return moduleInfo.value.config_schema &&
      Object.keys(moduleInfo.value.config_schema).length > 0
})

// 服务参数对话框相关
const serviceParamsDialogVisible = ref(false)
const currentService = ref<McpServiceInfo | null>(null)
const updatingParams = ref(false)

// 加载模块详情
async function loadModuleInfo() {
  loading.value = true
  try {
    const response = await mcpSquareApi.getModule(moduleId.value, loading)
    if (response && response.data) {
      moduleInfo.value = response.data
    } else {
      moduleInfo.value = {} as McpModuleInfo
    }

    const toolsResponse = await mcpSquareApi.getModuleTools(moduleId.value, loading)
    if (toolsResponse && toolsResponse.data) {
      moduleTools.value = toolsResponse.data
    } else {
      moduleTools.value = []
    }

    // 处理config_schema
    if (moduleInfo.value.config_schema) {
      try {
        // 先确保config_schema是对象格式
        let schema: Record<string, any>
        if (typeof moduleInfo.value.config_schema === 'string') {
          schema = JSON.parse(moduleInfo.value.config_schema)
        } else {
          schema = moduleInfo.value.config_schema
        }

        Object.entries(schema).forEach(([ key, config ]: [ string, any ]) => {
          configParams.value.push({
            key,
            type: config.type || 'string',
            title: config.title || '',
            description: config.description || '',
            required: config.required || false,
            placeholder: config.placeholder || '',
            default: config.default
          })
        })
      } catch (e) {
        console.error('解析配置模式失败', e)
        ElMessage.error('配置模式解析失败')
      }
    }
  } catch (error) {
    console.error('加载模块详情失败', error)
    ElNotification({
      title: '错误',
      message: '加载模块详情失败',
      type: 'error'
    })
  } finally {
    loading.value = false
  }
}

// 加载服务列表
const loadServices = async () => {
  loadingServices.value = true
  try {
    const response = await mcpServiceApi.listServices(moduleId.value, loading)
    if (response && response.data) {
      services.value = response.data
    } else {
      services.value = []
    }
  } catch (error) {
    console.error('加载服务列表失败', error)
    ElMessage.error('加载服务列表失败')
  } finally {
    loadingServices.value = false
  }
}

// 加载用户信息
const loadUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      const userInfo = JSON.parse(userInfoStr)
      currentUser.value = {
        user_id: userInfo.user_id || null,
        username: userInfo.username || '',
        is_admin: userInfo.is_admin || false
      }
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

// 处理发布服务
const handlePublishService = () => {
  publishDialogVisible.value = true
  initConfigForm() // 总是初始化表单，包括基本的服务字段
}

// 初始化配置表单
function initConfigForm() {
  configForm.value = {
    service_name: `${ moduleInfo.value.name }-实例-${ new Date().getTime().toString().slice(-6) }`, // 默认服务名称
    is_public: false,
    config_params: {}
  }
  configRules.value = {}

  if (moduleInfo.value.config_schema) {
    Object.entries(moduleInfo.value.config_schema).forEach(([ key, schema ]: [ string, any ]) => {
      configForm.value.config_params[key] = ''
      if (schema.required) {
        configRules.value[`config_params.${ key }`] = [
          { required: true, message: `请输入${ schema.title || key }`, trigger: 'blur' }
        ]
      }
    })
  }
}

// 提交配置表单
const submitConfigForm = async () => {
  if (!configFormRef.value) return

  try {
    await configFormRef.value.validate()
    publishDialogVisible.value = false
    publishServiceWithConfig(configForm.value)
  } catch (error) {
    console.error('表单验证失败', error)
  }
}

// 带配置参数发布服务
const publishServiceWithConfig = async (config: {
  service_name: string
  is_public: boolean
  config_params: Record<string, any>
}) => {
  try {
    ElMessage.info({ message: '正在发布服务...', duration: 0 })
    console.log('configForm', configForm)
    console.log('config', config)
    await mcpSquareApi.publishModule(moduleId.value, config, loading)
    ElMessage.closeAll()
    ElMessage.success('服务发布成功')
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    ElMessage.error(`发布服务失败: ${ error.message || '未知错误' }`)
  }
}

// 停止服务
const handleStopService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在停止服务...', duration: 0 })
    await mcpServiceApi.stopService(serviceUuid, loading)
    ElMessage.closeAll()
    ElMessage.success('服务已停止')
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    ElMessage.error(`停止服务失败: ${ error.message || '未知错误' }`)
  }
}

// 启动服务
const handleStartService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在启动服务...', duration: 0 })
    await mcpServiceApi.startService(serviceUuid, loading)
    ElMessage.closeAll()
    ElMessage.success('服务已启动')
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    ElMessage.error(`启动服务失败: ${ error.message || '未知错误' }`)
  }
}

// 卸载服务
const handleUninstallService = async (serviceUuid: string) => {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
        '确定要卸载此服务吗？卸载后将无法恢复。',
        '确认卸载',
        {
          confirmButtonText: '确认卸载',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: '正在卸载服务...', duration: 0 })
    await mcpServiceApi.uninstallService(serviceUuid, loading)
    ElMessage.closeAll()
    ElMessage.success('服务已卸载')
    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElMessage.error(`卸载服务失败: ${ error.message || '未知错误' }`)
    }
  }
}

// 显示编辑对话框
function showEditDialog() {
  // 检查权限
  if (!hasEditPermission.value) {
    ElMessageBox.alert(
        '您没有权限编辑此MCP服务。只有管理员或服务创建者才能编辑。',
        '权限不足',
        { type: 'warning' }
    )
    return
  }

  // 加载分类数据
  loadCategories()

  nextTick(() => {
    editDialogVisible.value = true
  })
}

// 加载分类列表
async function loadCategories() {
  try {
    const response = await mcpGroupApi.listGroup(loading)
    if (response && response.data) {
      categories.value = response.data
    } else {
      categories.value = []
    }
  } catch (error) {
    console.error('加载分类失败', error)
    ElNotification({
      title: '错误',
      message: '加载MCP分类列表失败',
      type: 'error'
    })
  }
}

// 更新分类列表
function updateCategories(newCategories: McpGroup[]) {
  if (newCategories && newCategories.length > 0) {
    categories.value = newCategories
  }
}

// 提交编辑表单
async function submitEditForm(formData: any) {
  updating.value = true
  try {
    const response = await mcpSquareApi.updateModule(moduleInfo.value.id, formData, loading)

    if (response && response.code === 0) {
      ElNotification({
        title: '成功',
        message: 'MCP服务更新成功',
        type: 'success'
      })
      editDialogVisible.value = false

      // 重新加载模块详情
      loadModuleInfo()
    } else {
      ElNotification({
        title: '错误',
        message: response?.message || '更新MCP服务失败',
        type: 'error'
      })
    }
  } catch (error) {
    console.error('更新MCP服务失败:', error)
    ElNotification({
      title: '错误',
      message: '更新MCP服务失败',
      type: 'error'
    })
  } finally {
    updating.value = false
  }
}

// 处理删除模块
async function handleDeleteModule() {
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
        '确定要删除此MCP服务吗？删除后将无法恢复，其关联的所有服务也将被卸载。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: '正在删除服务...', duration: 0 })
    const response = await mcpSquareApi.deleteModule(moduleId.value, loading)
    ElMessage.closeAll()
    if (response && response.code === 0) {
      ElMessage.success('服务已删除')
      // 删除成功后，返回到广场页面
      router.push('/mcp/marketplace')
    } else {
      ElMessage.error(`删除服务失败: ${ response?.message || '未知错误' }`)
    }
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElMessage.error(`删除服务失败: ${ error.message || '未知错误' }`)
    }
  }
}

// 保存代码
async function saveCode(code: string) {
  try {
    await mcpSquareApi.updateModule(moduleId.value, { code }, loading)
    ElNotification({
      title: '成功',
      message: '模块代码已保存',
      type: 'success'
    })
  } catch (error) {
    console.error('保存模块代码失败', error)
    ElNotification({
      title: '错误',
      message: '保存模块代码失败',
      type: 'error'
    })
  }
}

// 查看服务参数
const viewServiceParams = async (service: McpServiceInfo) => {
  try {
    // 获取最新的服务信息
    const response = await mcpServiceApi.getService(service.service_uuid, loading)
    if (response && response.data) {
      currentService.value = response.data
      serviceParamsDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取服务参数失败', error)
    ElMessage.error('获取服务参数失败')
  }
}

// 更新服务参数
const updateServiceParamsFunc = async (params: Record<string, any>) => {
  if (!currentService.value) return

  updatingParams.value = true
  try {
    const body = { ...params }
    // 调用API更新服务参数
    await mcpServiceApi.updateServiceParams(currentService.value.id, body, loading)
    ElMessage.success('服务参数更新成功')
    serviceParamsDialogVisible.value = false

    // 重新加载服务列表
    await loadServices()
  } catch (error) {
    console.error('更新服务参数失败', error)
    ElMessage.error('更新服务参数失败')
  } finally {
    updatingParams.value = false
  }
}

// 页面加载时获取模块详情
onMounted(() => {
  loadUserInfo() // 加载用户信息
  loadModuleInfo()
  loadServices() // 加载服务
})

function goBack() {
  router.push('/mcp/marketplace')
}
</script>

<style lang="scss">
/* 原有样式 */
.marketplace-detail-container {
  width: 100%;
  height: 100%;
  position: relative;

  > header {
    width: 100%;
    height: 56px;
    position: relative;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    padding-left: calc(2 * var(--app-base-px) + 4px);
    border-bottom: 1px solid #e9ecf2;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: normal;
      color: #081126;
      font-weight: 600;
    }
  }

  > main {
    width: 100%;
    height: calc(100% - 56px);
    position: relative;

    .divider {
      width: 1px;
      height: 100%;
      position: relative;
      background-color: #081126;
    }

    .module-info-card,
    .service-card {
      box-shadow: none !important;
      border: none !important;
      background-color: transparent !important;

      &:hover {
        box-shadow: none !important;
        transform: translateY(0) !important;
      }

      .el-card__header {
        border: none !important;
      }

      .el-card__body {
        padding-top: 0 !important;
      }
    }
  }

  .el-drawer__footer {
    border-top: none;
  }
}

.tabs-card {
  border-radius: 0px;
  //box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
  //border: 1px solid rgba(235, 235, 235, 0.8);
  border: none;
  overflow: hidden;
  margin-bottom: 0;

  .service-details-container {
    .markdown-content {
      border: none !important;
    }
  }
}

/* 设定顶部卡片的统一高度 */
.top-cards {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #E9ECF2;
}

.top-card {
  width: 50%;
  height: 300px;

  &:first-child {
    border-right: 1px solid #e9ecf2;
  }
}

.el-tabs {
  .el-tabs__header {
    .el-tabs__nav-wrap {
      &::after {
        opacity: 0;
      }
    }
  }
}

/* 设定下方标签页内容的固定高度和滚动条 */
.tab-content-container {
  height: calc(100vh - 540px);
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #DDE1EB;
  border-radius: 8px;
}

/* 美化滚动条样式 */
.tab-content-container::-webkit-scrollbar {
  width: 8px;
}

.tab-content-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.tab-content-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.tab-content-container::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>