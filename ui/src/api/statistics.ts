import { get, post } from '@/request/index'
import { Result } from '@/request/Result'
import type { Ref } from 'vue'

export interface StatisticsParams {
  start_time?: string
  end_time?: string
  username?: string
  dimension?: 'user' | 'group'
  current_page?: number
  page_size?: number
}

export interface StatisticsData {
  id: string
  username?: string
  nick_name?: string
  group_name?: string
  member_count?: number
  app_created_count: number
  app_updated_count: number
  dataset_created_count: number
  dataset_updated_count: number
  document_created_count: number
  document_updated_count: number
}

export interface StatisticsResponse {
  total: number
  records: StatisticsData[]
  current: number
  size: number
}

export interface StatisticsDetailParams {
  username: string
  start_time?: string
  end_time?: string
}

export default {
  getStatistics(params: StatisticsParams, loading?: Ref<boolean>) {
    return get('statistics', params, loading)
  },
  getStatisticsDetail(params: StatisticsDetailParams, loading?: Ref<boolean>) {
    return get('statistics/detail', params, loading)
  }
} 