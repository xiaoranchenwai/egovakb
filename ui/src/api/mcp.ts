/**
 * MCP服务管理相关API
 */
import { get, post, put, del } from '@/request'
import type { Result } from '@/request/Result'

const apiPrefix = '/v1/mcp'

/**
 * 工具调用数据
 */
export interface ToolCall {
  tool_name: string
  parameters: any
  function_name?: string
  module_id?: number
  service_id?: string
}

/**
 * 获取MCP服务状态
 */
export async function getMcpStatus(): Promise<Result<any>> {
  return get(`${apiPrefix}/mcp/service/status`)
}

/**
 * 获取启用的工具列表
 */
export async function getEnabledTools(): Promise<Result<any>> {
  return get(`${apiPrefix}/mcp/service/enabled_tools`)
}

/**
 * 重启MCP服务
 */
export async function restartMcpService(): Promise<Result<any>> {
  return post(`${apiPrefix}/mcp/service/restart`)
}

/**
 * 加载工具
 * @param modulePath 模块路径
 * @param functionName 函数名称
 * @param toolName 工具名称（可选）
 * @param description 工具描述（可选）
 */
export async function loadTool(
  modulePath: string,
  functionName: string,
  toolName?: string,
  description?: string
): Promise<Result<any>> {
  return post(`${apiPrefix}/mcp/service/load_tool`, {
    module_path: modulePath,
    function_name: functionName,
    tool_name: toolName,
    description: description
  })
}

/**
 * 卸载工具
 * @param toolName 工具名称
 */
export async function unloadTool(toolName: string): Promise<Result<any>> {
  return post(`${apiPrefix}/mcp/service/unload_tool`, {
    tool_name: toolName
  })
}

/**
 * 更新MCP SSE URL
 * @param sseUrl 新的SSE URL
 */
export async function updateSseUrl(sseUrl: string): Promise<Result<any>> {
  return put(`${apiPrefix}/mcp/service/sse_url`, {
    sse_url: sseUrl
  })
}

/**
 * 更新服务参数
 * @param id - 服务ID
 * @param configParams - 配置参数
 */
export async function updateServiceParams(
  id: number,
  configParams: Record<string, any>
): Promise<
  Result<{
    message: string
  }>
> {
  return put(`${apiPrefix}/mcp/service/${id}/params`, configParams)
}

/**
 * 获取所有工具信息
 */
export async function getTools(): Promise<Result<any[]>> {
  return get(`${apiPrefix}/tools`)
}

/**
 * 获取工具内容
 */
export async function getToolContent(toolPath: string): Promise<Result<any>> {
  return get(`${apiPrefix}/tools/${encodeURIComponent(toolPath)}/content`)
}

/**
 * 获取工具信息
 */
export async function getToolInfo(toolName: string): Promise<Result<any>> {
  return get(`${apiPrefix}/tools/${encodeURIComponent(toolName)}`)
}

/**
 * 创建工具
 */
export async function createTool(toolData: any): Promise<Result<any>> {
  return post(`${apiPrefix}/tools`, toolData)
}

/**
 * 更新工具
 */
export async function updateTool(toolPath: string, toolData: any): Promise<Result<any>> {
  return put(`${apiPrefix}/tools/${encodeURIComponent(toolPath)}`, toolData)
}

/**
 * 删除工具
 */
export async function deleteTool(toolPath: string): Promise<Result<any>> {
  return del(`${apiPrefix}/tools/${encodeURIComponent(toolPath)}`)
}

/**
 * 获取所有模块信息
 */
export async function getModules(): Promise<Result<any[]>> {
  return get(`${apiPrefix}/modules`)
}

/**
 * 获取模块内容
 */
export async function getModuleContent(modulePath: string): Promise<Result<any>> {
  return get(`${apiPrefix}/modules/${encodeURIComponent(modulePath)}/content`)
}

/**
 * 创建模块
 */
export async function createModule(moduleData: any): Promise<Result<any>> {
  return post(`${apiPrefix}/modules`, moduleData)
}

/**
 * 更新模块
 */
export async function updateModule(modulePath: string, moduleData: any): Promise<Result<any>> {
  return put(`${apiPrefix}/modules/${encodeURIComponent(modulePath)}`, moduleData)
}

/**
 * 删除模块
 */
export async function deleteModule(modulePath: string): Promise<Result<any>> {
  return del(`${apiPrefix}/modules/${encodeURIComponent(modulePath)}`)
}

/**
 * 执行工具
 */
export async function executeTool(toolCallData: ToolCall): Promise<Result<any>> {
  return post(`${apiPrefix}/mcp/execute`, toolCallData)
} 