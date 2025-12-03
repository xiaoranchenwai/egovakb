# coding=utf-8
"""
    @project: qabot
    @file： mcp_callback.py
    @date：2024/5/14
    @desc:  MCP回调接口
"""
import logging
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.authenticate import TokenAuth
from common.response import result

logger = logging.getLogger(__name__)


class MCPCallback(APIView):
    """
    MCP平台回调接口
    用于处理MCP平台转发的请求
    """
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(
        operation_summary="MCP回调授权接口",
        operation_id="mcp_callback_auth",
        responses=result.get_default_response(),
        security=[],
        tags=["MCP集成"]
    )
    def post(self, request: Request):
        """
        MCP回调授权接口
        处理从MCP平台转发的请求，验证用户身份和权限
        
        MCP平台将请求转发给当前egovakb平台，携带原始认证信息
        egovakb平台验证认证信息，返回用户信息和权限
        """
        try:
            # 记录MCP回调请求
            logger.info(f"收到MCP回调请求: 用户ID={request.user.id}, 角色={request.auth.current_role}")
            
            # 准备响应数据
            auth_info = {
                "user_id": str(request.user.id),
                "username": request.user.username,
                "email": request.user.email,
                "role": request.auth.current_role.name,
                "permissions": [p.name for p in request.auth.permission_list]
            }
            
            # 返回用户验证信息
            return result.success(auth_info)
            
        except Exception as e:
            logger.error(f"处理MCP回调请求异常: {str(e)}")
            return result.failed(500, f"处理回调请求失败: {str(e)}") 