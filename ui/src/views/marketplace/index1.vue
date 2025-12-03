<template>
  <div class="mcp-marketplace">
    <div class="container">
      <div class="sidebar">
        <div class="sidebar-header">
          <h3>MCP模板分类</h3>
          <el-icon @click="showAddCategoryModal = true" color="#A8B4C8" title="新增分类">
            <Plus/>
          </el-icon>
        </div>

        <div class="sidebar-search">
          <el-input placeholder="请输入模板名称搜索" suffix-icon="Search" clearable>
          </el-input>
        </div>

        <div class="category-list">
          <el-menu :default-active="!categoryId ? 'all' : categoryId.toString()" @select="handleCategorySelect">
            <el-menu-item index="all" class="category-item">
              <el-icon>
                <Folder/>
              </el-icon>
              <span>全部({{ totalCount }})</span>
            </el-menu-item>
            <el-menu-item v-for="category in categories" :key="category.id" :index="category.id.toString()"
                          class="category-item">
              <AppIcon class="app-mcp-square"></AppIcon>
              <component :is="iconMap['app-mcp-square-active'].iconReader()" class="el-icon app-icon"></component>
              <span>{{ category.name }} ({{ category.modules_count }})</span>
              <div class="toolbox" @click.stop>
                <el-dropdown trigger="click" @command="onHandleCommand($event,category)">
                  <el-button type="primary" link>
                    <el-icon>
                      <MoreFilled color="#A8B4C8"/>
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit_app">
                        <el-icon>
                          <EditPen/>
                        </el-icon>
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item command="delete_app">
                        <el-icon style="color: red;">
                          <Delete/>
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

      <div class="content-container">
        <router-view></router-view>
      </div>
    </div>

    <!-- 分类管理模态框 -->
    <el-drawer v-model="showCategoryModal" title="分类管理" width="600px" direction="rtl">
      <el-loading v-model="categoryLoading">
        <div class="category-actions">
          <el-button round @click="showAddCategoryModal = true">
            <el-icon>
              <Plus/>
            </el-icon>
            新增分类
          </el-button>
          <el-button round @click="loadCategories" :loading="categoryLoading">刷新分类</el-button>
        </div>

        <el-table :data="categories" :table-layout="'auto'">
          <el-table-column prop="id" label="ID" width="80"/>
          <el-table-column prop="name" label="名称"/>
          <el-table-column prop="description" label="描述"/>
          <el-table-column prop="modules_count" label="模块数量" width="100"/>
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
    </el-drawer>

    <!-- 添加分类模态框 -->
    <el-drawer v-model="showAddCategoryModal" title="新增分类" @confirm="saveCategory" :loading="savingCategory"
               direction="rtl">
      <el-form :model="categoryForm" label-position="top" label-width="90px">
        <el-form-item label="分类名称:" prop="name" :rules="[{ required: true, message: '请输入分类名称' }]">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"/>
        </el-form-item>
        <el-form-item label="描述:" prop="description">
          <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类描述" :rows="4"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategoryModal = false">取消</el-button>
        <el-button type="primary" @click="saveCategory" :loading="savingCategory">确定</el-button>
      </template>
    </el-drawer>

    <!-- 编辑分类模态框 -->
    <el-drawer v-model="showEditCategoryModal" title="编辑分类" @confirm="updateGroup" :loading="savingCategory"
               direction="rtl">
      <el-form :model="categoryForm" label-position="top" label-width="90px">
        <el-form-item label="分类名称:" prop="name" :rules="[{ required: true, message: '请输入分类名称' }]">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"/>
        </el-form-item>
        <el-form-item label="描述:" prop="description">
          <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类描述" :rows="4"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCategoryModal = false">取消</el-button>
        <el-button type="primary" @click="updateGroup" :loading="savingCategory">确定</el-button>
      </template>
    </el-drawer>
  </div>
</template>
<script lang="ts" setup>
import { computed, onMounted, reactive, ref, provide } from 'vue'
import type { McpGroup } from '@/api/type/mcp-group'
import { iconMap } from '@/components/icons/index'
import mcpGroupApi from '@/api/mcp-group'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import mcpServiceApi from '@/api/mcp-service'

const router = useRouter()
const categories = ref<McpGroup[]>([])
const categoryLoading = ref(false)
const showCategoryModal = ref(false)
const categoryId = ref<any>(null)
const showAddCategoryModal = ref(false)
const showEditCategoryModal = ref(false)
const savingCategory = ref(false)
const categoryForm = reactive({
  id: null as number | null,
  name: '',
  description: ''
})
const totalCount = computed(() => {
  const total = categories.value.reduce((val: number, next: any) => val + (next.modules_count || 0), 0)
  return total
})
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
const handleCategorySelect = (index: string) => {
  categoryId.value = index === 'all' ? undefined : (+index)
  router.push({
    path: '/mcp/marketplace/index',
    query: {
      categoryId: categoryId.value
    }
  })
}
onMounted(async () => {
  await loadCategories()
})

const onHandleCommand = async (command: string | number, row: any) => {
  switch (command) {
    case 'edit_app':
      editCategory(row)
      break
    case 'delete_app':
      await ElMessageBox.confirm(
          '确定要删除模板分类吗？删除后将无法恢复。',
          '确认删除',
          {
            confirmButtonText: '确认删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
      )

      ElMessage.info({ message: '正在删除分类...', duration: 0 })
      await deleteGroup(row.id)
      ElMessage.closeAll()
      break
  }
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
provide("editCategory",editCategory);
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
</script>
<style lang="scss">
.mcp-marketplace {
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background-color: #f5f7fa;
  position: relative;

  .container {
    width: 100%;
    height: 100%;
    position: relative;
    background-color: #FFFFFF;
    display: flex;
    justify-content: flex-start;

    .content-container {
      flex: 1;
      height: 100%;
      position: relative;
    }
  }

  .sidebar {
    width: 280px;
    height: 100%;
    border-right: none;
    overflow-y: auto;
    padding: var(--app-base-px);
    box-sizing: border-box;
    border-right: 1px solid #e9ecf2;

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
        .el-input__wrapper {
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

  .el-form-item--label-top .el-form-item__label {
    position: relative;
  }
  .el-form-item.is-required:not(.is-no-asterisk).asterisk-left>.el-form-item__label-wrap>.el-form-item__label:before, 
  .el-form-item.is-required:not(.is-no-asterisk).asterisk-left>.el-form-item__label:before {
    position: absolute;
    left: -8px;
    margin-right: unset;
  }
}
</style>