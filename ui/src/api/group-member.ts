import { get, post, del } from '@/request/index'
import type { Ref } from 'vue'

export interface GroupMemberData {
  id: string
  group_id: string
  user_id: string
  user_info: {
    id: string
    username: string
    email: string
  }
  avatar?: string
  create_time: string
  update_time: string
}

export interface UserData {
  id: string
  username: string
  email: string
}

export interface AddMemberParams {
  user_id: string
}

export default {
  // 获取分组成员列表
  getGroupMembers(groupId: string, loading?: Ref<boolean>) {
    return get(`group/${groupId}/members`, {}, loading)
  },
  
  // 添加分组成员
  addGroupMember(groupId: string, params: AddMemberParams, loading?: Ref<boolean>) {
    return post(`group/${groupId}/member`, params, loading)
  },
  
  // 移除分组成员
  removeGroupMember(groupId: string, userId: string, loading?: Ref<boolean>) {
    console.log('removeGroupMember', groupId, userId)
    return del(`group/${groupId}/member/${userId}`, {}, {}, loading)
  },
  
  // 获取可用用户（未分配到任何分组的用户）
  getAvailableUsers(groupId: string, loading?: Ref<boolean>) {
    return get(`group/${groupId}/available_users`, {}, loading)
  }
} 