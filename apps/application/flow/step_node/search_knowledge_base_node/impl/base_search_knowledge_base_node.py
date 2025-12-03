# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_search_knowledge_base_node.py
    @date：2024/6/4 11:56
    @desc: 知识库子系统检索节点基础实现
"""
import requests
import json
from typing import List, Dict
from datetime import datetime

from application.flow.i_step_node import NodeResult
from application.flow.step_node.search_knowledge_base_node.i_search_knowledge_base_node import ISearchKnowledgeBaseStepNode
from common.util.common import flat_map


def get_none_result(question):
    """返回空结果"""
    return NodeResult(
        {'paragraph_list': [], 'is_hit_handling_method': [], 'question': question, 'data': '',
         'directly_return': ''}, {})


def reset_title(title):
    """重置标题格式"""
    if title is None or len(title.strip()) == 0:
        return ""
    else:
        return f"#### {title}\n"


class BaseSearchKnowledgeBaseNode(ISearchKnowledgeBaseStepNode):
    """知识库子系统检索节点基础实现类"""

    def save_context(self, details, workflow_manage):
        """保存上下文信息"""
        result = details.get('paragraph_list', [])
        directly_return = '\n'.join(
            [f"{paragraph.get('title', '')}:{paragraph.get('content')}" for paragraph in result if
             paragraph.get('is_hit_handling_method')])
        self.context['paragraph_list'] = result
        self.context['question'] = details.get('question')
        self.context['run_time'] = details.get('run_time')
        self.context['is_hit_handling_method_list'] = [row for row in result if row.get('is_hit_handling_method')]
        self.context['data'] = '\n'.join(
            [f"{paragraph.get('title', '')}:{paragraph.get('content')}" for paragraph in
             result])[0:5000]
        self.context['directly_return'] = directly_return

    def execute(self, question, exclude_paragraph_id_list=None, **kwargs) -> NodeResult:
        """执行知识库子系统检索"""
        self.context['question'] = question
        
        # 从kwargs中提取参数
        knowledge_base_url = kwargs.get('knowledge_base_url')
        knowledge_base_key = kwargs.get('knowledge_base_key')
        
        # 处理知识库ID参数，支持多种格式
        knowledge_base_list = kwargs.get('knowledge_base_list')
        if knowledge_base_list:
            # 如果是对象数组，提取ID列表
            if isinstance(knowledge_base_list, list) and len(knowledge_base_list) > 0:
                if isinstance(knowledge_base_list[0], dict):
                    # 对象数组格式 [{id: 1, name: 'xxx'}, ...]
                    knowledge_base_id = [item.get('id') for item in knowledge_base_list if item.get('id')]
                else:
                    # 简单ID数组格式 [1, 2, 3]
                    knowledge_base_id = knowledge_base_list
            else:
                knowledge_base_id = knowledge_base_list
        else:
            # 向后兼容：优先使用knowledge_base_id_list，如果没有则使用knowledge_base_id
            knowledge_base_id = kwargs.get('knowledge_base_id_list') or kwargs.get('knowledge_base_id')
        search_setting = {
            'search_mode': kwargs.get('search_mode', 'content'),
            'top_n': kwargs.get('top_n', 3),
            'similarity': kwargs.get('similarity', 0.5),
            'max_paragraph_char_number': kwargs.get('max_paragraph_char_number', 5000),
            # 混合搜索权重参数
            'content_weight': kwargs.get('content_weight', 0.3),
            'search_vector_weight': kwargs.get('search_vector_weight', 0.3),
            'embedding_vector_weight': kwargs.get('embedding_vector_weight', 0.4)
        }
        
        try:
            # 调用第三方知识库检索接口
            search_result = self.call_knowledge_base_api(
                knowledge_base_url, knowledge_base_key, knowledge_base_id, search_setting, question
            )
            
            if not search_result or search_result.get('code') != 0:
                return get_none_result(question)
            
            # 处理检索结果
            paragraph_list = self.process_search_result(search_result.get('data', {}).get('list', []), search_setting)
            
            # 按相似度排序
            paragraph_list = sorted(paragraph_list, key=lambda p: p.get('similarity', 0), reverse=True)
            
            # 如果只展示命中分块
            if kwargs.get('show_hit_block', False):
                for row in paragraph_list:
                    if row.get('chunk_data') is not None and len(row.get('content', '')) > 0:
                        row['content'] = row.get('chunk_data')
            
            return NodeResult({
                'paragraph_list': paragraph_list,
                'is_hit_handling_method_list': [row for row in paragraph_list if row.get('is_hit_handling_method')],
                'data': '\n'.join(
                    [f"{reset_title(paragraph.get('title', ''))}{paragraph.get('content')}" for paragraph in
                     paragraph_list])[0:5000],
                'directly_return': '\n'.join(
                    [paragraph.get('content') for paragraph in
                     paragraph_list if
                     paragraph.get('is_hit_handling_method')]),
                'question': question
            }, {})
            
        except Exception as e:
            # 记录错误日志
            print(f"Knowledge base search error: {str(e)}")
            return get_none_result(question)

    def call_knowledge_base_api(self, knowledge_base_url, knowledge_base_key, knowledge_base_id, search_setting, question):
        """调用第三方知识库检索API"""
        # 构建检索API URL
        if not knowledge_base_url.endswith('/'):
            knowledge_base_url += '/'
        url = f"{knowledge_base_url}api/v1/datasets-search/search"
        
        headers = {
            'Authorization': knowledge_base_key,
            'User-Agent': 'EgovaKB',
            'Content-Type': 'application/json'
        }
        
        # 处理多个知识库ID，确保为整数列表
        if isinstance(knowledge_base_id, list):
            dataset_ids = [int(id) for id in knowledge_base_id if str(id).isdigit()]
        else:
            dataset_ids = [int(knowledge_base_id)] if str(knowledge_base_id).isdigit() else []
        
        # 构建POST请求体，按照DatasetSearchRequest模型
        request_body = {
            'dataset_ids': dataset_ids,
            'query': question,
            'search_mode': search_setting.get('search_mode', 'content'),
            'limit': search_setting.get('top_n', 3),  # 使用limit替代top_n
            'similarity_threshold': search_setting.get('similarity', 0.5)
        }
        
        # 为embedding_vector模式确保设置similarity_threshold
        if search_setting.get('search_mode') == 'embedding_vector':
            request_body['similarity_threshold'] = search_setting.get('similarity', 0.5)
        
        # 添加混合搜索权重参数（如果需要）
        if search_setting.get('search_mode') == 'hybrid':
            request_body.update({
                'content_weight': search_setting.get('content_weight', 0.3),
                'search_vector_weight': search_setting.get('search_vector_weight', 0.3),
                'embedding_vector_weight': search_setting.get('embedding_vector_weight', 0.4)
            })
            
        try:
            response = requests.post(url, headers=headers, json=request_body, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Knowledge base API request failed: {str(e)}")
            return None

    def process_search_result(self, search_data, search_setting):
        """处理搜索结果数据"""
        paragraph_list = []
        similarity_threshold = search_setting.get('similarity', 0.6)
        
        for item in search_data:
            # 使用relevance_score作为相似度
            similarity = item.get('relevance_score', 0)
            
            paragraph = {
                'id': str(item.get('id', '')),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'similarity': item.get('embedding_score', 0),
                'is_hit_handling_method': similarity > similarity_threshold,
                'update_time': item.get('created_at', ''),
                'create_time': item.get('created_at', ''),
                'dataset_id': str(item.get('dataset_id', '')),
                'chunk_id': str(item.get('id', '')),
                'chunk_data': item.get('content', ''),
                'document_id': str(item.get('dataset', {}).get('id', '')),
                'document_url': '',
                'hit_handling_method': 'directly_return' if similarity > similarity_threshold else 'none',
                'directly_return_similarity': similarity_threshold
            }
            paragraph_list.append(paragraph)
        
        return paragraph_list

    def get_details(self, index: int, **kwargs):
        """获取节点详情"""
        return {
            'name': self.node.properties.get('stepName'),
            'question': self.context.get('question'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'paragraph_list': self.context.get('paragraph_list'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }