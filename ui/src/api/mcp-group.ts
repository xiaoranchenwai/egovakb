/**
 * MCP广场相关API
 */
import { Result } from '@/request/Result'
import { get, post, put, del } from '@/request/index'
import type { Ref } from 'vue'
import type { McpModuleInfo } from '@/api/type/mcp-square'
import type { McpGroup } from '@/api/type/mcp-group'

const prefix = '/v1/mcp'
/**
 * 获取所有MCP分组
 */
const listGroup: (
    loading?: Ref<boolean>
) => Promise<Result<McpGroup[]>> = (loading) => {
    return get(`${prefix}/group`, undefined, loading)
}

/**
 * 获取分组详情
 * @param categoryId - 分组ID
 */
const getGroup: (
    categoryId: number,
    loading?: Ref<boolean>
) => Promise<Result<McpGroup>> = (categoryId, loading) => {
    return get(`${prefix}/group/${categoryId}`, undefined, loading)
}

/**
 * 创建MCP分组
 * @param data - 分组数据
 */
const createGroup: (
    data: Partial<McpGroup>,
    loading?: Ref<boolean>
) => Promise<Result<McpGroup>> = (data, loading) => {
    return post(`${prefix}/group`, data, undefined, loading)
}

/**
 * 更新MCP分组
 * @param categoryId - 分组ID
 * @param data - 分组数据
 */
const updateGroup: (
    categoryId: number,
    data: Partial<McpGroup>,
    loading?: Ref<boolean>
) => Promise<Result<McpGroup>> = (categoryId, data, loading) => {
    return put(`${prefix}/group/${categoryId}`, data, undefined, loading)
}

/**
 * 删除MCP分组
 * @param categoryId - 分组ID
 */
const deleteGroup: (
    categoryId: number,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (categoryId, loading) => {
    return del(`${prefix}/group/${categoryId}`, undefined, undefined, loading)
}

/**
 * 更新模块所属分组
 * @param moduleId - 模块ID
 * @param categoryId - 分组ID
 */
const updateModuleGroup: (
    moduleId: number,
    categoryId: number | null,
    loading?: Ref<boolean>
) => Promise<Result<McpModuleInfo>> = (moduleId, categoryId, loading) => {
    return put(`${prefix}/modules/${moduleId}/group`, { category_id: categoryId }, undefined, loading)
}

export default {
    listGroup,
    getGroup,
    createGroup,
    updateGroup,
    deleteGroup,
    updateModuleGroup,
} 