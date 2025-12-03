"""
    @project: MaxKB
    @file： log_serializers.py
    @desc: 操作日志序列化器
"""
import pandas as pd
from rest_framework import serializers
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from setting.models.log_management import Log
from common.util.field_message import ErrMessage
from common.db.search import page_search


class LogSerializerModel(serializers.ModelSerializer):
    """
    操作日志模型序列化器
    """
    class Meta:
        model = Log
        fields = '__all__'


class LogSerializer(serializers.Serializer):
    """
    操作日志序列化器
    """
    menu = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        error_messages=ErrMessage.char(_("操作菜单"))
    )
    operate = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        error_messages=ErrMessage.char(_("操作"))
    )
    operation_object = serializers.JSONField(
        required=False, allow_null=True,
        error_messages=ErrMessage.json(_("操作对象"))
    )
    user = serializers.JSONField(
        required=False, allow_null=True,
        error_messages=ErrMessage.json(_("用户信息"))
    )
    status = serializers.IntegerField(
        required=False, allow_null=True,
        error_messages=ErrMessage.integer(_("状态"))
    )
    ip_address = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        error_messages=ErrMessage.char(_("IP地址"))
    )
    details = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        error_messages=ErrMessage.char(_("详情"))
    )
    create_time = serializers.DateTimeField(
        required=False, allow_null=True,
        error_messages=ErrMessage.date(_("创建时间"))
    )
    
    class Meta:
        model = Log
        fields = '__all__'
    
    @staticmethod
    def get_paginated_logs(query_params, current_page, page_size, request, 
                           paginator):
        """
        获取分页的操作日志
        """
        # 创建查询序列化器
        serializer = LogSerializer.Query(data=query_params)
        serializer.is_valid(raise_exception=True)
        
        # 获取查询条件
        query = serializer.get_query_set()
        
        # 查询日志并排序
        logs = Log.objects.filter(query).order_by('-create_time')
        
        # 定义数据处理函数
        def post_records_handler(row):
            return LogSerializer(row).data
        
        # 使用统一的分页方法
        return page_search(current_page, page_size, logs, post_records_handler)
    
    @staticmethod
    def get_menu_operate_options():
        """
        获取菜单和操作选项
        """
        menu_list = Log.objects.values_list('menu', flat=True).distinct()
        operate_list = Log.objects.values_list('operate', flat=True).distinct()
        
        return {
            'menu_list': list(menu_list),
            'operate_list': list(operate_list)
        }
    
    @staticmethod
    def export_logs(query_params):
        """
        导出操作日志
        """
        # 创建查询序列化器
        serializer = LogSerializer.Query(data=query_params)
        serializer.is_valid(raise_exception=True)
        
        # 获取查询条件
        query = serializer.get_query_set()
        
        # 查询日志
        logs = Log.objects.filter(query).order_by('-create_time')
        serializer = LogExportSerializer(logs, many=True)
        
        # 转换为DataFrame
        df = pd.DataFrame(serializer.data)
        
        # 重命名列
        column_map = {
            'menu': '操作菜单',
            'operate': '操作',
            'operation_object': '操作对象',
            'user': '用户信息',
            'status': '状态',
            'ip_address': 'IP地址',
            'details': '详情',
            'create_time': '创建时间'
        }
        df.rename(columns=column_map, inplace=True)
        
        # 创建Excel响应
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=log.xlsx'
        
        # 写入Excel
        df.to_excel(response, index=False)
        
        return response
    
    class Query(serializers.Serializer):
        """
        操作日志查询序列化器
        """
        # start_time = serializers.DateTimeField(
        #     required=False, allow_null=True,
        #     error_messages=ErrMessage.date(_("开始时间"))
        # )
        # end_time = serializers.DateTimeField(
        #     required=False, allow_null=True,
        #     error_messages=ErrMessage.date(_("结束时间"))
        # )
        menu = serializers.CharField(
            required=False, allow_null=True, allow_blank=True,
            error_messages=ErrMessage.char(_("操作菜单"))
        )
        operate = serializers.CharField(
            required=False, allow_null=True, allow_blank=True,
            error_messages=ErrMessage.char(_("操作"))
        )
        status = serializers.IntegerField(
            required=False, allow_null=True,
            error_messages=ErrMessage.integer(_("状态"))
        )
        user_name = serializers.CharField(
            required=False, allow_null=True, allow_blank=True,
            error_messages=ErrMessage.char(_("用户名"))
        )
        
        def get_query_set(self):
            """
            获取查询条件
            """
            query = Q()
            if (self.validated_data.get('start_time') and
                    self.validated_data.get('end_time')):
                query &= Q(create_time__range=[
                    self.validated_data.get('start_time'),
                    self.validated_data.get('end_time')
                ])
            if self.validated_data.get('menu'):
                query &= Q(menu=self.validated_data.get('menu'))
            if self.validated_data.get('operate'):
                query &= Q(operate=self.validated_data.get('operate'))
            if self.validated_data.get('status') is not None:
                query &= Q(status=int(self.validated_data.get('status')))
            if self.validated_data.get('user_name'):
                query &= Q(
                    user__name__icontains=self.validated_data.get('user_name')
                )
            return query


class LogExportSerializer(serializers.ModelSerializer):
    """
    操作日志导出序列化器
    """
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Log
        fields = ['menu', 'operate', 'operation_object', 'user', 'status', 
                  'ip_address', 'details', 'create_time'] 