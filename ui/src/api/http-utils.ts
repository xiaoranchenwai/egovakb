import { get, post, postStream, del, put, request, download } from '@/request/index'
import { Result } from '@/request/Result'

const getRequest: (api: string) => Promise<Result<any>> = (
    api
) => {
    return get(api)
}

const postRequest: (api: string, data: any) => Promise<Result<any>> = (
    api,
    data
) => {
    return post(api, data)
}

export default {
    getRequest,
    postRequest
}