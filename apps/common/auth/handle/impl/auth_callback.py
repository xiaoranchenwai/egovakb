# coding=utf-8
"""
    @project: qabot
    @file： mcp_callback_token.py
    @date：2024/5/14
    @desc:  MCP平台回调认证处理器
"""
import logging
from django.db.models import QuerySet

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import RoleConstants, get_permission_list_by_role, Auth
from common.exception.app_exception import AppAuthenticationFailed
from users.models import User
from django.core import cache
from users.models.user import get_user_dynamics_permission
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
token_cache = cache.caches['token_cache']


class AuthCallback(AuthBaseHandle):
    """
    处理MCP平台回调的认证请求
    流程：
    1. egovakb平台向MCP平台发起请求，在请求头中携带egovakb平台的认证信息
    2. MCP平台回调egovakb平台的回调接口，携带原始认证信息
    3. egovakb平台验证认证信息，返回用户信息和权限信息
    """
    
    def support(self, request, token: str, get_token_details):
        """
        判断是否支持此类型的认证请求
        - 检查请求头中是否包含MCP平台特定标识
        - 检查token信息是否有效
        """
        # 检查请求头中是否包含MCP特定标识
        if 'AUTH_CALLBACK' not in request.META:
            return False
            
        # 检查token详情
        auth_details = get_token_details()
        if auth_details is None:
            return False
            
        # 检查token是否包含用户ID和正确的类型
        return 'id' in auth_details and auth_details.get('type') == AuthenticationType.USER.value

    def handle(self, request, token: str, get_token_details):
        """
        处理MCP平台回调的认证请求
        - 验证token的有效性
        - 获取用户信息
        - 获取用户权限
        - 返回用户信息和权限信息
        """
        try:
            # 从缓存中获取token信息
            cache_token = token_cache.get(token)
            if cache_token is None:
                logger.warning(f"MCP回调认证失败: token已过期")
                raise AppAuthenticationFailed(1002, _('Login expired'))
                
            # 获取token详情
            auth_details = get_token_details()
            
            # 获取用户信息
            user = QuerySet(User).get(id=auth_details['id'])
            
            # 获取用户角色和权限
            rule = RoleConstants[user.role]
            permission_list = get_permission_list_by_role(RoleConstants[user.role])
            
            # 获取用户的应用和知识库的权限
            permission_list += get_user_dynamics_permission(str(user.id))
            
            # 记录MCP回调认证成功
            logger.info(f"MCP回调认证成功: 用户ID={user.id}, 用户名={user.username}")
            
            # 返回用户信息和权限信息
            return user, Auth(role_list=[rule],
                             permission_list=permission_list,
                             client_id=str(user.id),
                             client_type=AuthenticationType.USER.value,
                             current_role=rule,
                             source='mcp')  # 添加来源标识
                             
        except Exception as e:
            logger.error(f"MCP回调认证处理异常: {str(e)}")
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect! illegal user')) 