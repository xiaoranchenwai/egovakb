# coding=utf-8
"""
    @project: maxkb
    @file： group_details.py
    @date：2024/11/01
    @desc: 分组详情管理视图
"""
import uuid
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.views import Request
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from application.serializers.application_serializers import ApplicationSerializer
from application.models.application import Application
from application.models.application_setting import ApplicationSetting
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants
from common.response import result
from setting.models.group import GroupMember
from setting.models.group import Group as GroupModel
from setting.models.group import GroupDetails as GroupDetailsModel
from setting.serializers.group_details_serializers import GroupDetailsSerializer


class GroupDetails(APIView):
    """
    分组详情的增删改查
    """
    authentication_classes = [TokenAuth]
    
    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary=_('获取分组详情列表'),
                         operation_id=_('获取分组详情列表'),
                         tags=[_('分组')])
    @has_permissions(PermissionConstants.TEAM_READ)
    def get(self, request: Request):
        """获取当前用户的所有分组详情"""
        queryset = GroupDetailsModel.objects.filter(user=request.user)
        serializer = GroupDetailsSerializer(queryset, many=True)
        return result.success(serializer.data)
    
    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('创建分组详情'),
                         operation_id=_('创建分组详情'),
                         tags=[_('分组')])
    @has_permissions(PermissionConstants.TEAM_EDIT)
    def post(self, request: Request):
        """创建分组详情"""
        serializer = GroupDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return result.success(serializer.data)
        
    class Operate(APIView):
        """
        单个分组详情的操作
        """
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取单个分组详情'),
                             operation_id=_('获取单个分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request, detail_id: str):
            """获取单个分组详情"""
            try:
                detail = GroupDetailsModel.objects.get(id=detail_id, user=request.user)
                serializer = GroupDetailsSerializer(detail)
                return result.success(serializer.data)
            except Exception as e:
                return result.error(_(f'分组详情不存在: {e}'))
        
        @action(methods=['PUT'], detail=False)
        @swagger_auto_schema(operation_summary=_('更新分组详情'),
                             operation_id=_('更新分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def put(self, request: Request, detail_id: str):
            """更新分组详情"""
            try:
                detail = GroupDetailsModel.objects.get(id=detail_id, user=request.user)
                serializer = GroupDetailsSerializer(detail, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return result.success(serializer.data)
            except Exception as e:
                return result.error(_(f'更新分组详情失败: {e}'))
        
        @action(methods=['DELETE'], detail=False)
        @swagger_auto_schema(operation_summary=_('删除分组详情'),
                             operation_id=_('删除分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_DELETE)
        def delete(self, request: Request, detail_id: str):
            """删除分组详情"""
            try:
                detail = GroupDetailsModel.objects.get(id=detail_id)
                detail.delete()
                return result.success(True)
            except Exception as e:
                return result.error(_(f'删除分组详情失败: {e}'))
    
    class BatchCreate(APIView):
        """
        批量创建分组详情
        """
        authentication_classes = [TokenAuth]
        
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('批量创建分组详情'),
                             operation_id=_('批量创建分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_EDIT)
        def post(self, request: Request):
            """批量创建分组详情"""
            items = request.data.get('items', [])
            if not items:
                return result.error(_('未提供任何项目'))
            
            with transaction.atomic():
                created_items = []
                for item in items:
                    serializer = GroupDetailsSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(user=request.user)
                    created_items.append(serializer.data)
            
            return result.success(created_items)
    
    class BatchDelete(APIView):
        """
        批量删除分组详情
        """
        authentication_classes = [TokenAuth]
        
        @action(methods=['POST'], detail=False)
        @swagger_auto_schema(operation_summary=_('批量删除分组详情'),
                             operation_id=_('批量删除分组详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_DELETE)
        def post(self, request: Request):
            """批量删除分组详情"""
            ids = request.data.get('ids', [])
            if not ids:
                return result.error(_('未提供任何ID'))
            
            deleted_count = GroupDetailsModel.objects.filter(
                id__in=ids, user=request.user
            ).delete()[0]
            
            return result.success({'deleted_count': deleted_count})
    
    class ByGroup(APIView):
        """
        获取指定分组的所有详情
        """
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(operation_summary=_('获取指定分组的所有详情'),
                             operation_id=_('获取指定分组的所有详情'),
                             tags=[_('分组')])
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request):
            """获取指定分组的所有详情"""
            group_id = request.query_params.get('group_id')
            if not group_id:
                return result.error(_('分组ID是必需的'))
            
            queryset = GroupDetailsModel.objects.filter(
                group_id=group_id, user=request.user
            )
            serializer = GroupDetailsSerializer(queryset, many=True)
            return result.success(serializer.data)

    class GroupDetailsTree(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @swagger_auto_schema(
            operation_summary=_('获取分组详情树'),
            operation_id=_('获取分组详情树'),
            tags=[_('分组详情')]
        )
        @has_permissions(PermissionConstants.TEAM_READ)
        def get(self, request: Request):
            user_id = request.user.id
            target_type = request.query_params.get('target_type', None)
            
            # 如果用户是管理员，则可以查看所有分组
            if request.user.role == RoleConstants.ADMIN.name:
                # 一次性获取所有分组
                all_groups = list(GroupModel.objects.all())
                # 按照ID创建映射，方便查找
                groups_dict = {str(group.id): group for group in all_groups}
                # 找出顶级分组
                top_groups = [group for group in all_groups if group.parent_id is None]
                
                # 一次性获取所有分组详情
                query = GroupDetailsModel.objects.all()
                if target_type:
                    query = query.filter(target_type=target_type)
                all_group_details = list(query)
                # 按分组ID分类
                group_details_map = {}
                for detail in all_group_details:
                    if str(detail.group_id) not in group_details_map:
                        group_details_map[str(detail.group_id)] = []
                    group_details_map[str(detail.group_id)].append(detail)
                
                # # 获取所有应用
                app_ids = [detail.target_id for detail in all_group_details 
                          if detail.target_type == 'APPLICATION']
                apps_dict = {
                    str(app.id): app 
                    for app in Application.objects.filter(id__in=app_ids)
                }
                
                # 一次性获取所有应用的access_token
                from application.models.api_key_model import ApplicationAccessToken
                app_tokens = {
                    str(token.application_id): token.access_token
                    for token in ApplicationAccessToken.objects.filter(application_id__in=app_ids)
                }
                
                # 构建结果
                result_data = self._build_admin_tree(
                    top_groups, 
                    groups_dict, 
                    group_details_map, 
                    apps_dict,
                    app_tokens,
                    target_type
                )
                
                return result.success(result_data)
            else:
                # 查找用户所属的所有分组（一次性查询）
                user_groups = list(GroupMember.objects.filter(
                    user_id=user_id
                ).values_list('group_id', flat=True))
                
                # 一次性获取所有分组
                all_groups = list(GroupModel.objects.all())
                # 按照ID创建映射，方便查找
                groups_dict = {str(group.id): group for group in all_groups}
                
                # 查找这些分组的所有父分组（向上追溯）
                parent_groups = set()
                groups_to_check = list(user_groups)
                
                while groups_to_check:
                    group_id = groups_to_check.pop(0)
                    group = groups_dict.get(str(group_id))
                    if group and group.parent_id and str(group.parent_id) not in parent_groups:
                        parent_groups.add(str(group.parent_id))
                        groups_to_check.append(group.parent_id)
                
                # 合并用户所属分组和父分组
                accessible_groups = set(map(str, user_groups)) | parent_groups
                
                # 找出顶级分组
                top_groups = [
                    group for group in all_groups 
                    if group.parent_id is None and (
                        str(group.id) in accessible_groups or 
                        str(group.user_id) == str(user_id)
                    )
                ]
                
                # 一次性获取所有分组详情
                query = GroupDetailsModel.objects.all()
                if target_type:
                    query = query.filter(target_type=target_type)
                all_group_details = list(query)
                # 按分组ID分类
                group_details_map = {}
                for detail in all_group_details:
                    if str(detail.group_id) not in group_details_map:
                        group_details_map[str(detail.group_id)] = []
                    group_details_map[str(detail.group_id)].append(detail)
                
                # 获取用户的应用
                applications = ApplicationSerializer.Query(
                    data={'user_id': request.user.id}).list(request.user.role)
                app_ids = [app.get('id') for app in applications]
                apps_dict = {
                    str(app.id): app 
                    for app in Application.objects.filter(id__in=app_ids)
                }
                
                # 一次性获取所有应用的access_token
                from application.models.api_key_model import ApplicationAccessToken
                app_tokens = {
                    str(token.application_id): token.access_token
                    for token in ApplicationAccessToken.objects.filter(application_id__in=app_ids)
                }
                
                # 构建结果
                result_data = self._build_user_tree(
                    top_groups, 
                    groups_dict, 
                    group_details_map, 
                    apps_dict,
                    app_tokens,
                    applications,
                    user_id,
                    accessible_groups,
                    target_type
                )
                
                return result.success(result_data)
        
        def _build_admin_tree(self, top_groups, groups_dict, group_details_map, apps_dict, app_tokens, target_type=None):
            """构建管理员分组树"""
            result_data = []
            
            for group in top_groups:
                group_data = {
                    'id': str(group.id),
                    'name': group.name,
                    'parent_id': str(group.parent_id) if group.parent_id else None,
                    'user_id': str(group.user_id),
                    'target_type': 'GROUP',
                    'create_time': group.create_time,
                    'update_time': group.update_time,
                    'children': []
                }
                
                # 添加子分组
                self._add_children_groups(
                    group, 
                    group_data, 
                    groups_dict, 
                    group_details_map, 
                    apps_dict,
                    app_tokens,
                    target_type,
                    None,
                    None,
                    is_admin=True
                )
                
                # 添加分组详情
                self._add_group_details(
                    group, 
                    group_data, 
                    group_details_map.get(str(group.id), []), 
                    apps_dict,
                    app_tokens
                )
                
                result_data.append(group_data)
            
            return result_data
        
        def _build_user_tree(self, top_groups, groups_dict, group_details_map, apps_dict, app_tokens,
                           applications, user_id, accessible_groups, target_type=None):
            """构建用户分组树"""
            result_data = []
            
            for group in top_groups:
                group_data = {
                    'id': str(group.id),
                    'name': group.name,
                    'parent_id': str(group.parent_id) if group.parent_id else None,
                    'user_id': str(group.user_id),
                    'target_type': 'GROUP',
                    'create_time': group.create_time,
                    'update_time': group.update_time,
                    'children': []
                }
                
                # 添加子分组
                self._add_children_groups(
                    group, 
                    group_data, 
                    groups_dict, 
                    group_details_map, 
                    apps_dict,
                    app_tokens,
                    target_type,
                    user_id,
                    accessible_groups,
                    is_admin=False
                )
                
                # 添加分组详情
                self._add_group_details(
                    group, 
                    group_data, 
                    group_details_map.get(str(group.id), []), 
                    apps_dict,
                    app_tokens
                )
                
                result_data.append(group_data)
            
            # 根据应用列表填充分组树
            # if applications:
            #     self._fill_group_with_applications(applications, result_data)
            
            return result_data
        
        def _add_children_groups(self, parent_group, parent_data, groups_dict, group_details_map, 
                               apps_dict, app_tokens, target_type, user_id, accessible_groups, is_admin=False):
            """添加子分组到父分组数据中"""
            # 获取所有子分组
            children = []
            for group in groups_dict.values():
                if group.parent_id == parent_group.id:
                    # 针对普通用户的权限过滤
                    if not is_admin and user_id and accessible_groups:
                        if (str(group.id) not in accessible_groups and
                            str(group.user_id) != str(user_id)):
                            continue
                    children.append(group)
            
            for child in children:
                child_data = {
                    'id': str(child.id),
                    'name': child.name,
                    'parent_id': str(child.parent_id) if child.parent_id else None,
                    'user_id': str(child.user_id),
                    'target_type': 'GROUP',
                    'create_time': child.create_time,
                    'update_time': child.update_time,
                    'children': []
                }
                
                # 递归添加子分组
                self._add_children_groups(
                    child, 
                    child_data, 
                    groups_dict, 
                    group_details_map, 
                    apps_dict,
                    app_tokens,
                    target_type,
                    user_id,
                    accessible_groups,
                    is_admin
                )
                
                # 添加分组详情
                self._add_group_details(
                    child, 
                    child_data, 
                    group_details_map.get(str(child.id), []), 
                    apps_dict,
                    app_tokens
                )
                
                parent_data['children'].append(child_data)
                
        def _add_group_details(self, group, group_data, details, apps_dict, app_tokens):
            """添加分组详情到分组数据中"""
            for detail in details:
                app_type = None
                app_avatar = None
                app_desc = None
                app_access_token = None
                
                if detail.target_type == 'APPLICATION':
                    app = apps_dict.get(str(detail.target_id))
                    if not app:
                        continue
                    
                    target_name = app.name
                    app_type = app.type
                    app_avatar = app.icon
                    app_desc = app.desc  # 获取应用描述
                    
                    # 从预先查询的字典中获取access_token
                    app_access_token = app_tokens.get(str(detail.target_id))
                else:
                    target_name = self._get_target_name(
                        detail.target_type, 
                        detail.target_id
                    )
                
                detail_data = {
                    'id': str(detail.id),
                    'group_id': str(detail.group_id),
                    'target_type': detail.target_type,
                    'target_id': str(detail.target_id),
                    'name': target_name,
                    'target_name': target_name,
                    'user_id': str(detail.user_id),
                    'create_time': detail.create_time,
                    'update_time': detail.update_time
                }
                
                if app_type:
                    detail_data['type'] = app_type
                if app_avatar:
                    detail_data['avatar'] = app_avatar
                if app_desc and detail.target_type == 'APPLICATION':
                    detail_data['desc'] = app_desc
                if app_access_token and detail.target_type == 'APPLICATION':
                    detail_data['access_token'] = app_access_token
                
                group_data['children'].append(detail_data)
                
        def _get_application_settings(self, app_ids):
            """获取应用的设置"""
            app_settings = ApplicationSetting.objects.filter(application_id__in=app_ids)
            return app_settings
        
        def _get_target_name(self, target_type, target_id):
            """获取目标对象的名称"""
            if target_type == 'APPLICATION':
                from application.models.application import Application
                try:
                    app = Application.objects.get(id=target_id)
                    return app.name
                except Application.DoesNotExist:
                    return f"未知应用({target_id})"
            elif target_type == 'DATASET':
                from dataset.models.data_set import DataSet
                try:
                    dataset = DataSet.objects.get(id=target_id)
                    return dataset.name
                except Exception as e:
                    return f"未知数据集({target_id}):{e}"
            else:
                return f"未知类型({target_id})"
        
        def _fill_group_with_applications(self, applications, groups_tree):
            """根据应用列表填充分组树
            
            Args:
                applications: 应用列表
                groups_tree: 分组树结构
            """
            # 创建分组ID到分组节点的映射，便于快速查找
            group_map = {}
            
            # 递归构建分组映射
            def build_group_map(groups):
                for group in groups:
                    group_map[group['id']] = group
                    if group.get('children'):
                        children_groups = [
                            child for child in group['children'] 
                            if child.get('target_type') == 'GROUP'
                        ]
                        if children_groups:
                            build_group_map(children_groups)
            
            build_group_map(groups_tree)
            
            # 遍历应用并添加到对应分组
            for app in applications:
                group_id = app.get('group_id')
                if not group_id or group_id not in group_map:
                    continue
                
                # 创建应用节点
                app_node = {
                    'id': str(app.get('id')),
                    'group_id': str(group_id),
                    'target_type': 'APPLICATION',
                    'target_id': str(app.get('id')),
                    'name': app.get('name'),
                    'target_name': app.get('name'),
                    'user_id': str(app.get('user_id')),
                    'create_time': app.get('create_time'),
                    'update_time': app.get('update_time'),
                    'type': app.get('type'),
                    'avatar': app.get('icon')
                }
                
                # 检查应用是否已存在于分组中
                is_app_exists = False
                for child in group_map[group_id]['children']:
                    if (child.get('target_type') == 'APPLICATION' and 
                        child.get('target_id') == app_node['target_id']):
                        is_app_exists = True
                        break
                
                # 如果应用不存在于分组中，则添加
                if not is_app_exists:
                    group_map[group_id]['children'].append(app_node) 