/**
 * 统计相关API
 */
import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { Ref } from 'vue'
import type {
  ServiceStats,
  ModuleRanking,
  ToolRanking,
  ServiceRanking,
  RankingPaginationResponse,
  ToolExecution,
  ToolExecutionsResponse
} from '@/api/type/mcp-statistics'

const prefix = '/v1/mcp'

/**
 * 获取服务统计数据
 */
const getServiceStats: (loading?: Ref<boolean>) => Promise<Result<ServiceStats>> = (loading) => {
  return get(`${ prefix }/statistics/services`, undefined, loading)
}

/**
 * 获取模块发布排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
const getModuleRankings: (
  size?: number,
  page?: number,
  loading?: Ref<boolean>
) => Promise<Result<RankingPaginationResponse<ModuleRanking>>> = (size = 10, page = 1, loading) => {
  return get(`${ prefix }/statistics/modules/rankings`, { size, page }, loading)
}

/**
 * 获取工具调用排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
const getToolRankings: (
  size?: number,
  page?: number,
  loading?: Ref<boolean>
) => Promise<Result<RankingPaginationResponse<ToolRanking>>> = (size = 10, page = 1, loading) => {
  return get(`${ prefix }/statistics/tools/rankings`, { size, page }, loading)
}

/**
 * 获取服务调用排名
 * @param size - 每页返回数量
 * @param page - 页码
 */
const getServiceRankings: (
  size?: number,
  page?: number,
  loading?: Ref<boolean>
) => Promise<Result<RankingPaginationResponse<ServiceRanking>>> = (size = 10, page = 1, loading) => {
  return get(`${ prefix }/statistics/services/rankings`, { size, page }, loading)
}

/**
 * 获取工具执行记录
 * @param page - 页码
 * @param size - 每页记录数
 * @param toolName - 工具名称过滤
 */
const getToolExecutions: (
  page?: number,
  size?: number,
  toolName?: string,
  loading?: Ref<boolean>
) => Promise<Result<ToolExecutionsResponse>> = (page = 1, size = 10, toolName, loading) => {
  const params: any = {
    page,
    size
  }

  if (toolName) {
    params.tool_name = toolName
  }

  return get(`${ prefix }/statistics/tools/executions`, params, loading)
}

/**
 * 刷新统计数据
 */
const refreshStatistics: (loading?: Ref<boolean>) => Promise<Result<{ message: string }>> = (loading) => {
  return post(`${ prefix }/statistics/refresh`, undefined, undefined, loading)
}

const getTotalTrend = (data: any, loading?: Ref<boolean>) => {
  return post(`${ prefix }/statistics/trend`, data, undefined, loading)
}

const getMcpGroupStat = (data: any, loading?: Ref<boolean>) => {
  return post(`${ prefix }/group/stat`, data, undefined, loading)
}

const getMcpTemplateStat = (data: any, loading?: Ref<boolean>) => {
  return post(`${ prefix }/marketplace/modules/stat`, data, undefined, loading)
}

const getMcpModuleStat = (page: number = 1, size: number = 10, loading?: Ref<boolean>) => {
  return get(`${ prefix }/statistics/modules/rankings?size=${ size }&page=${ page }`, undefined, loading)
}

const getMcpServiceStat = (page: number = 1, size: number = 10, loading?: Ref<boolean>) => {
  return get(`${ prefix }/statistics/services/rankings?size=${ size }&page=${ page }`, undefined, loading)
}

const getMcpToolStat = (page: number = 1, size: number = 10, loading?: Ref<boolean>) => {
  return get(`${ prefix }/statistics/tools/rankings?size=${ size }&page=${ page }`, undefined, loading)
}
export default {
  getServiceStats,
  getModuleRankings,
  getToolRankings,
  getServiceRankings,
  getToolExecutions,
  refreshStatistics,

  getTotalTrend,
  getMcpGroupStat,
  getMcpTemplateStat,
  getMcpModuleStat,
  getMcpServiceStat,
  getMcpToolStat
} 