/**
 * MCP分类信息
 */
export interface McpGroup {
    id: number;
    name: string;
    description?: string;
    modules_count?: number;
    created_at?: string;
    updated_at?: string;
}