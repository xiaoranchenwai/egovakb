/**
 * MCP服务器管理相关API
 */
import { get, post, put, del } from '@/request'
import type { Result } from '@/request/Result'

const apiPrefix = '/v1/mcp'

/**
 * 更新服务参数
 * @param id - 服务ID
 * @param configParams - 配置参数
 */
export async function updateServiceParams(
  id: number | string,
  configParams: Record<string, any>
): Promise<
  Result<{
    message: string
  }>
> {
  return put(`${apiPrefix}/mcp/service/${id}/params`, configParams)
} 