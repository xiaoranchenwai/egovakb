<template>
  <div class="group-drawer">
    <!-- 头部 -->
    <div class="header">
      <h4>应用分组</h4>
      <el-button type="primary" link @click="handleShowAll">
        <el-icon>
          <List />
        </el-icon>
        全部应用
      </el-button>
    </div>

    <!-- 搜索框 -->
    <div class="search">
      <el-input v-model="searchKey" placeholder="请输入关键字搜索" clearable suffix-icon="Search" />
    </div>

    <!-- 分组树 -->
    <div class="tree-container">
      <el-tree ref="treeRef" :data="groupTree" :props="defaultProps" node-key="id" highlight-current
        @node-click="handleNodeClick" default-expand-all>
        <template #default="{ node, data }">
          <div class="custom-node">
            <div class="label" @click.stop='settingApplication(data)'>
              <el-icon v-if="data.target_type === 'GROUP' && !node.expanded">
                <Folder />
              </el-icon>
              <el-icon v-else-if="data.target_type === 'GROUP' && node.expanded">
                <FolderOpened />
              </el-icon>
              <el-avatar v-else-if="data.avatar !== '/ui/favicon.ico' && data.target_type === 'APPLICATION'"
                :src="data.avatar" :size='26' shape="square" fit="scale-down" class="application-tree-avatar" />
              <el-icon v-else-if="data.avatar === '/ui/favicon.ico' && data.target_type === 'APPLICATION'">
                <ChatLineRound />
              </el-icon>
              <el-icon v-else-if="data.target_type === 'APPLICATION'">
                <ChatLineRound />
              </el-icon>
              <el-text truncated>
                {{ node.label }}
              </el-text>
            </div>
            <div class="actions" v-if="data.target_type === 'GROUP'" @click.stop>
              <el-dropdown trigger="click" @command="(cmd: any) => handleCommand(cmd, data)">
                <el-button type="primary" link>
                  <el-icon>
                    <MoreFilled color="#A8B4C8"/>
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <!-- <el-dropdown-item command="edit">编辑</el-dropdown-item> -->
                    <el-dropdown-item command="add_app">添加应用</el-dropdown-item>
                    <!-- <el-dropdown-item command="delete" divided>删除</el-dropdown-item> -->
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div class="actions" v-else-if="data.target_type === 'APPLICATION'">
              <el-dropdown trigger="click" @command="(cmd: any) => handleCommand(cmd, data)">
                <el-button type="primary" link>
                  <el-icon>
                    <MoreFilled color="#A8B4C8"/>
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="delete">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- 编辑/创建对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建分组' : '编辑分组'" width="500px"
      destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分组名称:" prop="name">
          <el-input v-model="form.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="上级分组:">
          <el-select v-model="form.parent_id" clearable placeholder="请选择上级分组"
            :disabled="!!currentGroup?.id && isParentDisabled">
            <el-option v-for="(group, i) in availableParents" :key="group.id" :label="group.name + '(' + i + ')'"
              :value="group.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加应用对话框 -->
    <el-dialog v-model="appDialogVisible" title="添加应用到分组" width="500px" destroy-on-close>
      <div v-loading="appLoading">
        <el-form label-width="5em">
          <el-form-item label="选择应用:">
            <el-select v-model="selectedAppId" filterable placeholder="请选择应用" style="width: 100%">
              <el-option v-for="(app, i) in availableApps" :key="app.id" :label="'(' + (i + 1) + ')' + app.name"
                :value="app.id" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="appDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addAppToGroup" :loading="addAppLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import useStore from '../../../stores'
import { ElMessage, ElMessageBox } from 'element-plus'
import groupApi from '../../../api/group'
import applicationApi from '../../../api/application'
import { ChatLineRound, Folder, FolderAdd, List, MoreFilled } from '@element-plus/icons-vue'
import { isWorkFlow } from '@/utils/application'
import { useRouter } from 'vue-router'
const router = useRouter()
// 定义接口
interface Application {
  id: string
  name: string
  // 其他应用属性
}

interface GroupDetail {
  id: string
  group_id: string
  target_type: string
  target_id: string
  target_name: string
  user_id: string
  create_time: string
  update_time: string
}

interface Group {
  id: string
  name: string
  parent_id: string | null
  user_id: string
  target_type: string
  create_time: string
  update_time: string
  children: (Group | GroupDetail)[]
  details?: GroupDetail[]
}

// 修复命令处理函数的类型
type CommandType = 'edit' | 'delete' | 'add_app';

const store = useStore()
const emit = defineEmits(['update:selectedGroup'])

const loading = ref(false)
const searchKey = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const submitLoading = ref(false)
const currentGroup = ref<Group | null>(null)
const formRef = ref()
const groupList = ref<Group[]>([])

// 应用相关状态
const appDialogVisible = ref(false)
const appLoading = ref(false)
const addAppLoading = ref(false)
const selectedAppId = ref<string>('')
const availableApps = ref<Application[]>([])
const selectedGroupForApp = ref<Group | null>(null)

const form = ref({
  name: '',
  parent_id: undefined as string | undefined
})

const rules = {
  name: [
    { required: true, message: '请输入分组名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const defaultProps = {
  children: 'children',
  label: 'name'
}

// 可选的父分组列表(排除当前分组及其子分组)
const availableParents = computed(() => {
  if (!currentGroup.value?.id) return groupList.value
  return groupList.value.filter((g: Group) => {
    return g.id !== currentGroup.value!.id &&
      !isChildGroup(g.id, currentGroup.value!.id)
  })
})

// 判断是否为子分组
function isChildGroup(parentId: string, childId: string): boolean {
  const group = groupList.value.find((g: Group) => g.id === childId)
  if (!group) return false
  if (group.parent_id === parentId) return true
  if (group.parent_id) {
    return isChildGroup(parentId, group.parent_id)
  }
  return false
}

// 创建分组
function createGroup() {
  dialogType.value = 'create'
  currentGroup.value = null
  form.value = {
    name: '',
    parent_id: undefined
  }
  dialogVisible.value = true
}

function settingApplication(row: any) {
  if (row.target_type !== 'APPLICATION') {
    console.log('click group node', row)
    emit('update:selectedGroup', row)
    return
  }
  if (isWorkFlow(row.type)) {
    router.push({ path: `/application/${row.target_id}/WORK_FLOW/flow` })
  } else {
    router.push({ path: `/application/${row.target_id}/${row.type}/setting` })
  }
}

// 编辑分组
function editGroup(group: Group) {
  dialogType.value = 'edit'
  currentGroup.value = group
  form.value = {
    name: group.name,
    parent_id: group.parent_id || undefined // 将 null 转换为 undefined
  }
  dialogVisible.value = true
}

// 删除分组
async function deleteGroup(group: Group) {
  try {
    await ElMessageBox.confirm(
      '删除分组将同时删除其下所有应用的分组关系，是否继续？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await groupApi.deleteGroup(group.id)
    ElMessage.success('删除成功')
    await getGroupTree() // 替换 store.dispatch('loadGroups')
  } catch (error) {
    console.error(error)
  }
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true

    if (dialogType.value === 'create') {
      await groupApi.createGroup(form.value)
      ElMessage.success('创建成功')
    } else {
      await groupApi.updateGroup(currentGroup.value!.id, form.value)
      ElMessage.success('更新成功')
    }

    await getGroupTree() // 替换 store.dispatch('loadGroups')
    dialogVisible.value = false
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

// 处理搜索
function handleSearch() {
  // 触发重新计算 groupTree
}

// 处理下拉菜单命令
function handleCommand(cmd: CommandType, data: Group | GroupDetail) {
  if (cmd === 'edit' && data.target_type === 'GROUP') {
    editGroup(data as Group)
  } else if (cmd === 'delete') {
    if (data.target_type === 'GROUP') {
      deleteGroup(data as Group)
    } else if (data.target_type === 'APPLICATION') {
      deleteApplication(data as GroupDetail)
    }
  } else if (cmd === 'add_app' && data.target_type === 'GROUP') {
    openAddAppDialog(data as Group)
  }
}

// 打开添加应用对话框
async function openAddAppDialog(group: Group) {
  selectedGroupForApp.value = group
  appDialogVisible.value = true
  selectedAppId.value = ''
  appLoading.value = true

  try {
    // 获取可用的应用列表
    const response = await applicationApi.getAllAppilcation({})
    if (response && response.data) {
      availableApps.value = response.data.map((app: any) => app)
    }
  } catch (error) {
    console.error('获取应用列表失败', error)
    ElMessage.error('获取应用列表失败')
  } finally {
    appLoading.value = false
  }
}

// 添加应用到分组
async function addAppToGroup() {
  if (!selectedAppId.value || !selectedGroupForApp.value) {
    ElMessage.warning('请选择应用')
    return
  }

  addAppLoading.value = true
  try {
    await groupApi.createGroupDetails({
      group: selectedGroupForApp.value.id,
      target_type: 'APPLICATION',
      target_id: selectedAppId.value
    })

    ElMessage.success('添加应用成功')
    appDialogVisible.value = false
    await getGroupTree()
  } catch (error) {
    console.error('添加应用失败', error)
    ElMessage.error('添加应用失败')
  } finally {
    addAppLoading.value = false
  }
}

// 添加删除应用的函数
async function deleteApplication(detail: GroupDetail) {
  try {
    await ElMessageBox.confirm(
      '确定要从分组中移除此应用吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await groupApi.deleteGroupDetails(detail.id)
    ElMessage.success('移除成功')
    // 重新加载数据
    const params = {
      target_type: 'APPLICATION'
    }
    const response = await groupApi.getGroupDetailsTree(params)
    if (response && response.data) {
      groupList.value = response.data
    }
  } catch (error) {
    console.error(error)
  }
}

// 过滤后的分组树
const groupTree = computed(() => {
  if (!groupList.value.length) return []

  // 如果有搜索关键词，则过滤整个树
  if (searchKey.value) {
    return filterTree(JSON.parse(JSON.stringify(groupList.value)), searchKey.value.toLowerCase())
  }
  console.log('groupList.value', groupList.value)
  // 没有搜索关键词，直接返回原始数据
  return groupList.value
})

// 递归过滤树
function filterTree(groups: (Group | GroupDetail)[], keyword: string): (Group | GroupDetail)[] {
  return groups.filter(group => {
    // 检查当前节点是否匹配
    const isMatch = 'name' in group && group.name.toLowerCase().includes(keyword)

    // 递归过滤子节点
    if ('children' in group && group.children && group.children.length) {
      group.children = filterTree(group.children, keyword)
    }

    // 如果当前节点匹配或者有匹配的子节点，则保留
    return isMatch || ('children' in group && group.children && group.children.length > 0)
  })
}

async function getGroupTree() {
  try {
    loading.value = true
    const params = {
      target_type: 'APPLICATION'
    }
    const response = await groupApi.getGroupDetailsTree(params)
    if (response && response.data) {
      // 直接使用API返回的树形结构
      groupList.value = response.data
    }
  } catch (error) {
    console.error('加载分组数据失败', error)
  } finally {
    loading.value = false
  }
}

// 加载分组数据
onMounted(async () => {
  await getGroupTree()
})

// 处理节点点击
function handleNodeClick(data: Group) {
  if (data.target_type === 'GROUP') {
    // console.log('click group node', data)
    emit('update:selectedGroup', data)
  }
}

// 显示全部应用
function handleShowAll() {
  // console.log('handleShowAll')
  emit('update:selectedGroup', null)
}

// 计算当前分组是否禁用父分组选择
const isParentDisabled = computed(() => {
  if (!currentGroup.value) return false
  // 如果有子分组，则不能修改父分组
  return groupList.value.some((g: Group) => g.parent_id === currentGroup.value?.id)
})
</script>

<style lang="scss" scoped>
.group-drawer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color);
  border-righupdateSt: 1px solid var(--el-border-color-light);

  .header {
    padding: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--el-border-color-light);

    h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .search {
    padding: 16px;
    border-bottom: 1px solid var(--el-border-color-light);
  }

  .tree-container {
    flex: 1;
    overflow: auto;
    padding: 16px;

    :deep(.el-tree) {
      // 移除树的背景色
      background: none;

      // 调整树节点
      .el-tree-node {

        // 设置节点间距
        &__content {
          height: 40px;
          padding-right: 8px;
          border-radius: 4px;
          margin-bottom: 4px;
          transition: all 0.2s ease;

          &:hover {
            background-color: #F0F9FF; // var(--el-fill-color-light);
          }
        }

        // 展开图标样式
        &__expand-icon {
          padding: 8px;
          color: var(--el-color-info);

          &::after {
            content: "";
            width: 12px;
            height: 12px;
            line-height: 12px;
            position: absolute;
            background-image: url("../../../assets/application/arrow_right.png");
            background-repeat: no-repeat;
            background-position: center center;
          }

          svg {
            display: none;
          }

          &.expanded {
            transform: rotate(90deg);
          }
        }

        // 选中状态
        &.is-current > .el-tree-node__content {
          background-color: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
          font-weight: 500;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }

        // 子节点缩进
        &__children {
          padding-left: 0px;
        }
      }

    }
  }

  .custom-node {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .label {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      min-width: 0;
      max-width: calc(100% - 20px); // 为操作按钮预留固定空间

      // 图标样式
      .el-icon {
        flex-shrink: 0;
        font-size: 16px;
        color: var(--el-color-primary);
        // background-color: var(--el-color-primary-light-9);
        padding: 6px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: auto;
      }

      .el-avatar {
        padding: 5px;
      }
    }

    .actions {
      flex-shrink: 0;
      opacity: 0;
      transition: opacity 0.2s;
      display: flex;
      justify-content: center;
      position: absolute;
      right: 3px;

      // 操作按钮样式
      .el-button {
        padding: 4px;
        border-radius: 4px;

        &:hover {
          background-color: var(--el-color-primary-light-8);
        }

        .el-icon {
          font-size: 14px;
        }
      }
    }

    &:hover .actions {
      opacity: 1;
    }
  }
}

.application-tree-avatar {
  background-color: #ffffff;
}
</style>
<style lang="scss">
.search {
  .el-input {
    .el-input__wrapper {
      border-radius: 18px;
    }
  }
}
</style>
