/**
 * MCP服务相关类型定义
 */

/**
 * 分页参数
 */
export interface ServicePagingParams {
  page: number;
  size: number;
}

/**
 * 服务查询条件
 */
export interface ServiceQueryCondition {
  name?: string;
  module_id?: number | null;
  status?: string;
  user_id?: number | null;
  protocol_type?: string | null;
  service_type?: any;
  is_public?: boolean | null | undefined;
}

/**
 * 服务分页查询请求参数
 */
export interface ServicePageQueryParams {
  paging: ServicePagingParams;
  condition: ServiceQueryCondition;
}

/**
 * 服务分页查询响应结果
 */
export interface ServicePageResult<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

/**
 * MCP服务信息
 */
export interface McpServiceInfo {
  id: number;
  service_uuid: string;
  name: string;
  description?: string;
  module_id: number;
  module_name: string;
  status: 'running' | 'stopped' | 'error';
  sse_url: string;
  config_params?: Record<string, any>;
  config_schema?: Record<string, any>;
  error_message?: string;
  created_at: string;
  updated_at: string;
  is_public: boolean;
  can_edit: boolean;
  username?: string;
  user_id?: number;
  user_name?: string;
  enabled?: boolean;
  service_type?: number;
  service_type_name?: string;
} 