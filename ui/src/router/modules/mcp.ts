import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/layout-template/McpLayout.vue'
import { Role } from '@/utils/permission/type'

const mcpRouter = {
  path: '/mcp',
  name: 'mcp',
  meta: { icon: 'Connection', title: 'MCP管理', permission: 'APPLICATION:READ' },
  redirect: () => {
    return '/mcp/marketplace'
  },
  component: Layout,
  children: [
    {
      path: '/mcp/marketplace',
      name: 'marketplace',
      meta: {
        icon: 'app-mcp-square',
        iconActive: 'app-mcp-square-active',
        title: '模板广场',
        activeMenu: '/mcp',
        parentPath: '/mcp',
        parentName: 'mcp',
        permission: 'APPLICATION:READ',
        hideChildren: true
      },
      component: () => import('@/views/marketplace/index1.vue'),
      redirect: "/mcp/marketplace/index",
      children: [
        {
          path: '/mcp/marketplace/index',
          name: 'module-home',
          meta: {
            title: 'MCP模块详情',          
            permission: 'APPLICATION:READ',
            hidden: true
          },
          component: () => import('@/views/marketplace/home.vue')
        },
        {
          path: '/mcp/marketplace/add',
          name: 'module-add',
          meta: {
            title: 'MCP模块新增',
            permission: 'APPLICATION:READ',
            hidden: true
          },
          component: () => import('@/views/marketplace/add.vue')
        },
        {
          path: '/mcp/marketplace-detail/:id',
          name: 'module-detail',
          meta: {
            title: 'MCP模块详情',
            permission: 'APPLICATION:READ',
            hidden: true
          },
          component: () => import('@/views/marketplace/components/ModuleDetailMain.vue')
        },
      ]
    },

    {
      path: '/mcp/service',
      name: 'mcp-service',
      meta: {
        icon: "app-mcp-server",
        iconActive: "app-mcp-server-active",
        title: '服务管理',
        activeMenu: '/mcp',
        parentPath: '/mcp',
        parentName: 'mcp',
        permission: 'APPLICATION:READ'
      },
      component: () => import('@/views/mcp-service/index.vue')
    },
    {
      path: '/mcp/statistics',
      name: 'mcp-statistics',
      meta: {
        icon: 'app-mcp-statistic',
        iconActive: 'app-mcp-statistic-active',
        title: '统计分析',
        activeMenu: '/mcp',
        parentPath: '/mcp',
        parentName: 'mcp',
        permission: 'APPLICATION:READ'
      },
      component: () => import('@/views/mcp-statistics/index1.vue')
    }
  ]
}

export default mcpRouter 