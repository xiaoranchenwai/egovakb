# coding=utf-8
"""
    @project: maxkb
    @file： group_serializers.py
    @date：2024/11/01
    @desc: 分组序列化器
"""
import uuid
from typing import Dict

from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage
from setting.models.group import Group, GroupMember
from django.utils.translation import gettext_lazy as _
from users.serializers.user_serializers import UserSerializer
from django.db.models import Q
from application.models.application import Application
from dataset.models.data_set import DataSet


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'parent_id', 'user_id', 'create_time', 'update_time']
        read_only_fields = ['id', 'create_time', 'update_time']


class GroupMemberSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = GroupMember
        fields = ['id', 'group_id', 'user_id', 'user_info', 'avatar', 'create_time', 'update_time']
        read_only_fields = ['id', 'create_time', 'update_time']
    
    def get_avatar(self, obj):
        from users.models.user import UserSetting
        # 查询用户的头像设置
        avatar_setting = UserSetting.objects.filter(
            user_id=obj.user_id, 
            name='avatar'
        ).first()
        
        # 如果找到头像设置，返回其值
        if avatar_setting and avatar_setting.value:
            return avatar_setting.value
        
        # 否则返回默认头像
        return '/api/image/default-avatar.png'


class GroupTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'parent_id', 'user_id', 'children', 'members', 'create_time', 'update_time']
    
    def get_children(self, obj):
        user_id = self.context.get('user_id')
        is_admin = self.context.get('is_admin', False)
        accessible_groups = self.context.get('accessible_groups', set())
        
        # 如果是管理员，可以看到所有子分组
        if is_admin or user_id == obj.user_id:
            children = Group.objects.filter(parent_id=obj.id)
        else:
            # 否则只能看到自己有权限的子分组
            children = Group.objects.filter(
                Q(parent_id=obj.id) & (
                    Q(id__in=accessible_groups) |
                    Q(user_id=user_id)
                )
            )
        
        serializer = GroupTreeSerializer(
            children, 
            many=True, 
            context=self.context
        )
        return serializer.data
    
    def get_members(self, obj):
        user_id = self.context.get('user_id')
        is_admin = self.context.get('is_admin', False)
        accessible_groups = self.context.get('accessible_groups', set())
        
        # 如果是管理员、分组创建者或分组成员，可以看到分组成员
        if (is_admin or 
            user_id == obj.user_id or 
            str(obj.id) in accessible_groups or
            GroupMember.objects.filter(group_id=obj.id, user_id=user_id).exists()):
            members = GroupMember.objects.filter(group_id=obj.id)
            serializer = GroupMemberSerializer(members, many=True)
            return serializer.data
        
        return []


class GroupSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        user_id = serializers.UUIDField(
            required=True, 
            error_messages=ErrMessage.uuid(_('用户ID'))
        )
        name = serializers.CharField(
            required=False, 
            error_messages=ErrMessage.char(_('分组名称'))
        )
        parent_id = serializers.UUIDField(
            required=False, 
            error_messages=ErrMessage.uuid(_('父分组ID'))
        )

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            
            user_id = self.data.get('user_id')
            name = self.data.get('name')
            parent_id = self.data.get('parent_id')
            
            # 构建查询条件
            user_params = {'user_id': user_id}
            query_params = {}
            if name:
                query_params['name__icontains'] = name
            if parent_id:
                query_params['parent_id'] = parent_id
            
            group_members = GroupMember.objects.filter(**user_params)
            group_ids = [member.group_id for member in group_members]
            if len(group_ids) > 0:
                query_params['id__in'] = group_ids
            # 查询分组列表
            groups = Group.objects.filter(**query_params).order_by('name')
            all_group = Group.objects.all()
            group_map = {group.id: group for group in all_group}
            
            # 将所有上级group也添加到groups列表中
            groups_set = set(groups)
            added = True
            while added:
                added = False
                current_groups = list(groups_set)
                for group in current_groups:
                    if hasattr(group, 'parent_id') and group.parent_id and group.parent_id in group_map:
                        parent_group = group_map[group.parent_id]
                        if parent_group not in groups_set:
                            groups_set.add(parent_group)
                            added = True
            
            # 将集合转换回列表
            groups = list(groups_set)
            # 可选：如果需要保持排序
            groups.sort(key=lambda x: x.name)
            
            # 转换为列表返回
            return [
                {
                    'id': str(group.id),
                    'name': group.name,
                    'parent_id': str(group.parent_id) if group.parent_id else None,
                    'user_id': str(group.user_id),
                    'create_time': group.create_time,
                    'update_time': group.update_time
                }
                for group in groups
            ]

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(
            required=True, 
            error_messages=ErrMessage.uuid(_('用户ID'))
        )
        name = serializers.CharField(
            required=True, 
            max_length=128, 
            error_messages=ErrMessage.char(_('分组名称'))
        )
        parent_id = serializers.UUIDField(
            required=False, 
            error_messages=ErrMessage.uuid(_('父分组ID'))
        )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            
            user_id = self.data.get('user_id')
            name = self.data.get('name')
            parent_id = self.data.get('parent_id')
            
            # 检查同级分组名称是否重复
            query_params = {'user_id': user_id, 'name': name}
            if parent_id:
                query_params['parent_id'] = parent_id
            else:
                query_params['parent_id'] = None
                
            if QuerySet(Group).filter(**query_params).exists():
                raise AppApiException(500, _('同级分组名称已存在'))
                
            # 如果指定了父分组，检查父分组是否存在
            if parent_id and not QuerySet(Group).filter(
                id=parent_id, user_id=user_id
            ).exists():
                raise AppApiException(500, _('父分组不存在'))

        def insert(self, user_id):
            self.is_valid(raise_exception=True)
            
            name = self.data.get('name')
            parent_id = self.data.get('parent_id')
            
            # 创建分组
            group = Group(
                id=uuid.uuid1(),
                name=name,
                parent_id=parent_id,
                user_id=user_id
            )
            group.save()
            
            return {
                'id': str(group.id),
                'name': group.name,
                'parent_id': str(group.parent_id) if group.parent_id else None,
                'user_id': str(group.user_id),
                'create_time': group.create_time,
                'update_time': group.update_time
            }

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(
            required=True, 
            error_messages=ErrMessage.uuid(_('分组ID'))
        )
        user_id = serializers.UUIDField(
            required=True, 
            error_messages=ErrMessage.uuid(_('用户ID'))
        )

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            
            group_id = self.data.get('id')
            user_id = self.data.get('user_id')
            
            # 检查分组是否存在且属于当前用户
            group = QuerySet(Group).filter(
                id=group_id, user_id=user_id
            ).first()
            if not group:
                raise AppApiException(500, _('分组不存在或无权限访问'))
                
            return group

        def one(self):
            group = self.is_valid(raise_exception=True)
            
            return {
                'id': str(group.id),
                'name': group.name,
                'parent_id': str(group.parent_id) if group.parent_id else None,
                'user_id': str(group.user_id),
                'create_time': group.create_time,
                'update_time': group.update_time
            }

        def edit(self, data: Dict):
            group = self.is_valid(raise_exception=True)
            
            name = data.get('name')
            parent_id = data.get('parent_id')
            
            # 检查同级分组名称是否重复
            if name and name != group.name:
                query_params = {
                    'user_id': group.user_id,
                    'name': name
                }
                
                if group.parent_id:
                    query_params['parent_id'] = group.parent_id
                else:
                    query_params['parent_id'] = None
                    
                if QuerySet(Group).exclude(id=group.id).filter(
                    **query_params
                ).exists():
                    raise AppApiException(500, _('同级分组名称已存在'))
            
            # 检查父分组是否存在
            if parent_id and parent_id != str(group.parent_id):
                # 检查父分组是否存在
                if not QuerySet(Group).filter(
                    id=parent_id, user_id=group.user_id
                ).exists():
                    raise AppApiException(500, _('父分组不存在'))
                
                # 检查是否形成循环引用
                parent_group = QuerySet(Group).get(id=parent_id)
                current_parent = parent_group.parent
                while current_parent:
                    if str(current_parent.id) == str(group.id):
                        raise AppApiException(500, _('不能将子分组设为父分组'))
                    current_parent = current_parent.parent
            
            # 更新分组
            if name:
                group.name = name
            if parent_id is not None:  # 允许设置为None（顶级分组）
                group.parent_id = parent_id
                
            group.save()
            
            return {
                'id': str(group.id),
                'name': group.name,
                'parent_id': str(group.parent_id) if group.parent_id else None,
                'user_id': str(group.user_id),
                'create_time': group.create_time,
                'update_time': group.update_time
            }

        def delete(self):
            group = self.is_valid(raise_exception=True)
            
            # 检查是否有子分组
            if QuerySet(Group).filter(parent_id=group.id).exists():
                raise AppApiException(500, _('请先删除子分组'))
            
            # 删除分组
            group.delete()
            
            return True 