# coding=utf-8
"""
    @project: maxkb
    @file： group.py
    @date：2024/11/01
    @desc: 分组管理视图
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.response import result
from common.util.common import query_params_to_single_dict
from setting.serializers.group_serializers import (
    GroupSerializer, GroupMemberSerializer, GroupTreeSerializer
)
from setting.models.group import GroupMember, GroupDetails
from setting.models.group import Group as GroupModel
from users.models import User


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    
    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Group.objects.filter(user_id=user_id)
        
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        user_id = request.user.id
        root_groups = Group.objects.filter(user_id=user_id, parent=None)
        serializer = GroupTreeSerializer(root_groups, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        members = GroupMember.objects.filter(group=group)
        serializer = GroupMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': _('User ID is required')}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': _('User not found')}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查用户是否已经在其他分组中
        existing_member = GroupMember.objects.filter(user_id=user_id).first()
        if existing_member:
            if existing_member.group_id == group.id:
                return Response({'error': _('User is already a member of this group')}, 
                               status=status.HTTP_400_BAD_REQUEST)
            else:
                # 如果用户在其他分组，先移除
                existing_member.delete()
        
        member = GroupMember.objects.create(group=group, user=user)
        serializer = GroupMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response({'error': _('User ID is required')}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            member = GroupMember.objects.get(group=group, user_id=user_id)
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except GroupMember.DoesNotExist:
            return Response({'error': _('Member not found')}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def available_users(self, request):
        # 获取所有未分配到任何分组的用户
        assigned_user_ids = GroupMember.objects.values_list('user_id', flat=True)
        available_users = User.objects.exclude(id__in=assigned_user_ids)
        
        from users.serializers.user_serializers import UserSerializer
        serializer = UserSerializer(available_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_application(self, request, pk=None):
        """添加应用到分组"""
        group = self.get_object()
        app_id = request.data.get('application_id')
        
        # 检查应用是否已在其他分组
        existing = GroupDetails.objects.filter(
            target_type='APPLICATION',
            target_id=app_id
        ).first()
        
        if existing:
            if existing.group_id == group.id:
                return Response({'detail': '应用已在该分组中'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            # 从原分组移除
            existing.delete()
            
        # 添加到新分组
        GroupDetails.objects.create(
            group=group,
            target_type='APPLICATION',
            target_id=app_id,
            user=request.user
        )
        
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """获取分组下的应用列表"""
        group = self.get_object()
        app_ids = GroupDetails.objects.filter(
            group=group,
            target_type='APPLICATION'
        ).values_list('target_id', flat=True)
        
        from application.models import Application
        from application.serializers import ApplicationSerializer
        
        apps = Application.objects.filter(id__in=app_ids)
        serializer = ApplicationSerializer(apps, many=True)
        return Response(serializer.data)

class Group(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取分组列表'),
                         operation_id=_('获取分组列表'),
                         tags=[_('分组')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        # 如果是管理员，则可以查看所有分组
        if request.user.role == 'ADMIN':
            # 查询所有分组
            groups = GroupModel.objects.all().order_by('name')
            return result.success([
                {
                    'id': str(group.id),
                    'name': group.name,
                    'parent_id': str(group.parent_id) if group.parent_id else None,
                    'user_id': str(group.user_id),
                    'create_time': group.create_time,
                    'update_time': group.update_time
                }
                for group in groups
            ])
        
        # 非管理员只能查看自己的分组
        return result.success(
            GroupSerializer.Query(
                data={**query_params_to_single_dict(request.query_params), 
                      'user_id': request.user.id}).list(
                with_valid=True))

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('创建分组'),
                         operation_id=_('创建分组'),
                         tags=[_('分组')])
    @has_permissions(PermissionConstants.TEAM_CREATE)
    def post(self, request: Request):
        return result.success(
            GroupSerializer.Create(data={**request.data, 'user_id': str(request.user.id)}).insert(request.user.id))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('更新分组'),
                             operation_id=_('更新分组'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def put(self, request: Request, group_id: str):
            return result.success(
                GroupSerializer.Operate(data={'id': group_id, 'user_id': request.user.id}).edit(request.data))

        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('删除分组'),
                             operation_id=_('删除分组'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_DELETE)
        def delete(self, request: Request, group_id: str):
            return result.success(
                GroupSerializer.Operate(data={'id': group_id, 'user_id': request.user.id}).delete())

        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取分组详情'),
                             operation_id=_('获取分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, group_id: str):
            return result.success(
                GroupSerializer.Operate(data={'id': group_id, 'user_id': request.user.id}).one())

    class Members(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取分组成员列表'),
                             operation_id=_('获取分组成员列表'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, group_id: str):
            try:
                # if request.user.role == RoleConstants.ADMIN.name:
                group = GroupModel.objects.get(id=group_id)
                # else:
                #     group = GroupModel.objects.get(id=group_id, user_id=request.user.id)
                members = GroupMember.objects.filter(group=group)
                serializer = GroupMemberSerializer(members, many=True)
                return result.success(serializer.data)
            except Exception as e:
                return result.error(_(f'分组不存在: {e}'))
    
    class AddMember(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('添加分组成员'),
                             operation_id=_('添加分组成员'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def post(self, request: Request, group_id: str):
            try:
                group = GroupModel.objects.get(id=group_id, user_id=request.user.id)
                user_id = request.data.get('user_id')
                
                if not user_id:
                    return result.error(_('用户ID不能为空'))
                
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return result.error(_('用户不存在'))
                
                # 检查用户是否已经在其他分组中
                existing_member = GroupMember.objects.filter(user_id=user_id).first()
                if existing_member:
                    if existing_member.group_id == group.id:
                        return result.error(_('用户已经是该分组的成员'))
                    else:
                        # 如果用户在其他分组，先移除
                        existing_member.delete()
                
                member = GroupMember.objects.create(group=group, user=user)
                serializer = GroupMemberSerializer(member)
                return result.success(serializer.data)
            except Group.DoesNotExist:
                return result.error(_('分组不存在'))
    
    class RemoveMember(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('移除分组成员'),
                             operation_id=_('移除分组成员'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def delete(self, request: Request, group_id: str, user_id: str):
            try:
                if request.user.role == RoleConstants.ADMIN.name:
                    group = GroupModel.objects.get(id=group_id)
                else:
                    group = GroupModel.objects.get(id=group_id, user_id=request.user.id)
                
                try:
                    member = GroupMember.objects.get(group=group, user_id=user_id)
                    member.delete()
                    return result.success(True)
                except GroupMember.DoesNotExist:
                    return result.error(_('成员不存在'))
            except Group.DoesNotExist:
                return result.error(_('分组不存在'))
    
    class AvailableUsers(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取可用用户列表'),
                             operation_id=_('获取可用用户列表'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, group_id: str):
            # 获取所有未分配到任何分组的用户
            assigned_user_ids = GroupMember.objects.values_list('user_id', flat=True)
            available_users = User.objects.exclude(id__in=assigned_user_ids)
            
            from users.serializers.user_serializers import UserSerializer
            serializer = UserSerializer(available_users, many=True)
            return result.success(serializer.data)

    class Tree(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取分组树'),
                             operation_id=_('获取分组树'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request):
            user_id = request.user.id
            
            # 如果用户是管理员，则可以查看所有分组
            if request.user.role == 'ADMIN':
                top_groups = GroupModel.objects.filter(parent_id=None)
                # 管理员可以访问所有分组
                serializer = GroupTreeSerializer(top_groups, many=True, 
                                               context={'user_id': user_id, 
                                                       'is_admin': True})
            else:
                # 查找用户所属的所有分组
                user_groups = GroupMember.objects.filter(user_id=user_id).values_list('group_id', flat=True)
                
                # 查找这些分组的所有父分组（向上追溯）
                parent_groups = set()
                groups_to_check = list(user_groups)
                
                while groups_to_check:
                    group_id = groups_to_check.pop(0)
                    try:
                        group = GroupModel.objects.get(id=group_id)
                        if group.parent_id and group.parent_id not in parent_groups:
                            parent_groups.add(group.parent_id)
                            groups_to_check.append(group.parent_id)
                    except Exception as e:
                        continue
                
                # 合并用户所属分组和父分组
                accessible_groups = set(user_groups) | parent_groups
                
                # 获取用户可访问的顶级分组
                top_groups = GroupModel.objects.filter(
                    Q(parent_id=None) & (
                        Q(id__in=accessible_groups) |
                        Q(user_id=user_id) |
                        Q(id__in=GroupMember.objects.filter(user_id=user_id).values_list('group_id', flat=True))
                    )
                )
                
                serializer = GroupTreeSerializer(top_groups, many=True, 
                                               context={'user_id': user_id, 
                                                       'accessible_groups': accessible_groups})
            
            return result.success(serializer.data)

class AvailableApplications(APIView):
    """获取可添加到分组的应用列表"""
    
    def get(self, request, group_id):
        user_id = request.user.id
        
        # 检查分组是否存在且用户有权限
        try:
            group = Group.objects.get(id=group_id)
            if str(group.user_id) != str(user_id):
                # 检查用户是否是分组成员
                if not GroupMember.objects.filter(group_id=group_id, user_id=user_id).exists():
                    return Response({"code": 403, "message": "无权访问此分组"})
        except Group.DoesNotExist:
            return Response({"code": 404, "message": "分组不存在"})
        
        # 获取已经在分组中的应用ID
        existing_app_ids = GroupDetails.objects.filter(
            group_id=group_id,
            target_type='APPLICATION'
        ).values_list('target_id', flat=True)
        
        # 获取用户的所有应用，排除已在分组中的
        from application.models.application import Application
        applications = Application.objects.filter(
            user_id=user_id
        ).exclude(
            id__in=existing_app_ids
        ).values('id', 'name')
        
        return Response({
            "code": 0,
            "message": "success",
            "data": list(applications)
        }) 