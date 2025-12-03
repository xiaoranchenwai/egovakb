<template>
  <div class="full-container markplace">
    <div class="content-container">
      <div class="main-content">
        <div class="sidebar">
          <div class="sidebar-header">
            <h3>MCP模板分类</h3>
            <el-icon @click="showCategoryModal = true" color="#A8B4C8" title="新增分类">
              <Plus />
            </el-icon>
          </div>
          <div class="sidebar-search">
            <el-input placeholder="请输入模板名称搜索" suffix-icon="Search" clearable>
            </el-input>
          </div>
          <div class="category-list">
            <el-menu :default-active="categoryId === null ? 'all' : categoryId.toString()"
              @select="handleCategorySelect">
              <el-menu-item index="all" class="category-item">
                <el-icon>
                  <Folder />
                </el-icon>
                <span>全部({{ totalCount }})</span>
              </el-menu-item>
              <el-menu-item v-for="category in categories" :key="category.id" :index="category.id.toString()"
                class="category-item">
                <AppIcon class="app-mcp-square"></AppIcon>
                <component :is="iconMap['app-mcp-square'].iconReader()" class="el-icon app-icon"></component>
                <span>{{ category.name }} ({{ category.modules_count }})</span>
                <div class="toolbox" @click.stop>
                  <el-dropdown trigger="click">
                    <el-button type="primary" link>
                      <el-icon>
                        <MoreFilled color="#A8B4C8" />
                      </el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit_app"><el-icon>
                            <EditPen />
                          </el-icon>编辑</el-dropdown-item>
                        <el-dropdown-item command="delete_app">
                          <el-icon style="color: red;">
                            <Delete />
                          </el-icon>
                          <span style="color: red;">删除</span>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

              </el-menu-item>
            </el-menu>
          </div>
        </div>
        <div class="content-divider"></div>

        <div class="main-panel">
          <div class="panel-header">
            <h2>MCP广场</h2>
          </div>
          <div class="tabs-panel">
            <el-tabs v-model="activeName">
              <el-tab-pane v-for="item in tabPanes" :label="item.label" :name="item.name"></el-tab-pane>
            </el-tabs>
          </div>

          <div class="search-bar">
            <el-form inline :model="formModel" :label-width="'80px'">
              <el-form-item label="模板名称:">
                <el-input v-model="searchKeyword" placeholder="按名称搜索" class="search-input custom" clearable
                  @input="handleSearch">
                  <template #suffix>
                    <el-icon>
                      <Search />
                    </el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="访问权限:">
                <el-select placeholder="请选择访问权限">
                  <el-option v-for="item in 5" :key="item" :label="item" :value="item"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="创建者:">
                <el-select placeholder="请选择创建者">
                  <el-option v-for="item in 5" :key="item" :label="item" :value="item"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item class="right">
                <el-button type="default" class="ml-8" @click="loadModules">
                  重置
                </el-button>
                <el-button type="primary" class="ml-8" @click="loadModules">
                  查询
                </el-button>
              </el-form-item>
            </el-form>

          </div>

          <div class="tool-bar">
            <el-button round @click="showCreateModuleModal = true">
              <el-icon>
                <Plus />
              </el-icon>新增
            </el-button>
          </div>

          <div class="content">
            <div class="abs">

              <div class="modules-grid">
                <el-loading v-model="loading">
                  <el-row :gutter="15">
                    <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" v-for="module in modules" :key="module.id"
                      class="mb-16">
                      <el-card shadow="hover" class="module-card" @click="viewModuleDetail(module)">
                        <div class="card-icon">
                        </div>
                        <el-text class="card-title" truncated>
                          {{ module.name }}
                        </el-text>
                        <div class="card-tag">
                          <el-tag v-if="module.is_public" size="small" class="public-tag">公开</el-tag>
                          <el-tag v-else size="small" class="private-tag">私有</el-tag>
                        </div>
                        <div class="card-time">
                          <el-text class="mb-2" truncated>
                            创建于 {{ module.created_at || '暂无日期' }}
                          </el-text>
                        </div>
                        <div class="card-content">
                          <div class="card-desc">
                            <el-text line-clamp="2">
                              {{ module.description || '无描述' }}
                            </el-text>
                          </div>
                          <div class="info flex">
                            <el-avatar :size="18" src="/user.png" />
                            <el-text class="username" truncated>
                              {{ module.username || " 暂无作者" }}
                            </el-text>
                            <el-text class="ml-8 create">
                              创建
                            </el-text>
                          </div>
                        </div>
                        <template #footer>
                          <div class="card-footer" @click.stop>
                            <el-text>服务数</el-text>
                            <el-text class="ml-8">7</el-text>
                            <el-divider direction="vertical" />

                            <el-text>工具数</el-text>
                            <el-text class="ml-8">4</el-text>
                            <el-divider direction="vertical" />

                            <el-text>关联应用</el-text>
                            <el-text class="ml-8">4</el-text>

                            <el-dropdown trigger="click" popper-class="app-dropdown">
                              <el-button text @click.stop>
                                <el-icon>
                                  <MoreFilled color="#A8B4C8" />
                                </el-icon>
                              </el-button>
                              <template #dropdown>
                                <el-dropdown-menu>
                                  <el-dropdown-item @click="openPublishModal(module)">
                                    <el-icon>
                                      <Document />
                                    </el-icon>
                                    发布服务
                                  </el-dropdown-item>
                                  <el-dropdown-item @click.stop="copyModule(module)">
                                    <el-icon>
                                      <CopyDocument />
                                    </el-icon>
                                    复制模板
                                  </el-dropdown-item>
                                  <el-dropdown-item v-if="module.can_edit"
                                    @click.stop="showCategorySelectModal(module)">
                                    <el-icon>
                                      <Edit />
                                    </el-icon>
                                    编辑分类
                                  </el-dropdown-item>
                                  <el-dropdown-item v-if="module.can_edit" @click.stop="confirmDeleteModule(module)">
                                    <el-icon>
                                      <Delete />
                                    </el-icon>
                                    删除
                                  </el-dropdown-item>
                                </el-dropdown-menu>
                              </template>
                            </el-dropdown>

                          </div>
                        </template>
                      </el-card>
                    </el-col>
                  </el-row>
                </el-loading>
              </div>
            </div>
          </div>
          <!-- 分页组件 -->
          <div v-if="!loading && total > 0" class="pagination-container">
            <el-config-provider :locale="zhCn">
              <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[8, 12, 16, 20, 40, 60]"
                :background="true" layout="total, sizes, prev, pager, next, jumper" :total="total"
                @size-change="handleSizeChange" @current-change="handleCurrentChange" />
            </el-config-provider>
          </div>
        </div>
      </div>
    </div>

    <!-- 分类管理模态框 -->
    <el-dialog v-model="showCategoryModal" title="分类管理" width="600px">
      <el-loading v-model="categoryLoading">
        <div class="category-actions">
          <el-button round @click="showAddCategoryModal = true"><el-icon>
              <Plus />
            </el-icon>新增分类</el-button>
          <el-button round @click="loadCategories" :loading="categoryLoading">刷新分类</el-button>
        </div>

        <el-table :data="categories" :table-layout="'auto'">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="modules_count" label="模块数量" width="100" />
          <el-table-column label="操作" width="110">
            <template #default="scope">
              <el-button type="primary" link @click="editCategory(scope.row)">编辑</el-button>
              <el-popconfirm title="确定要删除此分类吗?" @confirm="deleteGroup(scope.row.id)">
                <template #reference>
                  <el-button type="danger" link>删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-loading>
    </el-dialog>

    <!-- 添加分类模态框 -->
    <el-dialog v-model="showAddCategoryModal" title="添加分类" @confirm="saveCategory" :loading="savingCategory">
      <el-form :model="categoryForm" label-position="top">
        <el-form-item label="分类名称" prop="name" :rules="[{ required: true, message: '请输入分类名称' }]">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description" class="required-dot">
          <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类描述" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategoryModal = false">取消</el-button>
        <el-button type="primary" @click="saveCategory" :loading="savingCategory">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑分类模态框 -->
    <el-dialog v-model="showEditCategoryModal" title="编辑分类" @confirm="updateGroup" :loading="savingCategory">
      <el-form :model="categoryForm" label-position="top">
        <el-form-item label="分类名称" prop="name" :rules="[{ required: true, message: '请输入分类名称' }]">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description" class="required-dot">
          <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类描述" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCategoryModal = false">取消</el-button>
        <el-button type="primary" @click="updateGroup" :loading="savingCategory">确定</el-button>
      </template>
    </el-dialog>

    <!-- 发布服务模态框 -->
    <el-dialog v-model="publishModalVisible" title="发布服务" @confirm="publishService" :loading="publishing">
      <el-form :model="publishForm" label-position="top">
        <el-form-item label="服务名称" prop="name" :rules="[{ required: true, message: '请输入服务名称' }]">
          <el-input v-model="publishForm.name" placeholder="请输入服务名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description" class="required-dot">
          <el-input v-model="publishForm.description" type="textarea" placeholder="请输入服务描述" :rows="4" />
        </el-form-item>
        <!-- 根据模块配置参数动态生成表单 -->
        <template v-if="currentModule && currentModule.config_schema">
          <div v-for="(schema, key) in currentModule.config_schema" :key="key">
            <el-form-item :label="schema.title || key" class="required-dot">
              <el-input v-model="publishForm.config_params[key]" :placeholder="schema.description || `请输入${key}`" />
            </el-form-item>
          </div>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="publishModalVisible = false">取消</el-button>
        <el-button type="primary" @click="publishService" :loading="publishing">确定</el-button>
      </template>
    </el-dialog>

    <!-- 选择分类模态框 -->
    <el-dialog v-model="showSelectCategoryModal" title="选择分类" @confirm="setModuleCategory" :loading="settingCategory">
      <el-radio-group v-model="selectedCategoryId">
        <el-radio :label="null">无分类</el-radio>
        <el-radio v-for="category in categories" :key="category.id" :label="category.id">
          {{ category.name }}
        </el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="showSelectCategoryModal = false">取消</el-button>
        <el-button type="primary" @click="setModuleCategory" :loading="settingCategory">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新建模板模态框 -->
    <el-dialog v-model="showCreateModuleModal" title="新建模板" width="60%" :destroy-on-close="true" body-class="pt-0">
      <ModuleForm :categories="categories" :loading="creatingModule" :isEdit="false" @submit="createModule"
        @cancel="showCreateModuleModal = false" @categoriesLoaded="updateCategories" />
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, computed, watch, toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElConfigProvider } from 'element-plus'
import { More, View, Edit, Search, Folder, Grid, Document, Delete, CopyDocument, Plus, MoreFilled } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import mcpSquareApi from '@/api/mcp-square'
import mcpGroupApi from '@/api/mcp-group'
import type { McpModuleInfo } from '@/api/type/mcp-square'
import type { McpGroup } from '@/api/type/mcp-group'
import ModuleForm from '@/views/marketplace/components/ModuleForm.vue'
import { iconMap } from '@/components/icons/index';
const router = useRouter()
const loading = ref(false)
const modules = ref<McpModuleInfo[]>([])
const categoryId = ref<number | null>(null)
const searchKeyword = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(8)
const total = ref(0)

// 分类相关
const categoryLoading = ref(false)
const categories = ref<McpGroup[]>([])
const showCategoryModal = ref(false)
const showAddCategoryModal = ref(false)
const showEditCategoryModal = ref(false)
const savingCategory = ref(false)
const categoryForm = reactive({
  id: null as number | null,
  name: '',
  description: ''
})

// 发布服务相关
const publishModalVisible = ref(false)
const publishing = ref(false)
const currentModule = ref<McpModuleInfo | null>(null)
const publishForm = reactive({
  name: '',
  description: '',
  is_public: false,
  config_params: {} as Record<string, any>
})

// 选择分类相关
const showSelectCategoryModal = ref(false)
const settingCategory = ref(false)
const selectedCategoryId = ref<number | null>(null)
const moduleToUpdateCategory = ref<McpModuleInfo | null>(null)

// 新建模板相关
const showCreateModuleModal = ref(false)
const creatingModule = ref(false)

// 获取模块状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'active': 'success',
    'inactive': 'warning',
    'error': 'danger',
    'default': 'info'
  }
  return typeMap[status] || typeMap.default
}

// 处理分类选择
const handleCategorySelect = (index: string) => {
  categoryId.value = index === 'all' ? null : Number(index);
  currentPage.value = 1; // 重置到第一页
  loadModules();
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1; // 重置到第一页
  loadModules();
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page;
  loadModules();
}

// 处理页大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1; // 重置到第一页
  loadModules();
}

// 加载模块列表（分页）
const loadModules = async () => {
  loading.value = true
  try {
    const params = {
      paging: {
        page: currentPage.value,
        size: pageSize.value
      },
      condition: {
        category_id: categoryId.value,
        keyword: searchKeyword.value || undefined
      }
    }

    const res = await mcpSquareApi.listModulesPage(params, loading)
    if (res.code === 200) {
      modules.value = res.data.items
      total.value = res.data.total
      currentPage.value = res.data.page
      pageSize.value = res.data.size
    } else {
      ElMessage.error(res.message || '获取模块列表失败')
    }
  } catch (error) {
    console.error('加载模块失败:', error)
    ElMessage.error('加载模块失败')
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await mcpGroupApi.listGroup(categoryLoading)
    if (res.code === 200) {
      categories.value = res.data
    } else {
      ElMessage.error(res.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('加载分类失败:', error)
    ElMessage.error('加载分类失败')
  } finally {
    categoryLoading.value = false
  }
}

// 查看模块详情
const viewModuleDetail = (module: McpModuleInfo) => {
  router.push(`/mcp/marketplace/${module.id}`)
}

// 保存分类
const saveCategory = async () => {
  if (!categoryForm.name) {
    ElMessage.error('分类名称不能为空')
    return
  }

  savingCategory.value = true
  try {
    const res = await mcpGroupApi.createGroup({
      name: categoryForm.name,
      description: categoryForm.description
    }, savingCategory)

    if (res.code === 200) {
      ElMessage.success('分类创建成功')
      showAddCategoryModal.value = false
      categoryForm.name = ''
      categoryForm.description = ''
      await loadCategories()
    } else {
      ElMessage.error(res.message || '创建分类失败')
    }
  } catch (error) {
    console.error('创建分类失败:', error)
    ElMessage.error('创建分类失败')
  } finally {
    savingCategory.value = false
  }
}

// 编辑分类
const editCategory = (category: McpGroup) => {
  categoryForm.id = category.id
  categoryForm.name = category.name
  categoryForm.description = category.description || ''
  showEditCategoryModal.value = true
}

// 更新分类
const updateGroup = async () => {
  if (!categoryForm.name || !categoryForm.id) {
    ElMessage.error('分类名称不能为空')
    return
  }

  savingCategory.value = true
  try {
    const res = await mcpGroupApi.updateGroup(categoryForm.id, {
      name: categoryForm.name,
      description: categoryForm.description
    }, savingCategory)

    if (res.code === 200) {
      ElMessage.success('分类更新成功')
      showEditCategoryModal.value = false
      categoryForm.id = null
      categoryForm.name = ''
      categoryForm.description = ''
      await loadCategories()
    } else {
      ElMessage.error(res.message || '更新分类失败')
    }
  } catch (error) {
    console.error('更新分类失败:', error)
    ElMessage.error('更新分类失败')
  } finally {
    savingCategory.value = false
  }
}

// 删除分类
const deleteGroup = async (id: number) => {
  categoryLoading.value = true
  try {
    console.log('删除分类', id, categoryLoading.value)
    const res = await mcpGroupApi.deleteGroup(id, categoryLoading)
    if (res.code === 200) {
      ElMessage.success('分类删除成功')
      await loadCategories()
    } else {
      ElMessage.error(res.message || '删除分类失败')
    }
  } catch (error) {
    console.error('删除分类失败:', error)
    ElMessage.error('删除分类失败')
  } finally {
    categoryLoading.value = false
  }
}

// 显示选择分类模态框
const showCategorySelectModal = (module: McpModuleInfo) => {
  moduleToUpdateCategory.value = module
  selectedCategoryId.value = module.category_id || null
  showSelectCategoryModal.value = true
}

// 设置模块分类
const setModuleCategory = async () => {
  if (!moduleToUpdateCategory.value) return

  settingCategory.value = true
  try {
    const res = await mcpGroupApi.updateModuleGroup(
      moduleToUpdateCategory.value.id,
      selectedCategoryId.value,
      settingCategory
    )

    if (res.code === 200) {
      ElMessage.success('分类设置成功')
      showSelectCategoryModal.value = false
      await loadModules()
    } else {
      ElMessage.error(res.message || '设置分类失败')
    }
  } catch (error) {
    console.error('设置分类失败:', error)
    ElMessage.error('设置分类失败')
  } finally {
    settingCategory.value = false
  }
}

// 显示发布服务模态框
const openPublishModal = (module: McpModuleInfo) => {
  currentModule.value = module
  publishForm.name = module.name
  publishForm.description = module.description || ''
  publishForm.config_params = {}
  publishModalVisible.value = true
}

// 新建模板
const createModule = async (moduleForm: any) => {
  creatingModule.value = true
  try {
    const res = await mcpSquareApi.createModule(moduleForm, creatingModule)

    if (res.code === 200) {
      ElMessage.success('模板创建成功')
      showCreateModuleModal.value = false
      await loadModules()
    } else {
      ElMessage.error(res.message || '创建模板失败')
    }
  } catch (error) {
    console.error('创建模板失败:', error)
    ElMessage.error('创建模板失败')
  } finally {
    creatingModule.value = false
  }
}

// 复制模板
const copyModule = (module: McpModuleInfo) => {
  ElMessageBox.prompt('请输入新模板名称', '复制模板', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: `${module.name} - 副本`,
    inputValidator: (value) => {
      if (!value) {
        return '模板名称不能为空'
      }
      return true
    }
  }).then(({ value }) => {
    cloneModuleWithName(module, value)
  }).catch(() => {
    // 用户取消操作
  })
}

// 执行模板克隆
const cloneModuleWithName = async (sourceModule: McpModuleInfo, newName: string) => {
  loading.value = true
  try {
    const res = await mcpSquareApi.cloneModule(sourceModule.id, {
      name: newName,
      is_public: sourceModule.is_public,
      // 以下字段会在后端自动复制，不需要在前端传递
      // code、config_schema、markdown_docs等会在后端处理
    }, loading)

    if (res.code === 200) {
      ElMessage.success('模板复制成功')
      await loadModules()
    } else {
      ElMessage.error(res.message || '复制模板失败')
    }
  } catch (error) {
    console.error('复制模板失败:', error)
    ElMessage.error('复制模板失败')
  } finally {
    loading.value = false
  }
}

// 发布服务
const publishService = async () => {
  if (!currentModule.value) return
  if (!publishForm.name) {
    ElMessage.error('服务名称不能为空')
    return
  }

  publishing.value = true
  try {
    const res = await mcpSquareApi.publishModule(currentModule.value.id, {
      name: publishForm.name,
      description: publishForm.description,
      ...publishForm.config_params
    }, publishing)

    if (res.code === 200) {
      ElMessage.success('服务发布成功')
      publishModalVisible.value = false
      await loadModules()
    } else {
      ElMessage.error(res.message || '发布服务失败')
    }
  } catch (error) {
    console.error('发布服务失败:', error)
    ElMessage.error('发布服务失败')
  } finally {
    publishing.value = false
  }
}

// 确认删除模块
const confirmDeleteModule = (module: McpModuleInfo) => {
  ElMessageBox.confirm(
    `确定要删除模块 "${module.name}" 吗？如果有关联的服务，也会被停止和删除。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteModule(module.id)
  }).catch(() => {
    // 用户取消删除操作
  })
}

// 删除模块
const deleteModule = async (id: number) => {
  loading.value = true
  try {
    const res = await mcpSquareApi.deleteModule(id, loading)
    if (res.code === 200) {
      ElMessage.success('模块删除成功')
      await loadModules()
    } else {
      ElMessage.error(res.message || '删除模块失败')
    }
  } catch (error) {
    console.error('删除模块失败:', error)
    ElMessage.error('删除模块失败')
  } finally {
    loading.value = false
  }
}

// 更新分类列表
const updateCategories = (newCategories: McpGroup[]) => {
  if (newCategories && newCategories.length > 0) {
    categories.value = newCategories
  }
}

onMounted(async () => {
  await loadCategories()
  await loadModules()
})

const totalCount = computed(() => {
  const total = categories.value.reduce((val: number, next: any) => val + (next.modules_count || 0), 0);
  return total;
});

const tabPanes = ref<Array<any>>([
  { label: "全部", name: "all" },
  { label: "公开", name: "public" },
  { label: "私有", name: "private" }
]);
const activeName = ref(tabPanes.value[0]["name"]);
const formModel = ref({});
</script>

<style scoped lang="scss">
.full-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: #f5f7fa;
}

.content-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.main-content {
  display: flex;
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.sidebar {
  width: 280px;
  height: 100%;
  border-right: none;
  overflow-y: auto;
  padding: var(--app-base-px);
  box-sizing: border-box;

  .sidebar-header {
    width: 100%;
    height: 40px;
    padding: 0 calc(var(--app-base-px) + 4px) 0 calc(var(--app-base-px) + 4px);
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 14px;
      font-weight: normal;
      color: #081126;
      font-weight: 600;
    }

    .el-icon {
      cursor: pointer;
    }
  }

  .sidebar-search {
    padding: calc(var(--app-base-px) + 4px);

    .el-input {
      :deep(.el-input__wrapper) {
        border-radius: 16px;
      }
    }
  }

  .category-list {
    .el-menu {
      border-right: none;

      .category-item {
        height: 40px;
        line-height: 40px;
        padding-left: 12px !important;
        padding-right: 12px !important;

        .el-icon {
          margin-right: 10px;
          color: #a8b4c8;
        }

        &:hover {
          .toolbox {
            display: flex;
          }
        }

      }
    }

    .toolbox {
      position: absolute;
      right: 0;
      display: none;
      align-items: center;
    }
  }
}

.content-divider {
  width: 1px;
  height: 100%;
  background-color: #e9ecf2;
}

.main-panel {
  flex: 1;
  height: 100%;
  padding: var(--app-base-px) 0;
  box-sizing: border-box;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 40px;
    padding-left: calc(2 * var(--app-base-px) + 4px);
    // padding: 20px;
    // border-bottom: 1px solid #e9ecf2;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: normal;
      color: #081126;
      font-weight: 600;
    }

    .header-actions {
      display: flex;
      gap: 10px;

      .add-button {
        border-radius: 4px;
      }
    }
  }

  .tabs-panel {
    height: 40px;
    margin: calc(var(--app-base-px)) 0 0;
    box-sizing: border-box;

    .el-tabs {
      .el-tabs__nav-scroll {
        padding-left: var(--app-base-px);
      }
    }
  }

  .content {
    width: 100%;
    height: calc(100% - 260px);
    position: relative;

    .abs {
      width: 100%;
      height: 100%;
      position: absolute;
      overflow-y: auto;
    }
  }

  .modules-grid {
    height: calc(100% - 70px);
    padding: 0 20px 20px 20px;
    box-sizing: border-box;
  }

  .pagination-container {
    height: 70px;
    width: 100%;
    position: relative;
    padding: 0 20px;
    box-sizing: border-box;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid #e9ecf2;
    background-color: #fff;
  }
}

.module-card {
  position: relative;
  // height: 250px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e9ecf2;
  border-radius: 4px;

  &:hover {
    box-shadow: 0 5px 20px 0 rgba(0, 67, 202, 0.1);
  }

  .card-icon {
    position: absolute;
    top: 16px;
    left: 16px;
    color: #3e7de9;
    width: 20px;
    height: 20px;
    background-image: url("../../assets/mcp/mcp.png");
    background-size: 100% 100%;
  }

  .card-tag {
    position: absolute;
    top: 15px;
    right: 15px;

    .public-tag {
      background-color: #F0F9FF;
      height: 24px;
      border-radius: 4px;
      color: #3388FF;
      border: none;
      font-weight: 500;
    }

    .private-tag {
      background-color: #E6FFF4;
      height: 24px;
      border-radius: 4px;
      color: #11C79B;
      border: none;
      font-weight: 500;
    }
  }

  .card-title {
    max-width: calc(100% - 110px);
    position: absolute;
    top: 15px;
    left: 50px;
    font-size: 16px;
    font-weight: 600;
    color: #081126;
  }

  .card-time {
    width: 100%;
    height: 22px;
    position: absolute;
    top: 40px;
    left: 16px;

    .el-text {
      font-size: 14px;
      color: #6B7A99;
    }
  }

  .card-content {
    margin-top: 40px;
    padding: 0;


    .card-desc {
      padding-top: 15px;
      height: 50px;
      max-height: 50px;
      position: relative;
      font-weight: 400;
      font-size: 14px;
      color: #223355;
      line-height: 22px;
      overflow: hidden;
    }

    .info {
      height: 46px;
      line-height: 46px;
      position: relative;
      font-weight: 400;
      font-size: 14px;
      color: #6b7a99;
      display: flex;
      align-items: center;
      // border-bottom: 1px solid #e9ecf2;

      .username {
        font-weight: 400;
        font-size: 14px;
        color: #a8b4c8;
        margin-left: 5px;
        max-width: calc(100% - 165px);
      }

      .create {
        color: #6B7A99;
      }

      .time-right {
        margin-right: -10px;
      }
    }
  }
}

.category-actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

// 添加app-dropdown样式
.app-dropdown {
  box-shadow: 0 2px 24px 0 #F5F7FA !important;
}

// 添加时间右对齐样式
.time-right {
  position: absolute;
  right: 0;
}

// 添加宽度类
.w-150px {
  width: 150px;
}

// 添加底部间距
.mb-16 {
  margin-bottom: 16px;
}

// 添加底部间距2
.mb-2 {
  margin-bottom: 2px;
}

// 添加左边距
.ml-8 {
  margin-left: 8px;
}
</style>

<style lang="scss">
.markplace {
  .el-input.custom {
    .el-input__wrapper {
      border-radius: 15px !important;
    }
  }

  .el-card {
    --el-card-padding: 20px;
    border-radius: 4px;
    border: 1px solid #e9ecf2;

    .el-card__body {
      padding: var(--el-card-padding) var(--el-card-padding) 0;

      .card-header {
        padding-top: 12px;
      }
    }

    .el-card__footer {
      height: 52px !important;
      padding: 0 var(--el-card-padding);
      border-top: none;

      .card-footer {
        height: 100%;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        border-top: 1px solid #e9ecf2; // var(--el-card-border-color);

        .el-icon {
          color: #223355;
        }

        .el-button {
          &:hover {
            background-color: #F5F7FA !important;
          }
        }

        .el-dropdown {
          position: absolute;
          right: 20px;
        }
      }
    }

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

    &:hover {
      box-shadow: 0 5px 20px 0 #0043ca1a;
    }
  }

  .tabs-panel {
    .el-tabs {
      .el-tabs__nav-scroll {
        padding-left: calc(2*var(--app-base-px));
      }
    }
  }

  .search-bar {
    padding: 12px 20px;
    box-sizing: border-box;
    position: relative;

    &::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 20px;
      width: calc(100% - 40px);
      height: 1px;
      background-color: #e9ecf2;
    }

    .el-form {
      .el-form-item {
        margin-bottom: 0;

        &.right {
          .el-form-item__content {
            justify-content: flex-end;
          }

        }
      }
    }

    .search-input {
      width: 270px;

      .el-input__wrapper {
        border-radius: 4px;
      }
    }

    .el-select {
      width: 270px;
    }
  }

  .tool-bar {
    width: 100%;
    height: 56px;
    position: relative;
    padding: 12px 20px;
    box-sizing: border-box;
  }
}

.pt-0 {
  padding-top: 0 !important;
}
</style>