# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_search_knowledge_base_node.py
    @date：2024/6/3 17:52
    @desc: 知识库子系统检索节点接口定义
"""
import re
from typing import Type

from django.core import validators
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.common import flat_map
from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _


class KnowledgeBaseSettingSerializer(serializers.Serializer):
    # 第三方知识库HTTP地址
    knowledge_base_url = serializers.URLField(required=True,
                                             error_messages=ErrMessage.char(_("Knowledge base URL")))
    # 知识库访问密钥
    knowledge_base_key = serializers.CharField(required=True, max_length=500,
                                              error_messages=ErrMessage.char(_("Knowledge base key")))
    # 选择的知识库ID
    selected_knowledge_base_id = serializers.CharField(required=True, max_length=100,
                                                       error_messages=ErrMessage.char(_("Selected knowledge base ID")))
    # 需要查询的条数
    top_n = serializers.IntegerField(required=True,
                                     error_messages=ErrMessage.integer(_("Reference segment number")))
    # 相似度 0-1之间
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                        error_messages=ErrMessage.float(_('similarity')))
    # 检索模式：全文检索、向量检索等
    search_mode = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^fulltext|vector|hybrid|content|search_vector|embedding_vector$"),
                                  message=_("The type only supports fulltext|vector|hybrid|content|search_vector|embedding_vector"), code=500)
    ], error_messages=ErrMessage.char(_("Retrieval Mode")))
    # 最大引用字符数
    max_paragraph_char_number = serializers.IntegerField(required=True,
                                                         error_messages=ErrMessage.float(_("Maximum number of words in a quoted segment")))


class SearchKnowledgeBaseStepNodeSerializer(serializers.Serializer):
    # 外部知识库服务地址
    knowledge_base_url = serializers.CharField(required=True, error_messages=ErrMessage.char("外部知识库服务地址"))
    # API密钥
    knowledge_base_key = serializers.CharField(required=True, error_messages=ErrMessage.char("API密钥"))
    # 知识库列表（支持对象数组格式，如[{id: 1, name: 'xxx'}]）
    knowledge_base_list = serializers.ListField(required=False, error_messages=ErrMessage.list("知识库列表"))
    # 知识库ID列表（向后兼容）
    knowledge_base_id_list = serializers.ListField(required=False, error_messages=ErrMessage.list("知识库ID列表"))
    # 检索模式
    search_mode = serializers.CharField(required=False, default='embedding')
    # 返回条数
    top_n = serializers.IntegerField(required=False, default=3)
    # 相似度阈值
    similarity = serializers.FloatField(required=False, default=0.6)
    # 最大段落字符数
    max_paragraph_char_number = serializers.IntegerField(required=False, default=5000)
    # 检索问题引用地址
    question_reference_address = serializers.ListField(required=True)
    # 是否只展示命中分块
    show_hit_block = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        """
        自定义验证：确保至少提供knowledge_base_list或knowledge_base_id_list之一
        """
        knowledge_base_list = attrs.get('knowledge_base_list')
        knowledge_base_id_list = attrs.get('knowledge_base_id_list')
        
        if not knowledge_base_list and not knowledge_base_id_list:
            raise serializers.ValidationError({
                'knowledge_base_list': _('知识库列表或知识库ID列表至少需要提供一个')
            })
        
        return attrs

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


def get_paragraph_list(chat_record, node_id):
    return flat_map([chat_record.details[key].get('paragraph_list', []) for key in chat_record.details if
                     (chat_record.details[
                          key].get('type', '') == 'search-knowledge-base-node') and chat_record.details[key].get(
                         'paragraph_list', []) is not None and key == node_id])


class ISearchKnowledgeBaseStepNode(INode):
    type = 'search-knowledge-base-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SearchKnowledgeBaseStepNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('question_reference_address')[0],
            self.node_params_serializer.data.get('question_reference_address')[1:])
        exclude_paragraph_id_list = []
        if self.flow_params_serializer.data.get('re_chat', False):
            history_chat_record = self.flow_params_serializer.data.get('history_chat_record', [])
            paragraph_id_list = [p.get('id') for p in flat_map(
                [get_paragraph_list(chat_record, self.runtime_node_id) for chat_record in history_chat_record if
                 chat_record.problem_text == question])]
            exclude_paragraph_id_list = list(set(paragraph_id_list))

        return self.execute(**self.node_params_serializer.data, question=str(question),
                            exclude_paragraph_id_list=exclude_paragraph_id_list)

    def execute(self, knowledge_base_setting, question,
                exclude_paragraph_id_list=None,
                **kwargs) -> NodeResult:
        pass