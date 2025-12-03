/**
 * MCP服务相关API
 */
import { Result } from '@/request/Result'
import { get, post, put } from '@/request/index'
import type { Ref } from 'vue'
import type { 
  McpServiceInfo, 
  ServicePageQueryParams, 
  ServicePageResult 
} from '@/api/type/mcp-service'

const prefix = '/v1/mcp'

/**
 * 分页获取所有MCP服务列表
 * @param page - 页码
 * @param size - 每页记录数
 */
const listAllServices: (
  page?: number,
  size?: number,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page = 1, size = 10, loading) => {
  return get(`${prefix}/service/list`, { page, page_size: size }, loading)
}

/**
 * 获取服务详情
 * @param serviceUuid - 服务UUID
 */
const getService: (
  serviceUuid: string,
  loading?: Ref<boolean>
) => Promise<Result<McpServiceInfo>> = (serviceUuid, loading) => {
  return get(`${prefix}/service/${serviceUuid}`, undefined, loading)
}

/**
 * 停止服务
 * @param serviceUuid - 服务UUID
 */
const stopService: (
  serviceUuid: string,
  loading?: Ref<boolean>
) => Promise<Result<{ message: string }>> = (serviceUuid, loading) => {
  return post(`${prefix}/service/${serviceUuid}/stop`, undefined, undefined, loading)
}

/**
 * 启动服务
 * @param serviceUuid - 服务UUID
 */
const startService: (
  serviceUuid: string,
  loading?: Ref<boolean>
) => Promise<Result<{ message: string }>> = (serviceUuid, loading) => {
  return post(`${prefix}/service/${serviceUuid}/start`, undefined, undefined, loading)
}

/**
 * 获取模块的服务列表
 * @param moduleId - 可选的模块ID
 */
const listServices: (
  moduleId?: number,
  loading?: Ref<boolean>
) => Promise<Result<McpServiceInfo[]>> = (moduleId, loading) => {
  return get(`${prefix}/service/list`, { module_id: moduleId }, loading)
}

/**
 * 卸载服务（删除数据库记录并停止服务）
 * @param serviceUuid - 服务UUID
 */
const uninstallService: (
  serviceUuid: string,
  loading?: Ref<boolean>
) => Promise<Result<{ message: string }>> = (serviceUuid, loading) => {
  return post(`${prefix}/service/${serviceUuid}/uninstall`, undefined, undefined, loading)
}

/**
 * 获取MCP服务状态
 */
const getOnlineServices: (
  loading?: Ref<boolean>
) => Promise<Result<string[]>> = (loading) => {
  return get(`${prefix}/service/online`, undefined, loading)
}

/**
 * 更新服务参数
 * @param serviceId - 服务ID
 * @param params - 服务参数
 */
const updateServiceParams: (
  serviceId: number,
  params: Record<string, any>,
  loading?: Ref<boolean>
) => Promise<Result<McpServiceInfo>> = (serviceId, params, loading) => {
  return put(`${prefix}/service/${serviceId}/params`, params, undefined, loading)
}

/**
 * 更新服务状态
 * @param serviceId - 服务ID
 * @param data - 更新数据（如is_public等）
 */
const updateServiceVisibility: (
  serviceId: number,
  data: { is_public?: boolean },
  loading?: Ref<boolean>
) => Promise<Result<McpServiceInfo>> = (serviceId, data, loading) => {
  return put(`${prefix}/service/${serviceId}/visibility`, data, undefined, loading)
}

/**
 * 分页获取MCP服务列表
 * @param params - 分页查询参数
 */
const listServicesPage: (
  params: ServicePageQueryParams,
  loading?: Ref<boolean>
) => Promise<Result<ServicePageResult<McpServiceInfo>>> = (params, loading) => {
  return post(`${prefix}/service/page`, params, undefined, loading)
}

/**
 * 创建第三方MCP服务
 * @param data - 第三方服务数据
 */
const createThirdPartyService: (
  data: {
    service_name: string;
    sse_url: string;
    description?: string;
    is_public?: boolean;
  },
  loading?: Ref<boolean>
) => Promise<Result<{
  message: string;
  service: McpServiceInfo;
}>> = (data, loading) => {
  return post(`${prefix}/service/third-party-services`, data, undefined, loading)
}

export default {
  listAllServices,
  listServicesPage,
  getService,
  stopService,
  startService,
  listServices,
  uninstallService,
  getOnlineServices,
  updateServiceParams,
  updateServiceVisibility,
  createThirdPartyService
}
