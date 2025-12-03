import { get, post, put, del } from '@/request/index'
import { Result } from '@/request/Result'
import type { Ref } from 'vue'

export interface GroupParams {
  name?: string
  parent_id?: string
}

export interface GroupData {
  id: string
  name: string
  parent_id: string | null
  user_id: string
  create_time: string
  update_time: string
}
export interface GroupMemberData {
  id: string
  user_id: string
  user_info: {
    email: string
    id: string
    username: string
  },
  avatar: string
  create_time: string
  update_time: string
}

export interface GroupTreeData extends GroupData {
  children?: GroupTreeData[]
  members?: GroupMemberData[]
}

export interface CreateGroupParams {
  name: string
  parent_id?: string
}

export interface UpdateGroupParams {
  name?: string
  parent_id?: string | null
}

export interface GroupDetails {
  id: string
  group: string
  target_type: 'APPLICATION' | 'DATASET'
  target_id: string
  target_name: string
  user: string
}

export interface BatchCreateItem {
  group: string
  target_type: 'APPLICATION' | 'DATASET'
  target_id: string
}

export default {
  getGroups(params: GroupParams, loading?: Ref<boolean>) {
    return get('group', params, loading)
  },
  
  getGroupTree(loading?: Ref<boolean>) {
    return get('group/tree', {}, loading)
  },
  
  getGroup(groupId: string, loading?: Ref<boolean>) {
    return get(`group/${groupId}`, {}, loading)
  },
  
  createGroup(params: CreateGroupParams, loading?: Ref<boolean>) {
    return post('group', params, loading)
  },
  
  updateGroup(groupId: string, params: UpdateGroupParams, loading?: Ref<boolean>) {
    return put(`group/${groupId}`, params, loading)
  },
  
  deleteGroup(groupId: string, loading?: Ref<boolean>) {
    return del(`group/${groupId}`, null, null, loading)
  },

  // GroupDetails相关API
  getGroupDetails(loading?: Ref<boolean>) {
    return get('group-details', {}, loading)
  },

  getGroupDetailsByGroup(groupId: string, loading?: Ref<boolean>) {
    return get('group-details/by-group', { group_id: groupId }, loading)
  },

  createGroupDetails(data: Omit<GroupDetails, 'id' | 'user' | 'target_name'>, loading?: Ref<boolean>) {
    return post('group-details', data, loading)
  },

  batchCreateGroupDetails(items: BatchCreateItem[], loading?: Ref<boolean>) {
    return post('group-details/batch-create', { items }, loading)
  },

  deleteGroupDetails(id: string, loading?: Ref<boolean>) {
    return del(`group-details/${id}`, null, null, loading)
  },

  batchDeleteGroupDetails(ids: string[], loading?: Ref<boolean>) {
    return post('group-details/batch-delete', { ids }, loading)
  },

  // 获取分组下的应用
  getGroupApplications(groupId: string, loading?: Ref<boolean>) {
    return get(`group/${groupId}/applications`, {}, loading)
  },

  // 添加应用到分组
  addApplicationToGroup(groupId: string, applicationId: string, loading?: Ref<boolean>) {
    return post(`group/${groupId}/add_application`, {
      application_id: applicationId
    }, loading)
  },

  // 从分组移除应用
  removeApplicationFromGroup(groupId: string, applicationId: string, loading?: Ref<boolean>) {
    return del(`group/${groupId}/applications/${applicationId}`, null, null, loading)
  },
  
  // GroupDetailsTree相关API
  getGroupDetailsTree(params: any, loading?: Ref<boolean>) {
    return get('group-details/tree', params, loading)
  }
} 