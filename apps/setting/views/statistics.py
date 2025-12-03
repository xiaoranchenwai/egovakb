# coding=utf-8
"""
    @project: maxkb
    @file： statistics.py
    @date：2024/10/30
    @desc: 用户统计视图
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from setting.serializers.statistics_serializers import StatisticsSerializer
from django.utils.translation import gettext_lazy as _


class Statistics(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取统计数据'),
                         operation_id=_('获取统计数据'),
                         tags=[_('统计')])
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(
            StatisticsSerializer.Query(
                data=query_params_to_single_dict(request.query_params)).list(
                with_valid=True))
        
    class Detail(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取用户详细统计数据'),
                            operation_id=_('获取用户详细统计数据'),
                            tags=[_('统计')])
        @has_permissions(RoleConstants.ADMIN)
        def get(self, request: Request):
            params = query_params_to_single_dict(request.query_params)
            detail = StatisticsSerializer.Detail().get_detail(
                username=params.get('username'),
                start_time=params.get('start_time'),
                end_time=params.get('end_time')
            )
            return result.success(detail) 