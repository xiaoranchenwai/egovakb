# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： chunk.py
    @date：2023/10/16 15:51
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import Permission, Group, Operate
from common.response import result
from common.util.common import query_params_to_single_dict
from dataset.serializers.common_serializers import BatchSerializer
from dataset.serializers.chunk_serializers import ChunkSerializers
from django.utils.translation import gettext_lazy as _


class Chunk(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                dynamic_tag=k.get('dataset_id')))
    def get(self, request: Request, dataset_id: str, document_id: str):
        q = ChunkSerializers.Query(
            data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                  'document_id': document_id})
        q.is_valid(raise_exception=True)
        return result.success(q.list())

    @action(methods=['POST'], detail=False)
    @has_permissions(
        lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                dynamic_tag=k.get('dataset_id')))
    def post(self, request: Request, dataset_id: str, document_id: str, paragraph_id: str):
        return result.success(
            ChunkSerializers.Create(data={'dataset_id': dataset_id, 'document_id': document_id, 'paragraph_id': paragraph_id}).save(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['UPDATE'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def put(self, request: Request, dataset_id: str, document_id: str, chunk_id: str):
            o = ChunkSerializers.Operate(
                data={"chunk_id": chunk_id, 'dataset_id': dataset_id, 'document_id': document_id})
            o.is_valid(raise_exception=True)
            return result.success(o.edit(request.data))

        @action(methods=['UPDATE'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str, chunk_id: str):
            o = ChunkSerializers.Operate(
                data={"dataset_id": dataset_id, 'document_id': document_id, "chunk_id": chunk_id})
            o.is_valid(raise_exception=True)
            return result.success(o.one())

        @action(methods=['DELETE'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str, chunk_id: str):
            o = ChunkSerializers.Operate(
                data={"dataset_id": dataset_id, 'document_id': document_id, "chunk_id": chunk_id})
            o.is_valid(raise_exception=True)
            return result.success(o.delete())

    class Batch(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['DELETE'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.MANAGE,
                                    dynamic_tag=k.get('dataset_id')))
        def delete(self, request: Request, dataset_id: str, document_id: str):
            return result.success(ChunkSerializers.Batch(
                data={"dataset_id": dataset_id, 'document_id': document_id}).batch_delete(request.data))
    
    class List(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        def get(self, request: Request, paragraph_id: str):
            return result.success(ChunkSerializers.List(data={'paragraph_id': paragraph_id}).list())    

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @has_permissions(
            lambda r, k: Permission(group=Group.DATASET, operate=Operate.USE,
                                    dynamic_tag=k.get('dataset_id')))
        def get(self, request: Request, dataset_id: str, document_id: str, current_page, page_size):
            d = ChunkSerializers.Query(
                data={**query_params_to_single_dict(request.query_params), 'dataset_id': dataset_id,
                      'document_id': document_id})
            d.is_valid(raise_exception=True)
            return result.success(d.page(current_page, page_size)) 