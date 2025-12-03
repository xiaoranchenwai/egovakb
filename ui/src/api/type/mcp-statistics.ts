/**
 * MCP统计相关类型定义
 */

/**
 * 服务统计数据接口
 */
export interface ServiceStats {
  total_services: number;
  running_services: number;
  stopped_services: number;
  error_services: number;
  updated_at: string;
}

/**
 * 模块排名接口
 */
export interface ModuleRanking {
  module_id: number;
  module_name: string;
  service_count: number;
  user_id: number;
  user_name: string;
  updated_at: string;
}

/**
 * 工具排名接口
 */
export interface ToolRanking {
  tool_name: string;
  call_count: number;
  success_count: number;
  error_count: number;
  avg_execution_time: number;
  last_called_at: string | null;
  updated_at: string;
}

/**
 * 服务调用排名接口
 */
export interface ServiceRanking {
  service_id: string;
  service_name: string;
  module_name: string;
  call_count: number;
  success_count: number;
  error_count: number;
  updated_at: string;
}

/**
 * 排名分页响应接口
 */
export interface RankingPaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * 工具执行记录接口
 */
export interface ToolExecution {
  id: number;
  tool_name: string;
  description: string;
  parameters: any;
  result: any;
  status: string;
  execution_time: number;
  created_at: string;
  service_id?: string;
  module_id?: number;
  service?: {
    id: string;
    name: string;
    description: string;
  };
  module?: {
    id: number;
    name: string;
    description: string;
  };
  creator_name?: string;
}

/**
 * 分页工具执行记录接口
 */
export interface ToolExecutionsResponse {
  items: ToolExecution[];
  total: number;
  page: number;
  size: number;
  pages: number;
} 