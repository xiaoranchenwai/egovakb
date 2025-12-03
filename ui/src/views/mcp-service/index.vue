<template>
  <div class="mcp-services-container">
    <div class="mcp-services-container-header">
      <h2>MCP服务管理</h2>
    </div>
    <div class="search-box">
      <el-form :model="searchCondition" :label-width="'110px'">
        <el-row :gutter="0">
          <el-col :span="5">
            <el-form-item label="MCP名称:">
              <el-input v-model="searchCondition.name" placeholder="请输入MCP名称" clearable @input="handleSearch"
                        class="search-input">
                <template #suffix>
                  <el-icon>
                    <Search/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="服务类型:">
              <el-select v-model="searchCondition.service_type" placeholder="请选择服务类型" clearable class="status-select">
              <el-option label="全部类型" :value="null"/>
              <el-option v-for="(item,index) in serviceTypeList" :key="item.value" :label="item.text" :value="item.value">
                  <span class="option-text">{{ item.text }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="访问权限:">
              <el-select v-model="searchCondition.is_public" placeholder="请选择访问权限" clearable class="status-select">
                <el-option label="全部" :value="undefined"/>
                <el-option label="公开" :value="true"/>
                <el-option label="私有" :value="false"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="状态:">
              <el-select v-model="searchCondition.status" placeholder="请选择状态" clearable @change="handleSearch"
                         class="status-select">
                <el-option label="全部状态" value=""/>
                <el-option label="运行中" value="running"/>
                <el-option label="已停止" value="stopped"/>
                <el-option label="错误" value="error"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4" class="right">
            <el-icon class="ml-16" @click="toggleShow">
              <ArrowUpBold v-if="expand"/>
              <ArrowDownBold v-else/>
            </el-icon>
            <el-button type="default" class="ml-16" @click="onReset">重置</el-button>
            <el-button type="primary" @click="handleSearch" :loading="loading" class="ml-8">查询</el-button>
          </el-col>
        </el-row>

        <el-row :gutter="0" :class="{ hidden: !expand }">
          <el-col :span="5">
            <el-form-item label="模板名称:">
              <el-select v-model="searchCondition.module_id" placeholder="请选择模板" clearable @clear="handleSearch"
                         @change="handleSearch" class="module-select">
                <el-option v-for="(module, index) in modules" :key="module.id" :label="module.name" :value="module.id">
                  <span class="option-text">{{ index + 1 }}. {{ module.name }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="模板分类:">
              <el-select v-model="searchCondition.protocol_type" placeholder="选择模板分类" clearable class="status-select">
                <el-option v-for="(item,index) in categories" :key="item.id" :label="item.name" :value="item.id">
                  <span class="option-text">{{ index + 1 }}. {{ item.name }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="创建者:">
              <el-select v-model="searchCondition.user_id" placeholder="请选择创建者" clearable @clear="handleSearch"
                         @change="handleSearch" class="user-select">
                <el-option label="全部创建者" :value="null"/>
                <el-option v-for="(user, index) in users" :key="user.id" :label="user.username" :value="user.id">
                  <span class="option-text">{{ index + 1 }}. {{ user.username }}</span>
                  <el-icon v-if="user.is_admin" class="admin-icon">
                    <UserFilled/>
                  </el-icon>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>
    <div class="operate-box">
      <el-button @click="openCreateThirdPartyDialog" round class="add-btn">
        <el-icon class="mr-1">
          <Plus/>
        </el-icon>
        创建第三方服务
      </el-button>
      <el-button @click="goToCreateService" round v-show="false">
        <el-icon class="mr-1">
          <Shop/>
        </el-icon>
        从模板创建
      </el-button>

      <el-button round class="action-button" @click.stop="onBatchStartService">
        <el-icon>
          <VideoPlay/>
        </el-icon>
        <span>启动服务</span>
      </el-button>

      <el-button round class="action-button" @click.stop="onBatchStopService">
        <el-icon>
          <VideoPause/>
        </el-icon>
        <span>停止服务</span>
      </el-button>


      <el-button round class="action-button" @click.stop="onBatchDelService">
        <el-icon color="#FF0000">
          <Delete/>
        </el-icon>
        <span>删除服务</span>
      </el-button>

    </div>

    <div class="mcp-service-result">
      <div class="table-box">
        <div class="abs">
          <el-loading v-model="loading">
            <el-table :data="services" :table-layout="'auto'" height="540" @selection-change="onHandleSelectionChange">
              <el-table-column type="selection" width="55"/>
              <el-table-column type="index" label="序号" width="55"/>

              <el-table-column prop="name" label="MCP服务名称" show-overflow-tooltip/>
              <el-table-column prop="module_name" label="MCP模板名称" show-overflow-tooltip/>
              <el-table-column prop="description" label="MCP模板分类" show-overflow-tooltip/>
              <el-table-column prop="description" label="MCP模板简介" show-overflow-tooltip/>
              <el-table-column prop="username" label="创建者" show-overflow-tooltip/>
              <el-table-column prop="created_at" label="发布时间" show-overflow-tooltip/>

              <el-table-column prop="count" label="调用次数">
                <template #default="{ row }">
                  <span>0</span>
                </template>
              </el-table-column>
              <el-table-column prop="sse_url" label="SSE" show-overflow-tooltip/>
              <el-table-column prop="service_type" label="服务类型" show-overflow-tooltip>
                <template #default="{ row }">
                  <!-- 服务类型标识 -->
                  <el-tag v-if="row.service_type === 1" type="primary" size="small" class="service-type-tag">
                    内置服务
                  </el-tag>
                  <el-tag v-else-if="row.service_type === 2" type="warning" size="small" class="service-type-tag">
                    第三方服务
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_public" label="访问权限" show-overflow-tooltip>
                <template #default="{ row }">
                  <!-- 公开状态标识 -->
                  <el-tag v-if="row.is_public" type="success" size="small" class="public-tag"
                          :class="{ 'clickable-tag': row.can_edit }"
                          @click.stop="row.can_edit && togglePublicStatus(row)">
                    公开
                  </el-tag>
                  <el-tag v-else type="info" size="small" class="private-tag" :class="{ 'clickable-tag': row.can_edit }"
                          @click.stop="row.can_edit && togglePublicStatus(row)">
                    私有
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <span class="status-dot" :class="getStatusClass(row.status)"></span>
                  <span class="status-text">{{ getStatusText(row.status) }}</span>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="110">
                <template #default="{ row }">
                  <div class="inline">
                    <el-dropdown trigger="click" class="mr-2" popper-class="service-dropdown">
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

                    <el-dropdown trigger="click" popper-class="service-dropdown">
                      <a>更多</a>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="edit_app">
                            <a @click.stop="viewServiceParams(row)" class="action-button">
                              <el-icon>
                                <Setting/>
                              </el-icon>
                              <span>配置</span>
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
                            <a @click.stop="handleUninstallService(row.service_uuid)" class="action-button" style="color: #ff0000;">
                              <el-icon color="#ff0000">
                                <Delete/>
                              </el-icon>
                              <span>删除</span>
                            </a>
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-loading>

        </div>
      </div>
      <div class="pagination-box">
        <el-config-provider :locale="zhCn">
          <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
                         :background="true" layout="total, sizes, prev, pager, next, jumper" :total="total"
                         @size-change="handleSizeChange" @current-change="handleCurrentChange" class="pagination"/>
        </el-config-provider>
      </div>
    </div>

    <!-- 服务参数查看/编辑对话框 -->
    <ServiceParamsDialog v-model="serviceParamsDialogVisible" :service="currentService" :loading="updatingParams"
                         @confirm="updateServiceParamsFunc" @cancel="serviceParamsDialogVisible = false"/>

    <!-- 创建第三方服务对话框 -->
    <el-drawer v-model="createThirdPartyDialogVisible" title="创建第三方MCP服务" width="50%" :destroy-on-close="true"
               class="create-dialog" direction="rtl">
      <el-form ref="thirdPartyFormRef" :model="thirdPartyForm" :rules="thirdPartyRules" label-width="90px"
               class="third-party-form">
        <el-form-item label="服务名称:" prop="service_name">
          <el-input v-model="thirdPartyForm.service_name" placeholder="请输入服务名称" clearable/>
        </el-form-item>

        <el-form-item label="SSE URL:" prop="sse_url">
          <el-input v-model="thirdPartyForm.sse_url" placeholder="请输入第三方MCP服务的SSE URL，如：https://example.com/sse"
                    clearable/>
        </el-form-item>

        <el-form-item label="服务描述:" prop="description" class="required-dot">
          <el-input v-model="thirdPartyForm.description" type="textarea" :rows="3" placeholder="请输入服务描述（可选）" clearable/>
        </el-form-item>

        <el-form-item label="访问权限:" prop="is_public">
          <el-radio-group v-model="thirdPartyForm.is_public">
            <el-radio :label="false">私有</el-radio>
            <el-radio :label="true">公开</el-radio>
          </el-radio-group>
          <div class="form-tip">
            <span>私有：仅自己可见和使用</span><br>
            <span>公开：所有用户可见和使用</span>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createThirdPartyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createThirdPartyService" :loading="creatingThirdParty">
            创建服务
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>

import { ref, onMounted, reactive, toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  DocumentCopy,
  Connection,
  VideoPlay,
  VideoPause,
  Delete,
  Refresh,
  Plus,
  Setting,
  Lock,
  Search,
  UserFilled,
  Shop
} from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import mcpServiceApi from '@/api/mcp-service'
import type { McpServiceInfo, ServiceQueryCondition } from '@/api/type/mcp-service'
import mcpSquareApi from '@/api/mcp-square'
import mcpAuthApi from '@/api/mcp-auth'
import { copyTextToClipboard } from '../../utils/copy'
import ServiceParamsDialog from './components/service-params-setting.vue'
import mcpGroupApi from '@/api/mcp-group'
// '@/components/service-params-dialog/index.vue'

const router = useRouter()
const loading = ref(false)
const services = ref<McpServiceInfo[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const serviceTypeList: Array<any> = [{ value: 1, text: "内置服务" }, {value: 2, text:"第三方服务"}];
// 模块和用户数据用于下拉选择
const modules = ref<{ id: number, name: string, description: string }[]>([])
const users = ref<{ id: number, username: string, is_admin: boolean }[]>([])
const categories = ref<Array<any>>([])
// 搜索条件
const searchCondition = reactive<ServiceQueryCondition>({
  name: '',
  module_id: null,
  status: '',
  user_id: null,
  protocol_type: null,
  service_type: undefined
})

// 服务参数对话框相关
const serviceParamsDialogVisible = ref(false)
const currentService = ref<McpServiceInfo | null>(null)
const updatingParams = ref(false)

// 创建第三方服务对话框相关
const createThirdPartyDialogVisible = ref(false)
const thirdPartyFormRef = ref()
const thirdPartyForm = ref({
  service_name: '',
  sse_url: '',
  description: '',
  is_public: false
})
const thirdPartyRules = ref({
  service_name: [ { required: true, message: '请输入服务名称', trigger: 'blur' } ],
  sse_url: [
    { required: true, message: '请输入SSE URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  is_public: [ { required: true, message: '请选择访问权限', trigger: 'change' } ]
})
const creatingThirdParty = ref(false)
const expand = ref(false)

const toggleShow = () => {
  expand.value = !expand.value
}
// 加载模块数据
const loadModules = async () => {
  try {
    const response = await mcpSquareApi.listModules()
    if (response && response.data) {
      modules.value = response.data.map((module: any) => ({
        id: module.id,
        name: module.name,
        description: module.description || ''
      }))
    }
  } catch (error) {
    console.error('获取模块列表失败', error)
  }
}
const loadCategories = async () => {

  try {
    const res = await mcpGroupApi.listGroup()
    if (res.code === 200) {
      categories.value = res.data ?? [];
    } else {
      ElMessage.error(res.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('加载分类失败:', error)
  } finally {

  }
}
// 加载用户数据
const loadUsers = async () => {
  try {
    const response = await mcpAuthApi.getAllUsers()
    if (response && response.data) {
      users.value = response.data.map((user: any) => ({
        id: user.id,
        username: user.username,
        is_admin: user.is_admin || false
      }))
    }
  } catch (error: any) {
    // 非管理员可能没有权限查看用户列表，这是正常的
    console.log('获取用户列表失败（可能无权限）', error.message)
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
  loadServices()
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadServices()
}

// 处理页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  loadServices()
}

// 加载服务列表（分页）
const loadServices = async () => {
  loading.value = true
  try {
    const params = {
      paging: {
        page: currentPage.value,
        size: pageSize.value
      },
      condition: {
        ...toRaw(searchCondition),
        name: searchCondition.name || undefined,
        module_id: searchCondition.module_id,
        status: searchCondition.status || undefined,
        user_id: searchCondition.user_id
      }
    }

    const response = await mcpServiceApi.listServicesPage(params, loading)
    if (response && response.data) {
      services.value = response.data.items || []
      total.value = response.data.total || 0
      currentPage.value = response.data.page || 1
      pageSize.value = response.data.size || 10
    } else {
      services.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载服务列表失败', error)
    ElMessage.error('加载服务列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新服务
const refreshServices = () => {
  loadServices()
}

// 前往创建服务页面
const goToCreateService = () => {
  router.push('/mcp/marketplace')
}

// 打开创建第三方服务对话框
const openCreateThirdPartyDialog = () => {
  // 重置表单
  thirdPartyForm.value = {
    service_name: '',
    sse_url: '',
    description: '',
    is_public: false
  }
  createThirdPartyDialogVisible.value = true
}

// 启动服务
const handleStartService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在启动服务...', duration: 0 })
    await mcpServiceApi.startService(serviceUuid, loading)
    ElMessage.closeAll()
    ElNotification({
      title: '成功',
      message: '服务已启动',
      type: 'success'
    })
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    ElNotification({
      title: '错误',
      message: `启动服务失败: ${ error.message || '未知错误' }`,
      type: 'error'
    })
  }
}

// 停止服务
const handleStopService = async (serviceUuid: string) => {
  try {
    ElMessage.info({ message: '正在停止服务...', duration: 0 })
    await mcpServiceApi.stopService(serviceUuid, loading)
    ElMessage.closeAll()
    ElNotification({
      title: '成功',
      message: '服务已停止',
      type: 'success'
    })
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    ElNotification({
      title: '错误',
      message: `停止服务失败: ${ error.message || '未知错误' }`,
      type: 'error'
    })
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
    ElNotification({
      title: '成功',
      message: '服务已卸载',
      type: 'success'
    })
    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `卸载服务失败: ${ error.message || '未知错误' }`,
        type: 'error'
      })
    }
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

// 查看服务参数
const viewServiceParams = async (service: McpServiceInfo) => {
  try {
    // 获取最新的服务信息
    const response = await mcpServiceApi.getService(service.service_uuid, loading)
    if (response && response.data) {
      currentService.value = response.data
      // 初始化表单
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

// 切换服务公开状态
const togglePublicStatus = async (service: McpServiceInfo) => {
  if (!service.can_edit) {
    ElMessage.warning('您没有权限编辑此服务')
    return
  }

  const newStatus = !service.is_public
  const statusText = newStatus ? '公开' : '私有'

  try {
    await ElMessageBox.confirm(
        `确定要将服务设置为${ statusText }状态吗？`,
        '确认修改',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: `正在设置服务为${ statusText }状态...`, duration: 0 })
    await mcpServiceApi.updateServiceVisibility(service.id, { is_public: newStatus }, loading)
    ElMessage.closeAll()
    ElMessage.success(`服务已设置为${ statusText }状态`)

    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElMessage.error(`设置服务状态失败: ${ error.message || '未知错误' }`)
    }
  }
}

// 获取服务状态样式类名
const getStatusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'status-running'
    case 'stopped':
      return 'status-stopped'
    case 'error':
      return 'status-error'
    default:
      return 'status-unknown'
  }
}

// 获取服务状态文字
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '运行中'
    case 'stopped':
      return '已停止'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 跳转到模块详情
const viewModuleDetail = (moduleId: number) => {
  router.push(`/mcp/marketplace/${ moduleId }`)
}

// 创建第三方服务
const createThirdPartyService = async () => {
  if (!thirdPartyFormRef.value) return

  try {
    await thirdPartyFormRef.value.validate()
    creatingThirdParty.value = true

    const response = await mcpServiceApi.createThirdPartyService(thirdPartyForm.value, loading)

    if (response && response.data) {
      ElNotification({
        title: '成功',
        message: '第三方服务创建成功',
        type: 'success'
      })
      createThirdPartyDialogVisible.value = false
      await loadServices() // 重新加载服务列表
    }
  } catch (error: any) {
    ElNotification({
      title: '错误',
      message: `创建第三方服务失败: ${ error.message || '未知错误' }`,
      type: 'error'
    })
  } finally {
    creatingThirdParty.value = false
  }
}

// 页面加载时获取服务列表
onMounted(async () => {
  await Promise.all([
    loadServices(),
    loadModules(),
    loadCategories(),
    loadUsers()
  ])
})

const multipleSelections = ref<Array<any>>([])
const onHandleSelectionChange = (rows: any) => {
  multipleSelections.value = rows
}

const onBatchStartService = async () => {
  if (!multipleSelections.value.length) {
    ElMessage.warning('请先勾选需要启动的服务')
    return
  }
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
        `确定要启动这${ multipleSelections.value.length }个服务吗？`,
        '确认',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: '正在启动服务...', duration: 0 })
    await Promise.all(multipleSelections.value.map(g => mcpServiceApi.startService(g.service_uuid)))
    ElMessage.closeAll()
    ElNotification({
      title: '成功',
      message: '服务已启动',
      type: 'success'
    })
    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `启动服务失败: ${ error.message || '未知错误' }`,
        type: 'error'
      })
    }
  }
}

const onBatchStopService = async () => {
  if (!multipleSelections.value.length) {
    ElMessage.warning('请先勾选需要停止的服务')
    return
  }
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
        `确定要停止这${ multipleSelections.value.length }个服务吗？`,
        '确认',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: '正在停止服务...', duration: 0 })
    await Promise.all(multipleSelections.value.map(g => mcpServiceApi.stopService(g.service_uuid)))
    ElMessage.closeAll()
    ElNotification({
      title: '成功',
      message: '服务已停止',
      type: 'success'
    })
    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `停止服务失败: ${ error.message || '未知错误' }`,
        type: 'error'
      })
    }
  }
}

const onBatchDelService = async () => {
  if (!multipleSelections.value.length) {
    ElMessage.warning('请先勾选需要删除的服务')
    return
  }
  try {
    // 弹出确认框
    await ElMessageBox.confirm(
        `确定要删除这${ multipleSelections.value.length }个服务吗？`,
        '确认',
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning'
        }
    )

    ElMessage.info({ message: '正在删除服务...', duration: 0 })
    await Promise.all(multipleSelections.value.map(g => mcpServiceApi.stopService(g.service_uuid)))
    ElMessage.closeAll()
    ElNotification({
      title: '成功',
      message: '服务已删除',
      type: 'success'
    })
    // 重新加载服务列表
    await loadServices()
  } catch (error: any) {
    ElMessage.closeAll()
    if (error !== 'cancel') {
      ElNotification({
        title: '错误',
        message: `删除服务失败: ${ error.message || '未知错误' }`,
        type: 'error'
      })
    }
  }
}

const onReset = () => {
  searchCondition.name= '';
  searchCondition.module_id= null;
  searchCondition.status= '';
  searchCondition.user_id= null;
  searchCondition.protocol_type= null;
  searchCondition.service_type = '';
  searchCondition.is_public = undefined;
  handleSearch();
};
</script>

<style lang="scss">
.mcp-services-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f5f7fa;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: var(--app-view-padding);
  box-sizing: border-box;

  .mcp-services-container-header {
    width: 100%;
    height: 56px;
    min-height: 56px;
    position: relative;
    padding-left: 20px;
    box-sizing: border-box;
    background-color: #fff;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(221, 221, 221, 0.8);

    h2 {
      color: #081126;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .search-box {
    width: 100%;
    position: relative;
    padding: 12px 15px 0;
    box-sizing: border-box;
    background-color: #FFFFFF;

    &::after {
      content: "";
      width: calc(100% - 30px);
      height: 1px;
      position: absolute;
      bottom: 0;
      left: 15px;
      background-color: #E9ECF2;
    }

    .el-form {
      .el-form-item {
        margin-bottom: 15px;
        .el-form-item__label {
          padding-left: 5px;
        }
      }
      .right {
        text-align: right;
        .el-icon {
          cursor: pointer;
        }
      }
    }

    .el-input,
    .el-select {
      width: 100%;
    }

    .hidden {
      height: 0;
      display: none;
    }
  }

  .operate-box {
    width: 100%;
    height: 56px;
    position: relative;
    background-color: #FFFFFF;
    padding-left: 20px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    .add-btn {
      color: #3388FF;
    }
  }

  .mcp-service-result {
    flex: 1;
    width: 100%;
    position: relative;
    padding: 0 20px 10px;
    box-sizing: border-box;
    background-color: #fff;
    display: flex;
    flex-direction: column;

    .table-box {
      flex: 1;
      width: 100%;
      position: relative;

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

    .pagination-box {
      width: 100%;
      height: 45px;
      position: relative;
      display: flex;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
    }
  }
}

.services-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #fff;
  z-index: 10;
  border-bottom: 1px solid rgba(221, 221, 221, 0.8);
  border-radius: 8px 8px 0 0;
}

.header-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
}

.search-input {
  width: 200px;
}

.status-select,
.module-select,
.user-select {
  width: 140px;
}

.option-text {
  flex: 1;
}

.admin-icon {
  color: #409eff;
  margin-left: 8px;
}

.mcp-services-content {
  flex: 1;
  padding: 24px;
  background-color: #fff;
  border-radius: 0 0 8px 8px;

  .el-row {
    height: calc(100% - 50px);
    overflow-y: auto;
  }
}

.search-button {
  border-radius: 20px;
  padding: 8px 20px;
  font-weight: 500;
}

.service-col {
  margin-bottom: 24px;
}

.service-card {
  height: 100%;
  border-radius: 16px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.service-card:hover {
  /* transform: translateY(-4px); */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.service-running {
  border-left: 4px solid #67c23a;
}

.card-content {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.service-status {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  position: relative;
  display: inline-block;
}

.status-running {
  background-color: #11C79B;
  // box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

// .status-running::after {
//   content: '';
//   position: absolute;
//   top: -3px;
//   left: -3px;
//   right: -3px;
//   bottom: -3px;
//   border-radius: 50%;
//   background-color: rgba(103, 194, 58, 0.2);
//   animation: pulse 2s infinite;
// }

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }

  70% {
    transform: scale(1.5);
    opacity: 0;
  }

  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.status-stopped {
  background-color: #A8B4C8;
  // box-shadow: 0 0 0 3px rgba(144, 147, 153, 0.2);
}

.status-error {
  background-color: #FF4433;
  // box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2);
}

.status-unknown {
  background-color: #e6a23c;
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.2);
}

.status-text {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.public-tag {
  margin-left: 4px;
  background-color: #F0F9FF !important;
  border: none !important;
  width: 40px;
  height: 24px;
  border-radius: 4px;
  color: #3388FF;
}

.private-tag {
  margin-left: 4px;
  background-color: #E6FFF4 !important;
  border: none !important;
  width: 40px;
  height: 24px;
  border-radius: 4px;
  color: #11C79B;
}

.service-type-tag {
  margin-right: 4px;
}

.clickable-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.service-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-button {
  font-size: 12px;
}

.no-permission-icon {
  color: #909399;
  font-size: 16px;
}

.service-info {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.service-title-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.service-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
  white-space: nowrap;
  min-width: 40px;
}

.service-value {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
  flex: 1;
  min-width: 0;
}

.service-description {
  font-size: 13px;
  color: #606266;
  margin-top: 8px;
  display: block;
}

.service-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 8px;
}

.detail-row .service-title-row {
  margin-bottom: 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.detail-value {
  font-size: 13px;
  color: #303133;
}

.url-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f5f7fa;
  border-radius: 6px;
  padding: 6px 10px;
}

.url-text {
  font-size: 13px;
  cursor: pointer;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy-button {
  padding: 2px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 20px 0;
  border-top: 1px solid #e9ecf2;
  background-color: #fff;
}

.pagination {
  /* 可以添加自定义分页样式 */
}

.empty-container {
  padding: 80px 0;
  text-align: center;
}

.create-dialog {
  border-radius: 0px;
}

.third-party-form {
  padding: 0;
}

.form-tip {
  width: 100%;
  font-size: 12px;
  color: #6B7A99;
  margin-top: 8px;
  line-height: 1.4;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  .el-button + .el-button {
    margin-left: 0px;
  }
}

.mr-1 {
  margin-right: 8px;
}

/* 适配暗色主题 */
:root[data-theme="dark"] .mcp-services-container {
  background-color: #141414;
}

:root[data-theme="dark"] .services-header,
:root[data-theme="dark"] .mcp-services-content {
  background-color: #1d1e1f;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.2);
}

:root[data-theme="dark"] .service-card {
  background-color: rgba(48, 49, 51, 0.8);
  border-color: #484848;
}

:root[data-theme="dark"] .add-service-card {
  background-color: rgba(48, 49, 51, 0.5);
  border-color: #606266;
}

:root[data-theme="dark"] .add-service-card:hover {
  border-color: #409eff;
}

:root[data-theme="dark"] .url-container {
  background-color: rgba(0, 0, 0, 0.2);
}

.service-dropdown {
  
  border-color: #F1F6FA !important;
  box-shadow: 0 4px 20px 0 #0043ca12 !important;
  border-radius: 4px;

  .el-dropdown-menu {
    padding: 8px !important;
    .action-button {
      display: flex;
      align-items: center;
    }
  }
}
</style>
