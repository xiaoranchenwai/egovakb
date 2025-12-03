<template>
  <LayoutContainer class='group-manage'>
    <div class="group-container">
      <!-- 左侧分组树 -->
      <div class="group-tree-container">
        <div class="tree-header">
          <h4>{{ $t('views.group.groupTree') }}</h4>
          <el-button type="primary" link @click="handleAdd">
            <el-icon><Plus /></el-icon>
          </el-button>
        </div>
        
        <el-input
          v-model="treeFilterText"
          :placeholder="$t('common.search')"
          suffix-icon="Search"
          class="mb-16"
          clearable
        />
        
        <el-scrollbar height="calc(100vh - 220px)">
          <el-tree
            ref="treeRef"
            :data="processedTreeData"
            :props="treeProps"
            :filter-node-method="filterNode"
            node-key="id"
            highlight-current
            @node-click="handleNodeClick"
            v-loading="treeLoading"
            default-expand-all
          >
            <template #default="{ node, data }">
              <div class="tree-node">
                <!-- 显示分组或成员名称 -->
                <div class="node-label">
                  <el-icon v-if="data.type === 'group'" class="mr-4"><Folder /></el-icon>
                  <el-avatar v-else-if="data.type === 'member'" :size="24" class="mr-4" :src="data.avatar">
                    {{ data.name.charAt(0) }}
                  </el-avatar>
                  <span>{{ node.label }}</span>
                </div>
                
                <!-- 分组操作按钮 -->
                <div v-if="data.type === 'group'" class="node-actions" @click.stop>
                  <el-dropdown 
                    trigger="click" 
                    @command="(cmd: string) => handleTreeNodeCommand(cmd, data)" 
                    @click.stop
                    @visible-change="handleDropdownVisibleChange"
                  >
                    <el-icon><MoreFilled color="#A8B4C8"/></el-icon>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit" v-if="canManageGroup(data)">{{ $t('common.edit') }}</el-dropdown-item>
                        <el-dropdown-item command="addMember" v-if="canManageGroup(data)">{{ $t('views.group.members.addMember') }}</el-dropdown-item>
                        <el-dropdown-item command="delete" divided v-if="canManageGroup(data)">{{ $t('common.delete') }}</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
                
                <!-- 成员操作按钮 -->
                <div v-else-if="data.type === 'member'" class="node-actions">
                  <el-button 
                    type="danger" 
                    link 
                    size="small"
                    v-if="canManageGroup(data)"
                    @click.stop="handleQuickRemoveMember(data)"
                  >
                    {{ $t('views.group.members.remove') }}
                  </el-button>
                </div>
              </div>
            </template>
          </el-tree>
        </el-scrollbar>
      </div>
      
      <!-- 右侧内容区 -->
      <div class="group-content">
        <div class="flex-between mb-16">
          <el-input
            v-model="searchName"
            :placeholder="$t('common.search')"
            style="width: 300px"
            class='combine-input'
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
          <el-button type="primary" @click="handleAdd">
            {{ $t('views.group.addGroup') }}
          </el-button>
        </div>

        <app-table
          class="mt-16"
          :data="tableData"
          v-loading="loading"
        >
          <el-table-column :label="$t('common.index')">
            <template #default="{ $index }">
              {{ $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="name" :label="$t('views.group.name')" />
          <el-table-column :label="$t('views.group.parentGroup')">
            <template #default="{ row }">
              {{ row.parent_id ? getParentName(row.parent_id) : $t('views.group.topLevel') }}
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="250">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">
                {{ $t('common.edit') }}
              </el-button>
              <el-button type="primary" link @click="handleManageMembers(row)">
                {{ $t('views.group.members.title') }}
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">
                {{ $t('common.delete') }}
              </el-button>
            </template>
          </el-table-column>
        </app-table>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? $t('views.group.editGroup') : $t('views.group.addGroup')"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item :label="$t('views.group.name')+':'" prop="name">
          <el-input v-model="form.name" placeholder="请输入分组名称"/>
        </el-form-item>
        <el-form-item :label="$t('views.group.parentGroup')+':'" prop="parent_id" class='required-dot'>
          <el-select
            v-model="form.parent_id"
            class="w-full"
            :placeholder="$t('views.group.selectParent')"
            clearable
          >
            <el-option
              v-for="item in parentOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              :disabled="item.id === currentId"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitForm">{{ $t('common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="memberDialogVisible"
      :title="$t('views.group.members.title')"
      width="700px"
      class="member-dialog"
    >
      <div class="flex-between mb-16">
        <h3>{{ currentGroupName }}</h3>
        <el-button type="primary" @click="handleAddMember">
          {{ $t('views.group.members.addMember') }}
        </el-button>
      </div>

      <el-input
        v-model="memberFilterText"
        :placeholder="$t('common.search')"
        prefix-icon="Search"
        class="mb-16"
        clearable
      />

      <app-table
        :data="filteredMemberList"
        v-loading="memberLoading"
        max-height="400px"
      >
        <el-table-column :label="$t('common.index')">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="user_info.username" :label="$t('views.group.members.username')" />
        <el-table-column prop="user_info.email" :label="$t('views.group.members.email')" />
        <el-table-column :label="$t('common.operation')" width="120">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleRemoveMember(row)">
              {{ $t('views.group.members.remove') }}
            </el-button>
          </template>
        </el-table-column>
      </app-table>
    </el-dialog>

    <el-dialog
      v-model="addMemberDialogVisible"
      :title="$t('views.group.members.addMember')"
      width="500px"
      :destroy-on-close="true"
    >
      <el-form
        ref="memberFormRef"
        :model="memberForm"
        :rules="memberRules"
        label-width="100px"
        label-position="top"
      >
        <el-form-item :label="$t('views.group.members.user')+':'" prop="user_id">
          <el-select
            v-model="memberForm.user_id"
            class="w-full"
            :placeholder="$t('views.group.members.selectUser')"
            filterable
          >
            <el-option
              v-for="user in availableUsers"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            >
              <div class="flex-between">
                <span>{{ user.username }}</span>
                <span class="text-gray">{{ user.email }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addMemberDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitMemberForm">{{ $t('common.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </LayoutContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import groupApi from '@/api/group'
import groupMemberApi from '@/api/group-member'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { GroupData, GroupTreeData } from '@/api/group'
import type { GroupMemberData, UserData } from '@/api/group-member'
import { Plus, MoreFilled, Search, Folder, User } from '@element-plus/icons-vue'
import useStore from '@/stores'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const searchName = ref('')
const tableData = ref<GroupData[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref('')
const parentOptions = ref<GroupData[]>([])
const formRef = ref<FormInstance>()
const form = ref({
  name: '',
  parent_id: undefined as string | undefined
})
const rules = ref<FormRules>({
  name: [
    { required: true, message: t('views.group.nameRequired'), trigger: 'blur' },
    { min: 1, max: 128, message: t('views.group.nameLength'), trigger: 'blur' }
  ]
})

const memberDialogVisible = ref(false)
const memberLoading = ref(false)
const memberList = ref<GroupMemberData[]>([])
const currentGroupId = ref('')
const currentGroupName = ref('')
const memberFilterText = ref('')

// 过滤后的成员列表
const filteredMemberList = computed(() => {
  if (!memberFilterText.value) return memberList.value
  
  return memberList.value.filter(member => 
    member.user_info.username.toLowerCase().includes(memberFilterText.value.toLowerCase()) ||
    member.user_info.email.toLowerCase().includes(memberFilterText.value.toLowerCase())
  )
})

const addMemberDialogVisible = ref(false)
const memberFormRef = ref<FormInstance>()
const memberForm = ref({
  user_id: ''
})
const memberRules = ref<FormRules>({
  user_id: [
    { required: true, message: t('views.group.members.userRequired'), trigger: 'change' }
  ]
})
const availableUsers = ref<UserData[]>([])

// 分组树相关
const treeRef = ref()
const treeLoading = ref(false)
const groupTreeData = ref<GroupTreeData[]>([])
const treeFilterText = ref('')
const treeProps = {
  label: 'name',
  children: 'children',
  expandOnClickNode: false
}

// 选中的分组和成员
const selectedGroupId = ref('')
const selectedGroupName = ref('')
const selectedGroupMembers = ref<GroupMemberData[]>([])

const { user } = useStore()

// 处理后的树数据，包含分组和成员
const processedTreeData = computed(() => {
  // 递归处理分组树数据
  const processGroup = (group: GroupTreeData): any => {
    // 创建分组节点
    const groupNode = {
      id: group.id,
      name: group.name,
      parent_id: group.parent_id,
      user_id: group.user_id,
      type: 'group',
      create_time: group.create_time,
      update_time: group.update_time,
      children: [] as any[]
    }
    
    // 添加子分组
    if (group.children && group.children.length > 0) {
      group.children.forEach(child => {
        groupNode.children.push(processGroup(child))
      })
    }
    
    // 添加成员节点
    if (group.members && group.members.length > 0) {
      group.members.forEach(member => {
        groupNode.children.push({
          id: `member-${member.id}`,
          name: member.user_info.username,
          type: 'member',
          group_id: group.id,
          user_id: member.user_id,
          user_info: member.user_info,
          avatar: member.avatar || '/api/image/default-avatar.png',
          original: member
        })
      })
    }
    
    return groupNode
  }
  
  // 处理所有顶级分组
  return groupTreeData.value.map(group => processGroup(group))
})

// 监听搜索输入，过滤树节点
watch(treeFilterText, (val) => {
  treeRef.value?.filter(val)
})

// 过滤树节点
function filterNode(value: string, data: any) {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

// 处理树节点点击
function handleNodeClick(data: any) {
  // 如果点击的是分组节点
  if (data.type === 'group') {
    selectedGroupId.value = data.id
    selectedGroupName.value = data.name
  }
}

// 快速移除成员
function handleQuickRemoveMember(data: any) {
  if (data.type !== 'member') return
  
  ElMessageBox.confirm(
    t('views.group.members.removeConfirm'),
    t('common.delete'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(() => {
    memberLoading.value = true
    groupMemberApi.removeGroupMember(data.group_id, data.user_id, memberLoading).then(() => {
      ElMessage.success(t('views.group.members.removeSuccess'))
      getGroupTree() // 更新分组树
    }).catch((error) => {
      memberLoading.value = false
    })
  }).catch(() => {})
}

// 在获取分组树后，默认选中第一个分组
function selectFirstGroup() {
  if (groupTreeData.value.length > 0) {
    const firstGroup = groupTreeData.value[0]
    selectedGroupId.value = firstGroup.id
    selectedGroupName.value = firstGroup.name
    
    // 高亮第一个节点
    treeRef.value?.setCurrentKey(firstGroup.id)
  }
}

// 修改 getGroupTree 函数，添加更多调试信息
function getGroupTree() {
  console.log('开始获取分组树')
  treeLoading.value = true
  groupApi.getGroupTree(treeLoading).then(res => {
    console.log('分组树数据:', res.data)
    groupTreeData.value = res.data
    
    // 添加调试信息
    console.log('处理前的分组树数据:', groupTreeData.value)
    
    // 确保在设置数据后再计算处理后的树数据
    setTimeout(() => {
      console.log('处理后的分组树数据:', processedTreeData.value)
    }, 0)
    
    treeLoading.value = false
    // 选中第一个分组
    selectFirstGroup()
  }).catch((error) => {
    console.error('获取分组树失败:', error)
    treeLoading.value = false
    ElMessage.error(t('common.fetchFailed'))
  })
}

function getList() {
  const params = {
    name: searchName.value
  }
  
  groupApi.getGroups(params, loading).then(res => {
    tableData.value = res.data
    parentOptions.value = res.data
  })
}

function getParentName(parentId: string): string {
  const parent = parentOptions.value.find(item => item.id === parentId)
  return parent ? parent.name : ''
}

function handleSearch() {
  getList()
}

function handleAdd() {
  isEdit.value = false
  currentId.value = ''
  form.value = {
    name: '',
    parent_id: undefined
  }
  dialogVisible.value = true
}

function handleEdit(row: GroupData) {
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    name: row.name,
    parent_id: row.parent_id || undefined
  }
  dialogVisible.value = true
}

function handleManageMembers(row: GroupData) {
  currentGroupId.value = row.id
  currentGroupName.value = row.name
  memberFilterText.value = ''
  memberDialogVisible.value = true
  getGroupMembers()
}

function getGroupMembers() {
  memberLoading.value = true
  groupMemberApi.getGroupMembers(currentGroupId.value, memberLoading).then(res => {
    memberList.value = res.data
    memberLoading.value = false
  })
}

function handleAddMember() {
  memberForm.value.user_id = ''
  getAvailableUsers()
  addMemberDialogVisible.value = true
}

function getAvailableUsers() {
  memberLoading.value = true
  groupMemberApi.getAvailableUsers(currentGroupId.value, memberLoading).then(res => {
    availableUsers.value = res.data
    memberLoading.value = false
  })
}

function submitMemberForm() {
  if (!memberFormRef.value) return
  
  memberFormRef.value.validate((valid) => {
    if (valid) {
      memberLoading.value = true
      groupMemberApi.addGroupMember(currentGroupId.value, memberForm.value, memberLoading).then(() => {
        ElMessage.success(t('views.group.members.addSuccess'))
        addMemberDialogVisible.value = false
        getGroupMembers()
        getGroupTree() // 更新分组树
        // 如果当前选中的分组就是添加成员的分组，更新选中分组的成员列表
        // if (selectedGroupId.value === currentGroupId.value) {
        //   getSelectedGroupMembers(selectedGroupId.value)
        // }
      }).catch(() => {
        memberLoading.value = false
      })
    }
  })
}

function handleRemoveMember(row: GroupMemberData) {
  ElMessageBox.confirm(
    t('views.group.members.removeConfirm'),
    t('common.delete'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(() => {
    memberLoading.value = true
    groupMemberApi.removeGroupMember(currentGroupId.value, row.user_id, memberLoading).then(() => {
      ElMessage.success(t('views.group.members.removeSuccess'))
      getGroupMembers()
      getGroupTree() // 更新分组树
      // 如果当前选中的分组就是移除成员的分组，更新选中分组的成员列表
      // if (selectedGroupId.value === currentGroupId.value) {
      //   getSelectedGroupMembers(selectedGroupId.value)
      // }
    }).catch((error) => {
      memberLoading.value = false
    })
  }).catch(() => {})
}

function handleViewMembers(row: GroupData) {
  router.push(`/group/${row.id}/members`)
}

function handleDelete(row: GroupData) {
  ElMessageBox.confirm(
    t('views.group.deleteConfirm'),
    t('common.delete'),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(() => {
    loading.value = true
    groupApi.deleteGroup(row.id, loading).then(() => {
      ElMessage.success(t('common.deleteSuccess'))
      getList()
      getGroupTree() // 更新分组树
    }).catch((error) => {
      loading.value = false
      console.error('删除分组失败:', error)
    })
  }).catch(() => {})
}

function submitForm() {
  if (!formRef.value) return
  
  formRef.value.validate((valid) => {
    if (valid) {
      if (isEdit.value) {
        loading.value = true
        groupApi.updateGroup(currentId.value, form.value, loading).then(() => {
          ElMessage.success(t('common.updateSuccess'))
          dialogVisible.value = false
          getList()
          getGroupTree() // 更新分组树
        }).catch(() => {
          loading.value = false
        })
      } else {
        loading.value = true
        groupApi.createGroup(form.value, loading).then(() => {
          ElMessage.success(t('common.createSuccess'))
          dialogVisible.value = false
          getList()
          getGroupTree() // 更新分组树
        }).catch(() => {
          loading.value = false
        })
      }
    }
  })
}

function handleTreeNodeCommand(cmd: string, data: GroupTreeData) {
  // 阻止事件冒泡，防止触发树的展开/收起
  console.log('handleTreeNodeCommand', cmd, data)
  switch (cmd) {
    case 'edit':
      handleEdit(data)
      break
    case 'addMember':
      handleManageMembers(data)
      break
    case 'delete':
      handleDelete(data)
      break
  }
}

// 检查用户是否可以管理分组
function canManageGroup(data: any) {
  // 如果是管理员，可以管理所有分组
  if (user.getRole() === 'ADMIN') {
    return true
  }
  
  // 如果是分组创建者，可以管理该分组
  if (data.type === 'group' && data.user_id === user.userInfo?.id) {
    return true
  }
  
  // 如果是成员节点，检查其所属分组
  if (data.type === 'member' && data.group_id) {
    const group = findGroupById(data.group_id)
    return group && group.user_id === user.userInfo?.id
  }
  
  return false
}

// 根据ID查找分组
function findGroupById(groupId: string) {
  // 递归查找分组
  const findInGroups = (groups: any[], id: string): any => {
    for (const group of groups) {
      if (group.id === id) {
        return group
      }
      if (group.children && group.children.length > 0) {
        const found = findInGroups(group.children.filter((c: any) => c.type === 'group'), id)
        if (found) return found
      }
    }
    return null
  }
  
  return findInGroups(processedTreeData.value, groupId)
}

// 添加 dropdown 显示/隐藏事件处理
function handleDropdownVisibleChange(visible: boolean) {
  // 阻止事件冒泡到树节点
  event?.stopPropagation()
}

onMounted(() => {
  getList()
  getGroupTree()
})
</script>

<style lang="scss" scoped>
.group-manage {
  padding: var(--app-view-padding) !important;
  box-sizing: border-box;
  ::v-deep(.el-scrollbar__wrap) {
      overflow: hidden !important;
  }
}
.group-container {
  display: flex;
  height: 100%;
  ::v-deep(.el-scrollbar__wrap) {
    overflow: auto !important;
  }

}

.group-tree-container {
  width: 280px;
  border-right: 1px solid var(--el-border-color-light);
  padding: var(--app-view-padding);
  
  .tree-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h4 {
      margin: 0;
    }
  }
}

.group-content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
  
  .node-label {
    display: flex;
    align-items: center;
  }
  
  .node-actions {
    display: none;
    position: relative;
    z-index: 1;
  }
  
  &:hover .node-actions {
    display: block;
  }
}

.group-members-container {
  margin-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
  padding-top: 12px;
  
  h5 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  
  &:last-child {
    border-bottom: none;
  }
  
  .member-info {
    display: flex;
    align-items: center;
  }
}

.w-full {
  width: 100%;
}

.member-dialog {
  .el-dialog__body {
    padding-top: 10px;
  }
}

.text-gray {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
<style lang='scss'>
.group-manage {
  .group-container {
    .el-input {
      .el-input__wrapper {
        border-radius: 16px;
      }
    }
    .app-table {
      height: calc(100% - 50px);
      .el-table {
        max-height: 100% !important;
        height: calc(100% - 45px) !important;
      }
    }
  }
}
</style>