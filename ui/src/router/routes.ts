import type { RouteRecordRaw } from 'vue-router'
import { Role } from '@/utils/permission/type'
import scheduleRouter from './modules/schedule'

const modules: any = import.meta.glob('./modules/*.ts', { eager: true })
let rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]

console.log('window app config', window.APP_CONFIG)
// 根据 APP_CONFIG.SHOW_MCP 的值决定是否包含 MCP 路由
if (window.APP_CONFIG && (window as any).APP_CONFIG.SHOW_MCP === false) {
  rolesRoutes = rolesRoutes.filter(route => route.name !== 'mcp')
  console.log('filter mcp', rolesRoutes)
}

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    redirect: '/application',
    children: [...rolesRoutes]
  },

  // 高级编排
  {
    path: '/application/:id/workflow',
    name: 'ApplicationWorkflow',
    meta: { activeMenu: '/application' },
    component: () => import('@/views/application-workflow/index.vue')
  },

  {
    path: '/chat/:accessToken',
    name: 'Chat',
    component: () => import('@/views/chat/index.vue')
  },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/login/register/index.vue')
  },
  {
    path: '/forgot_password',
    name: 'forgot_password',
    component: () => import('@/views/login/forgot-password/index.vue')
  },
  {
    path: '/reset_password/:code/:email',
    name: 'reset_password',
    component: () => import('@/views/login/reset-password/index.vue')
  },
  {
    path: '/:pathMatch(.*)',
    name: '404',
    component: () => import('@/views/404/index.vue')
  }
]
