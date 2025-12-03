export interface McpTenant {
    id: number;
    name: string;
    code: string;
}

export interface McpUser {
    id: number;
    username: string;
    fullname: string;
    email: string | null;
    is_admin: boolean;
    status: string;
    tenants: McpTenant[];
    created_at: string;
}