# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chunk_serializers.py
    @date：2023/10/16 15:51
    @desc: 分块序列化器
"""
import uuid
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from embedding.vector.base_vector import chunk_data_list
from embedding.models import SourceType
from common.util.common import bulk_create_in_batches
from dataset.serializers.common_serializers import get_embedding_model_id_by_dataset_id
from embedding.task.embedding import get_embedding_model
from common.event.listener_manage import ListenerManagement
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.field_message import ErrMessage
from dataset.models import Chunk, Document, DataSet
from django.utils.translation import gettext_lazy as _


def create_paragraph_chunks(paragraph_content: str, paragraph_id: str,
                            dataset_id: str, document_id: str,
                            chunk_patterns: str = None,
                            chunk_length: int = None) -> None:
    """
    对段落内容进行分块并批量插入数据库
    
    Args:
        paragraph_content: 段落内容
        paragraph_id: 段落ID
        dataset_id: 数据集ID
        document_id: 文档ID
        chunk_patterns: 分块模式（可选）
        chunk_length: 分块长度（可选）
    """
    # 准备分块数据
    ckd = {
        'source_type': SourceType.PARAGRAPH.value,
        'text': paragraph_content,
    }
    data_list = [ckd]
    
    # 执行分块
    chunk_list = chunk_data_list(data_list, chunk_patterns, chunk_length)
    
    # 创建分块模型列表
    chunk_model_list = []
    for index, chunk in enumerate(chunk_list):
        chunk_model_list.append(Chunk(
            id=uuid.uuid1(),
            paragraph_id=paragraph_id,
            dataset_id=dataset_id,
            document_id=document_id,
            content=chunk.get('text', ''),
            char_length=len(chunk.get('text', '')),
            chunk_index=index
        ))
    
    # 批量插入分块
    if chunk_model_list:
        bulk_create_in_batches(Chunk, chunk_model_list, batch_size=10000)


def create_content_chunks(content: str, chunk_patterns: str = None,
                          chunk_length: int = None) -> list:
    """
    对内容进行分块，返回分块列表（用于文档分割等场景）
    
    Args:
        content: 要分块的内容
        chunk_patterns: 分块模式（可选）
        chunk_length: 分块长度（可选）
        
    Returns:
        list: 分块列表
    """
    # 准备分块数据
    ckd = {
        'source_type': SourceType.PARAGRAPH.value,
        'text': content,
    }
    data_list = [ckd]
    
    # 执行分块
    chunk_list = chunk_data_list(data_list, chunk_patterns, chunk_length)
    
    return chunk_list


class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk
        fields = ['id', 'content', 'paragraph_id', 'document_id', 'dataset_id', 'chunk_index', 'char_length',
                  'create_time', 'update_time']


class ChunkInstanceSerializer(ApiMixin, serializers.Serializer):
    """
    分块实例对象
    """
    content = serializers.CharField(required=True, error_messages=ErrMessage.char(_('content')),
                                    max_length=1024,
                                    min_length=1,
                                    allow_null=True, allow_blank=True)

    chunk_index = serializers.IntegerField(required=False, error_messages=ErrMessage.integer(_('chunk index')))

    char_length = serializers.IntegerField(required=False, error_messages=ErrMessage.integer(_('char length')))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=1024, title=_('content'),
                                         description=_('content')),
                'chunk_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('chunk index'),
                                            description=_('chunk index')),
                'char_length': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('char length'),
                                           description=_('char length'))
            }
        )


class EditChunkSerializers(serializers.Serializer):
    content = serializers.CharField(required=False, max_length=1024, allow_null=True, allow_blank=True,
                                    error_messages=ErrMessage.char(_('content')))
    chunk_index = serializers.IntegerField(required=False, error_messages=ErrMessage.integer(_('chunk index')))


class ChunkSerializers(ApiMixin, serializers.Serializer):
    content = serializers.CharField(required=True, max_length=1024, error_messages=ErrMessage.char(_('content')))
    chunk_index = serializers.IntegerField(required=False, error_messages=ErrMessage.integer(_('chunk index')))

    class Batch(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            chunk_id_list = instance.get('id_list')
            if not chunk_id_list:
                return {}
            chunks = QuerySet(Chunk).filter(id__in=chunk_id_list)
            chunks.delete()
            return {}
    
    class List(serializers.Serializer):
        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('paragraph id')))
        
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=raise_exception)

        def list(self):
            self.is_valid()
            return [ChunkSerializer(row).data for row in QuerySet(Chunk).filter(paragraph_id=self.data.get('paragraph_id')).order_by('chunk_index')]

    class Operate(ApiMixin, serializers.Serializer):
        # 分块ID
        chunk_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('chunk id')))
        # 知识库ID
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('dataset id')))
        # 文档ID
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('document id')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=raise_exception)
            if not QuerySet(Chunk).filter(id=self.data.get('chunk_id')).exists():
                raise AppApiException(500, _('Chunk id does not exist'))

        @transaction.atomic
        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            chunk = QuerySet(Chunk).filter(id=self.data.get('chunk_id')).first()
            if not chunk:
                raise AppApiException(500, _(f'Chunk id {self.data.get("chunk_id")} does not exist'))
            if 'content' in instance:
                chunk.content = instance.get('content')
                if 'char_length' not in instance:
                    chunk.char_length = len(instance.get('content'))
            
            if 'chunk_index' in instance:
                chunk.chunk_index = instance.get('chunk_index')
                
            if 'char_length' in instance:
                chunk.char_length = instance.get('char_length')
                
            chunk.save()
            model_id = get_embedding_model_id_by_dataset_id(self.data.get('dataset_id'))
            embedding_model = get_embedding_model(model_id)
            ListenerManagement.embedding_by_chunk(chunk.id, embedding_model)
            return ChunkSerializer(chunk).data

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            chunk = QuerySet(Chunk).filter(id=self.data.get('chunk_id')).first()
            return ChunkSerializer(chunk).data

        def delete(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            chunk = QuerySet(Chunk).filter(id=self.data.get('chunk_id')).first()
            if chunk:
                ListenerManagement.delete_embedding_by_chunk(chunk.id)
                chunk.delete()                
            return {}

        @staticmethod
        def get_request_body_api():
            return EditChunkSerializers().get_request_body_api()

        @staticmethod
        def get_response_body_api():
            return ChunkSerializer().get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('dataset id')),
                   openapi.Parameter(name='document_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('document id')),
                   openapi.Parameter(name='chunk_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('chunk id'))]

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('document id')))
        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('paragraph id')))
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            # 验证文档是否存在
            if not QuerySet(Document).filter(id=self.data.get('document_id')).exists():
                raise AppApiException(500, _('Document id does not exist'))

        @transaction.atomic
        def save(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ChunkInstanceSerializer(data=instance).is_valid(raise_exception=True)
                
            content = instance.get('content')
            char_length = instance.get('char_length', len(content))
            chunk_index = instance.get('chunk_index', 0)
            
            chunk = Chunk(id=uuid.uuid1(),
                         dataset_id=self.data.get('dataset_id'),
                         document_id=self.data.get('document_id'),
                         paragraph_id=self.data.get('paragraph_id'),
                         content=content,
                         char_length=char_length,
                         chunk_index=chunk_index)
            chunk.save()
            model_id = get_embedding_model_id_by_dataset_id(self.data.get('dataset_id'))
            embedding_model = get_embedding_model(model_id)
            ListenerManagement.embedding_by_chunk(chunk.id, embedding_model)
            return ChunkSerializer(chunk).data

        @staticmethod
        def get_request_body_api():
            return ChunkInstanceSerializer().get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('dataset id')),
                   openapi.Parameter(name='document_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('document id'))]

    class Query(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(_('document id')))
        content = serializers.CharField(required=False)
        chunk_index = serializers.IntegerField(required=False)
        paragraph_id = serializers.UUIDField(required=False)  # 作为可选过滤条件

        def get_query_set(self):
            query = QuerySet(Chunk).filter(dataset_id=self.data.get('dataset_id'),
                                          document_id=self.data.get('document_id'))
            
            if self.data.get('paragraph_id'):
                query = query.filter(paragraph_id=self.data.get('paragraph_id'))
                
            if self.data.get('content'):
                query = query.filter(content__contains=self.data.get('content'))
                
            if self.data.get('chunk_index') is not None:
                query = query.filter(chunk_index=self.data.get('chunk_index'))
                
            return query.order_by('chunk_index')

        def list(self):
            return [ChunkSerializer(row).data for row in self.get_query_set()]

        def page(self, current_page, page_size):
            return page_search(self.get_query_set(), current_page, page_size,
                              lambda row: ChunkSerializer(row).data)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('dataset id')),
                   openapi.Parameter(name='document_id',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_STRING,
                                     required=True,
                                     description=_('document id')),
                   openapi.Parameter(name='content',
                                     in_=openapi.IN_QUERY,
                                     type=openapi.TYPE_STRING,
                                     required=False,
                                     description=_('content')),
                   openapi.Parameter(name='chunk_index',
                                     in_=openapi.IN_QUERY,
                                     type=openapi.TYPE_INTEGER,
                                     required=False,
                                     description=_('chunk index')),
                   openapi.Parameter(name='paragraph_id',
                                     in_=openapi.IN_QUERY,
                                     type=openapi.TYPE_STRING,
                                     required=False,
                                     description=_('paragraph id'))]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title='id',
                                        description='id'),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('content'),
                                             description=_('content')),
                    'paragraph_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('paragraph id'),
                                                 description=_('paragraph id')),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('document id'),
                                                description=_('document id')),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset id'),
                                               description=_('dataset id')),
                    'chunk_index': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('chunk index'),
                                                description=_('chunk index')),
                    'char_length': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('char length'),
                                               description=_('char length')),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                description=_('create time')),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                description=_('update time'))
                }
            ) 