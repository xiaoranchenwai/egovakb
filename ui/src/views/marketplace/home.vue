<template>
  <div class="marketplace-home">
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
          <el-input v-model="formModel.keyword" placeholder="按名称搜索" class="search-input" clearable
                    @input="handleSearch">
            <template #suffix>
              <el-icon>
                <Search/>
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="访问权限:">
          <el-select v-model="formModel.can_edit" placeholder="请选择访问权限">
            <el-option v-for="item in canEditList" :key="item.label" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="创建者:">
          <el-select v-model="formModel.creator" placeholder="请选择创建者">
            <el-option v-for="item in members" :key="item.id" :label="item.username" :value="item.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item class="right">
          <el-button type="default" class="ml-8" @click="onReset">
            重置
          </el-button>
          <el-button type="primary" class="ml-8" @click="loadModules">
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="tool-bar">
      <el-button round @click="onNewAdd" style="color: #3388FF">
        <el-icon color="#3388FF">
          <Plus/>
        </el-icon>
        新增
      </el-button>
    </div>

    <div class="content">
      <div class="abs">
        <div class="modules-grid">
          <InfiniteScroll :size='moduleList.length' :total='paginationConfig.total'
                          :page_size='paginationConfig.page_size' :current_page='paginationConfig.current_page'
                          @update:current_page='(page: number) => paginationConfig.current_page = page'
                          @load='loadModules'
                          :loading='loading'>
            <el-row :gutter="15">
              <el-col :xs="24" :sm="12" :md="8" :lg="8" :xl="8" v-for="module in dataList" :key="module.id"
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
                      <el-avatar :size="18" src="/ui/user.png"/>
                      <el-text class="username" truncated>
                        {{ module.username || ' 暂无作者' }}
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
                    

                      <el-dropdown trigger="hover" popper-class="marketplace-dropdown">
                        <el-button text @click.stop>
                          <el-icon>
                            <MoreFilled color="#A8B4C8"/>
                          </el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item @click="openPublishModal(module)">
                              <el-icon>
                                <Document/>
                              </el-icon>
                              发布服务
                            </el-dropdown-item>
                            <el-dropdown-item @click.stop="copyModule(module)">
                              <el-icon>
                                <CopyDocument/>
                              </el-icon>
                              复制模板
                            </el-dropdown-item>
                            <el-dropdown-item v-if="module.can_edit" @click.stop="showCategorySelectModal(module)">
                              <el-icon>
                                <Edit/>
                              </el-icon>
                              编辑分类
                            </el-dropdown-item>
                            <el-dropdown-item v-if="module.can_edit" @click.stop="confirmDeleteModule(module)" style="color:#ff0000">
                              <el-icon color="#FF0000">
                                <Delete/>
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
          </InfiniteScroll>
        </div>
      </div>
    </div>

    <!-- 发布服务模态框 -->
    <el-drawer v-model="publishModalVisible" title="发布服务" @confirm="publishService" :loading="publishing" direction="rtl">
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
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>

import { computed, onMounted, reactive, ref, watch, getCurrentInstance, onBeforeMount, inject } from 'vue'
import { ElMessage, ElMessageBox, ElConfigProvider, ElDialog } from 'element-plus'
import {
  More,
  View,
  Edit,
  Search,
  Folder,
  Grid,
  Document,
  Delete,
  CopyDocument,
  Plus,
  MoreFilled
} from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import type { McpModuleInfo } from '@/api/type/mcp-square'
import mcpSquareApi from '@/api/mcp-square'
import mcpGroupApi from '@/api/mcp-group'
import teamApi from '@/api/team'
import { useRoute, useRouter } from 'vue-router'
import ModuleForm from '@/views/marketplace/components/ModuleForm.vue'

const instance = getCurrentInstance();
const route = useRoute()
const router = useRouter()
const paginationConfig = reactive({
  current_page: 1,
  page_size: 10,
  total: 0
})
const moduleList = ref<Array<McpModuleInfo>>([])
const loading = ref<boolean>(false)
const id = ref<string | number | null>(null)
const categories = ref<Array<any>>([])
const searchKeyword = ref('')
const tabPanes = ref<Array<any>>([
  { label: '全部', name: 'all' },
  { label: '公开', name: 'public' },
  { label: '私有', name: 'private' }
])
const activeName = ref(tabPanes.value[0]['name'])
const formModel = reactive<any>({
  keyword: undefined,
  can_edit: undefined,
  creator: undefined
})
const canEditList = ref([ { label:"可编辑", value: true }, { label:"不可编辑", value: false } ]);
const showCreateModuleModal = ref(false)
const creatingModule = ref(false)

const dataList = computed(() => {
  switch (activeName.value) {
    case 'all':
      return moduleList.value
    case 'public':
      return moduleList.value.filter((g: any) => g.is_public)
    case 'private':
      return moduleList.value.filter((g: any) => !g.is_public)
    default:
      return moduleList.value
  }
})
const handleSearch = () => {
}
const onReset = () => {
  reset()
  loadModules()
}
const loadModules = async () => {
  loading.value = true
  try {
    const queryModel = {
      paging: {
        size: paginationConfig.page_size,
        page: paginationConfig.current_page
      },
      condition: {
        category_id: id.value ? Number(id.value) : null,
        keyword: formModel.keyword || searchKeyword.value,
        creator: formModel.creator,
        can_edit: formModel.can_edit
      }
    }
    const res = await mcpSquareApi.listModulesPage(queryModel, loading)
    if (res.code === 200) {
      paginationConfig.total = res?.data?.total || 0
      paginationConfig.current_page = res?.data?.page || 1
      paginationConfig.page_size = res?.data?.size || 10

      moduleList.value = [ ...moduleList.value, ...res.data.items ]
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

const viewModuleDetail = (module: McpModuleInfo) => {
  router.push(`/mcp/marketplace-detail/${ module.id }`)
}
// 发布服务
const openPublishModal = (module: McpModuleInfo) => {
  currentModule.value = module
  publishForm.name = module.name
  publishForm.description = module.description || ''
  publishForm.config_params = {}
  publishModalVisible.value = true
}
// 复制模板
const copyModule = (module: McpModuleInfo) => {
  ElMessageBox.prompt('请输入新模板名称', '复制模板', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: `${ module.name } - 副本`,
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
      is_public: sourceModule.is_public
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
// 确认删除模块
const confirmDeleteModule = (module: McpModuleInfo) => {
  ElMessageBox.confirm(
      `确定要删除模块 "${ module.name }" 吗？如果有关联的服务，也会被停止和删除。`,
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
const editCategory: any = inject("editCategory");
// 显示选择分类模态框
const showCategorySelectModal = (module: McpModuleInfo) => {
  editCategory?.(module);
}
const reset = () => {
  formModel.keyword = "";
  formModel.can_edit = "";
  formModel.creator = "";
  paginationConfig.current_page = 1
  paginationConfig.page_size = 10
  paginationConfig.total = 0
  moduleList.value = []
}
onMounted(() => {
  reset()
  loadCategories()
})
const loadCategories = async () => {
  try {
    const res = await mcpGroupApi.listGroup()
    if (res.code === 200) {
      categories.value = res.data
    } else {
      ElMessage.error(res.message || '获取分类列表失败')
    }
  } catch (error) {
    console.error('加载分类失败:', error)
    ElMessage.error('加载分类失败')
  } finally {

  }
}
watch(() => route.query, () => {
  const { categoryId } = route.query
  console.log(categoryId)

  if (categoryId) {
    id.value = categoryId.toString()
  } else {
    id.value = ''
  }
  reset()
  loadModules()
}, { immediate: true, deep: true })

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

// 更新分类列表
const updateCategories = (newCategories: Array<any>) => {
  if (newCategories && newCategories.length > 0) {
    categories.value = newCategories
  }
}


const onNewAdd = () => {
  router.push({
    path: '/mcp/marketplace/add',
    replace: false
  })
}

onBeforeMount(() => {
  getTeamMembers();
});
const members = ref<Array<any>>([]);
const getTeamMembers = async () => {
  const res = await teamApi.getTeamMember();
  members.value = res?.data ?? [];
};

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
</script>

<style lang="scss">
.marketplace-home {
  width: 100%;
  height: 100%;
  position: relative;
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
    height: calc(100% - 200px);
    position: relative;

    .abs {
      width: 100%;
      height: 100%;
      position: absolute;
      overflow-y: auto;
    }
  }

  .modules-grid {
    height: calc(100%);
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
      left: 46px;
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

  // marketplace-dropdown样式
  .marketplace-dropdown {
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
        padding-left: calc(2 * var(--app-base-px));
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
      display: flex;
      .el-form-item {
        margin-bottom: 0;

        &.right {
          flex: 1;
          margin-right: 0;
          .el-form-item__content {
            justify-content: flex-end;
          }
        }
      }
    }

    .search-input {
      width: 250px;

      .el-input__wrapper {
        border-radius: 4px;
      }
    }

    .el-select {
      width: 250px;
    }
  }

  .tool-bar {
    width: 100%;
    height: 56px;
    position: relative;
    padding: 12px 20px;
    box-sizing: border-box;
  }

  .el-button.is-text:not(.is-disabled):focus-visible {
    outline: none;
  }
}

// marketplace-dropdown样式
.marketplace-dropdown {
  
  border-color: #F1F6FA !important;
  box-shadow: 0 4px 20px 0 #0043ca12 !important;
  border-radius: 4px;
  // --el-dropdown-menuItem-hover-fill: #F5F7FA !important;
  // --el-dropdown-menuItem-hover-color: #3388FF;
  .el-dropdown-menu {
    padding: 8px !important;
  }
}
</style>