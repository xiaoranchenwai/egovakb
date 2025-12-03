import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'

export default {
  saveSetting(data: any) {
    return post('/user/settings', data)
  },
  
  // 添加获取设置的方法
  getSetting(param: any) {
    return get(`/user/settings`, param)
  }
} 