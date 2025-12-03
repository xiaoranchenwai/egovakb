"""
    @project: MaxKB
    @file： operate_log.py
    @desc: 操作日志相关接口
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.decorators import action

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from setting.serializers.operate_log_serializers import LogSerializer


class OperateLogPagination(PageNumberPagination):
    """
    操作日志分页
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    current_page = 1


class OperateLog(APIView):
    """
    操作日志接口
    """
    authentication_classes = [TokenAuth]
    
    @action(methods=['GET'], detail=False)
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request, current_page, page_size):
        """
        获取操作日志分页列表
        """
        # 创建分页器
        paginator = OperateLogPagination()
        paginator.page_size = int(page_size)
        paginator.current_page = int(current_page)
        # 解析查询参数
        query_params = {
            'start_time': request.query_params.get('start_time'),
            'end_time': request.query_params.get('end_time'),
            'menu': request.query_params.get('menu'),
            'operate': request.query_params.get('operate'),
            'status': request.query_params.get('status'),
            'user_name': request.query_params.get('user_name')
        }
        
        # 调用序列化器获取分页数据
        result_data = LogSerializer.get_paginated_logs(
            query_params, paginator.current_page, paginator.page_size, request, paginator
        )
        
        return result.success(result_data)


class MenuOperateOption(APIView):
    """
    获取菜单操作选项
    """
    authentication_classes = [TokenAuth]
    
    @action(methods=['GET'], detail=False)
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request):
        """
        获取日志中的菜单和操作选项
        """
        result_data = LogSerializer.get_menu_operate_options()
        return result.success(result_data)


class ExportOperateLog(APIView):
    """
    导出操作日志
    """
    authentication_classes = [TokenAuth]
    
    @action(methods=['POST'], detail=False)
    @has_permissions(RoleConstants.ADMIN)
    def post(self, request):
        """
        导出操作日志为Excel
        """
        # 获取请求参数
        query_params = {
            'start_time': request.data.get('start_time'),
            'end_time': request.data.get('end_time'),
            'menu': request.data.get('menu'),
            'operate': request.data.get('operate'),
            'status': request.data.get('status'),
            'user_name': request.data.get('user_name')
        }
        
        # 调用序列化器导出日志
        return LogSerializer.export_logs(query_params) 