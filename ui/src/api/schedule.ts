import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = 'schedule'

interface ScheduleTaskData {
  name: string
  desc?: string
  cron_expression: string
  function_lib_id: string
  params?: any
  is_active?: boolean
  dataset_id?: string
}

/**
 * 获取定时任务列表
 * @param page 分页参数
 * @param param 查询参数
 */
const getScheduleTaskList: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建定时任务
 * @param data 任务数据
 */
const createScheduleTask: (data: ScheduleTaskData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 更新定时任务
 * @param taskId 任务ID
 * @param data 更新数据
 */
const putScheduleTask: (
  taskId: string,
  data: Partial<ScheduleTaskData>,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (taskId, data, loading) => {
  return put(`${prefix}/${taskId}`, data, undefined, loading)
}

/**
 * 删除定时任务
 * @param taskId 任务ID
 */
const deleteScheduleTask: (taskId: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  taskId,
  loading
) => {
  return del(`${prefix}/${taskId}`, undefined, undefined, loading)
}

/**
 * 获取定时任务详情
 * @param taskId 任务ID
 */
const getScheduleTaskDetail: (taskId: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  taskId,
  loading
) => {
  return get(`${prefix}/${taskId}`, undefined, loading)
}

/**
 * 获取定时任务执行记录列表
 * @param taskId 任务ID
 * @param param 查询参数
 */
const getScheduleTaskRecords: (
  taskId: string,
  param?: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (taskId, param, loading) => {
  return get(`${prefix}/records/${taskId}`, param, loading)
}

/**
 * 分页获取定时任务执行记录
 * @param taskId 任务ID
 * @param page 分页参数
 * @param param 查询参数
 */
const getScheduleTaskRecordsByPage: (
  taskId: string,
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (taskId, page, param, loading) => {
  return get(
    `${prefix}/records/${taskId}/${page.current_page}/${page.page_size}`,
    param,
    loading
  )
}

/**
 * 获取定时任务状态
 * @param taskId 任务ID
 */
const getScheduleTaskStatus: (taskId: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  taskId,
  loading
) => {
  return get(`${prefix}/status/${taskId}`, undefined, loading)
}

/**
 * 手动执行定时任务
 * @param taskId 任务ID
 */
const executeScheduleTask: (taskId: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  taskId,
  loading
) => {
  return post(`${prefix}/execute/${taskId}`, null, undefined, loading)
}

export default {
  getScheduleTaskList,
  createScheduleTask,
  putScheduleTask,
  deleteScheduleTask,
  getScheduleTaskDetail,
  getScheduleTaskRecords,
  getScheduleTaskRecordsByPage,
  getScheduleTaskStatus,
  executeScheduleTask
} 