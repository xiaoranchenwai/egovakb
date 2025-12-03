/**
 * MCP广场相关类型定义
 */

/**
 * MCP模块信息
 */
export interface McpModuleInfo {
  id: number;
  name: string;
  code?: string;
  description?: string;
  author?: string;
  version?: string;
  visibility: 'public' | 'private';
  category_id?: number | null;
  config_schema?: Record<string, any>;
  tools_count?: number;
  created_at?: string;
  updated_at?: string;
  is_public?: boolean;
  user_id?: number;
  tags?: string;
  module_path?: string;
  markdown_docs?: string;
  creator_name?: string;
  can_edit?: boolean;
  username?: string;
  category_name?: string;
}

/**
 * MCP工具信息
 */
export interface McpToolInfo {
  id: number;
  name: string;
  description?: string;
  module_id: number;
  module_name?: string;
  function_name: string;
  params_schema?: Record<string, any>;
  parameters?: McpToolParameter[];
  created_at?: string;
  updated_at?: string;
}

/**
 * MCP工具参数
 */
export interface McpToolParameter {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  default?: any;
}

/**
 * 扫描结果接口
 */
export interface ScanResult {
  new_modules: number;
  updated_modules: number;
  new_tools: number;
  updated_tools: number;
  message: string;
}

/**
 * 分页参数
 */
export interface PagingParams {
  page: number;
  size: number;
}

/**
 * 查询条件
 */
export interface QueryCondition {
  category_id?: number | null;
  keyword?: string;
}

/**
 * 分页查询请求参数
 */
export interface PageQueryParams {
  paging: PagingParams;
  condition: QueryCondition;
}

/**
 * 分页查询响应结果
 */
export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
} 