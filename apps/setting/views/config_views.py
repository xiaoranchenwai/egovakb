# -*- coding: utf-8 -*-
"""
前端配置动态生成视图
"""
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from smartdoc.const import CONFIG


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_frontend_config(request):
    """
    动态生成前端配置文件config.js
    根据后端配置动态生成前端所需的配置参数
    """
    # 获取配置参数
    frontend_path_prefix = CONFIG.get("FRONTEND_PATH_PREFIX", "/ui/")
    backend_api_prefix = CONFIG.get("BACKEND_API_PREFIX", "")
    show_mcp = CONFIG.get("MCP_SSE_SERVER", "") != ""
    
    # 确保路径格式正确
    if not frontend_path_prefix.startswith("/"):
        frontend_path_prefix = "/" + frontend_path_prefix
    if not frontend_path_prefix.endswith("/"):
        frontend_path_prefix = frontend_path_prefix + "/"
    
    if backend_api_prefix and not backend_api_prefix.startswith("/"):
        backend_api_prefix = "/" + backend_api_prefix
    
    # 确保backend_api_prefix不以斜杠结尾，避免与前端拼接时产生双斜杠
    if backend_api_prefix.endswith("/"):
        backend_api_prefix = backend_api_prefix[:-1]
    
    # 生成JavaScript配置内容
    config_content = f"""window.APP_CONFIG = {{
  VITE_STATIC_PATH: '{frontend_path_prefix}',
  VITE_API_PATH: '{backend_api_prefix}',
  SHOW_MCP: {str(show_mcp).lower()}
}};"""
    
    # 返回JavaScript内容
    response = HttpResponse(config_content, content_type='application/javascript; charset=utf-8')
    
    # 添加缓存控制头，避免浏览器缓存配置文件
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response