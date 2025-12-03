import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'
const prefix = '/dataset'

/**
 * 分块列表
 * @param 参数 dataset_id document_id
 * page {
              "current_page": "string",
              "page_size": "string",
            }
 * param {
          "content": "string",
          "chunk_index": number,
        }
 */
const getChunk: (
    dataset_id: string,
    document_id: string,
    page: pageRequest,
    param: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, page, param, loading) => {
    return get(
        `${prefix}/${dataset_id}/document/${document_id}/chunk/${page.current_page}/${page.page_size}`,
        param,
        loading
    )
}

/**
 * 删除分块
 * @param 参数 dataset_id, document_id, chunk_id
 */
const delChunk: (
    dataset_id: string,
    document_id: string,
    chunk_id: string,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, chunk_id, loading) => {
    return del(
        `${prefix}/${dataset_id}/document/${document_id}/chunk/${chunk_id}`,
        undefined,
        {},
        loading
    )
}

/**
 * 批量删除分块
 * @param 参数 dataset_id, document_id
 */
const delMulChunk: (
    dataset_id: string,
    document_id: string,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, document_id, data, loading) => {
    return del(
        `${prefix}/${dataset_id}/document/${document_id}/chunk/_batch`,
        undefined,
        { id_list: data },
        loading
    )
}

/**
 * 创建分块
 * @param 参数 
 * dataset_id, document_id
 * {
  "content": "string",
  "chunk_index": number,
  "char_length": number
    }
 */
const postChunk: (
    dataset_id: string,
    document_id: string,
    paragraph_id: string,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, paragraph_id, data, loading) => {
    return post(`${prefix}/${dataset_id}/document/${document_id}/paragraph/${paragraph_id}/chunk`,
        data,
        undefined,
        loading)
}

/**
 * 修改分块
 * @param 参数 
 * dataset_id, document_id, chunk_id
 * {
  "content": "string",
  "chunk_index": number,
  "char_length": number
    }
 */
const putChunk: (
    dataset_id: string,
    document_id: string,
    chunk_id: string,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, document_id, chunk_id, data, loading) => {
    return put(
        `${prefix}/${dataset_id}/document/${document_id}/chunk/${chunk_id}`,
        data,
        undefined,
        loading
    )
}

/**
 * 根据段落ID获取分块列表
 * @param 参数 paragraph_id
 * @description 打开对话框后，如果data的chunk_id不为空，调用此接口查询chunklist
 */
const getChunkList: (
    paragraph_id: string,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (paragraph_id, loading) => {
    return get(`/paragraph/${paragraph_id}/chunk/list`, {}, loading)
}

export default {
    getChunk,
    delChunk,
    putChunk,
    postChunk,
    delMulChunk,
    getChunkList
} 