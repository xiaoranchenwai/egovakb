import { get } from "@/request"
import Result from "@/request/Result"
import type { Ref } from 'vue'
import type { McpUser } from "@/api/type/mcp-auth"
const prefix = '/v1/mcp'

/**
 * 获取用户列表
 */
const getAllUsers: (
  loading?: Ref<boolean>
) => Promise<Result<McpUser[]>> = (loading) => {
  return get(`${prefix}/auth/users`, undefined, loading)
}

export default {
  getAllUsers
}