export interface ScheduleTaskData {
  id: string
  name: string
  desc?: string
  cron_expression: string
  function_lib_id: string
  params?: string
  task_params?: string
  is_active: boolean
  create_time?: string
  update_time?: string
  user_avatar?: string
  username?: string
}

export interface CreateScheduleTaskRequest {
  name: string
  desc?: string
  cron_expression: string
  function_lib_id: string
  params?: Record<string, any>
  is_active?: boolean
}

export interface UpdateScheduleTaskRequest {
  name?: string
  desc?: string
  cron_expression?: string
  function_lib_id?: string
  params?: Record<string, any>
  is_active?: boolean
} 