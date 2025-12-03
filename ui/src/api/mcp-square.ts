/**
 * MCP广场相关API
 */
import { Result } from '@/request/Result'
import { get, post, put, del } from '@/request/index'
import type { Ref } from 'vue'
import type { 
  McpModuleInfo, 
  McpToolInfo, 
  ScanResult,
  PageQueryParams,
  PageResult
} from '@/api/type/mcp-square'
import type { McpServiceInfo } from '@/api/type/mcp-service'

const prefix = '/v1/mcp'

/**
 * 获取所有MCP模块列表
 * @param categoryId - 可选的分类ID
 */
const listModules: (
  categoryId?: string | null,
  loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo[]>> = (categoryId, loading) => {
  let url = `${prefix}/marketplace/modules`
  if (categoryId) {
    url += `?category_id=${categoryId}`
  }
  return get(url, undefined, loading)
}

/**
 * 分页获取MCP模块列表
 * @param params - 分页查询参数
 */
const listModulesPage: (
  params: PageQueryParams,
  loading?: Ref<boolean>
) => Promise<Result<PageResult<McpModuleInfo>>> = (params, loading) => {
  return post(`${prefix}/marketplace/modules/page`, params, undefined, loading)
}

/**
 * 获取指定MCP模块详情
 * @param moduleId - 模块ID
 */
const getModule: (
  moduleId: number,
  loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo>> = (moduleId, loading) => {
  return get(`${prefix}/marketplace/modules/${moduleId}`, undefined, loading)
}

/**
 * 创建MCP模块/服务
 * @param data - 模块数据
 */
const createModule: (
  data: Partial<McpModuleInfo>,
  loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo>> = (data, loading) => {
  return post(`${prefix}/marketplace/modules`, data, undefined, loading)
}

/**
 * 获取指定MCP模块的所有工具
 * @param moduleId - 模块ID
 */
const getModuleTools: (
  moduleId: number,
  loading?: Ref<boolean>
) => Promise<Result<McpToolInfo[]>> = (moduleId, loading) => {
  return get(`${prefix}/marketplace/modules/${moduleId}/tools`, undefined, loading)
}

/**
 * 获取指定MCP工具详情
 * @param toolId - 工具ID
 */
const getTool: (
  toolId: number,
  loading?: Ref<boolean>
) => Promise<Result<McpToolInfo>> = (toolId, loading) => {
  return get(`${prefix}/marketplace/tools/${toolId}`, undefined, loading)
}

/**
 * 扫描仓库中的MCP模块并更新数据库
 */
const scanModules: (
  loading?: Ref<boolean>
) => Promise<Result<ScanResult>> = (loading) => {
  return post(`${prefix}/marketplace/modules/scan`, undefined, undefined, loading)
}

/**
 * 更新模块信息
 * @param moduleId - 模块ID
 * @param data - 要更新的模块数据
 */
const updateModule: (
  moduleId: number,
  data: Partial<McpModuleInfo>,
  loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo>> = (moduleId, data, loading) => {
  return put(`${prefix}/marketplace/modules/${moduleId}`, data, undefined, loading)
}

/**
 * 测试模块工具
 * @param toolId - 工具ID
 * @param params - 工具参数
 */
const testModuleTool: (
  toolId: number,
  params: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (toolId, params, loading) => {
  return post(`${prefix}/execute/tool/${toolId}`, params, undefined, loading)
}

/**
 * 测试模块工具(通过模块ID和函数名)
 * @param moduleId - 模块ID
 * @param functionName - 函数名称
 * @param params - 工具参数
 */
const testModuleFunction: (
  moduleId: number,
  functionName: string,
  params: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (moduleId, functionName, params, loading) => {
  return post(`${prefix}/execute/module/${moduleId}/function/${functionName}`, params, undefined, loading)
}


/**
 * 发布模块
 * @param moduleId - 模块ID
 * @param configParams - 配置参数，可选
 */
const publishModule: (
  moduleId: number,
  configParams?: Record<string, any>,
  loading?: Ref<boolean>
) => Promise<Result<{ message: string; service: McpServiceInfo }>> = (moduleId, configParams, loading) => {
  return post(`${prefix}/marketplace/modules/${moduleId}/publish`, configParams || {}, undefined, loading)
}

/**
 * 删除MCP模块
 * @param moduleId - 模块ID
 */
const deleteModule: (
  moduleId: number,
  loading?: Ref<boolean>
) => Promise<Result<{ message: string }>> = (moduleId, loading) => {
  return del(`${prefix}/marketplace/modules/${moduleId}`, undefined, undefined, loading)
}

/**
 * 复制MCP模块
 * @param moduleId - 源模块ID
 * @param data - 新模块的自定义数据
 */
const cloneModule: (
  moduleId: number,
  data: Partial<McpModuleInfo>,
  loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo>> = (moduleId, data, loading) => {
  // 确保复制所有必要信息，包括markdown说明、代码、配置模式等
  return post(`${prefix}/marketplace/modules/${moduleId}/clone`, data, undefined, loading)
}

export default {
  listModules,
  listModulesPage,
  getModule,
  createModule,
  getModuleTools,
  getTool,
  scanModules,
  updateModule,
  testModuleTool,
  testModuleFunction,
  publishModule,
  deleteModule,
  cloneModule
} 