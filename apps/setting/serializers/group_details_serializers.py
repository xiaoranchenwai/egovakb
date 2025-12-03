# coding=utf-8
"""
    @project: maxkb
    @file： group_details_serializers.py
    @date：2024/11/01
    @desc: 分组详情序列化器
"""
from rest_framework import serializers

from setting.models.group import GroupDetails
from application.models.application import Application
from dataset.models.data_set import DataSet


class GroupDetailsSerializer(serializers.ModelSerializer):
    target_name = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupDetails
        fields = ['id', 'group', 'target_type', 'target_id', 'target_name', 'user']
        read_only_fields = ['id', 'user']

    def get_target_name(self, obj):
        """获取目标对象的名称"""
        if obj.target_type == 'APPLICATION':
            try:
                app = Application.objects.get(id=obj.target_id)
                return app.name
            except Application.DoesNotExist:
                return None
        elif obj.target_type == 'DATASET':
            try:
                dataset = DataSet.objects.get(id=obj.target_id)
                return dataset.name
            except DataSet.DoesNotExist:
                return None
        return None

    def validate(self, attrs):
        """验证目标对象是否存在"""
        target_type = attrs.get('target_type')
        target_id = attrs.get('target_id')
        
        if target_type == 'APPLICATION':
            if not Application.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({'target_id': '应用不存在'})
        elif target_type == 'DATASET':
            if not DataSet.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({'target_id': '数据集不存在'})
                
        return attrs 