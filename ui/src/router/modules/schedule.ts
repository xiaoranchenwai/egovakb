const scheduleRouter = {
  path: '/schedule',
  name: 'schedule',
  meta: { title: 'views.schedule.title', permission: 'APPLICATION:READ' },
  redirect: '/schedule',
  component: () => import('@/layout/layout-template/AppLayout.vue'),
  children: [
    {
      path: '/schedule',
      name: 'schedule-index',
      meta: { title: '定时任务', activeMenu: '/schedule' },
      component: () => import('@/views/schedule/index.vue')
    }
  ]
}

export default scheduleRouter 