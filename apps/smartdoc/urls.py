"""
URL configuration for apps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import: from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function_lib: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import logging
import mimetypes
import os
import re

from django.http import HttpResponse, FileResponse, Http404, HttpResponseRedirect
from django.urls import path, re_path, include
from django.views import static
from rest_framework import status

from application.urls import urlpatterns as application_urlpatterns
from common.cache_data.static_resource_cache import get_index_html, get_static_file_content
from common.constants.cache_code_constants import CacheCodeConstants
from common.init.init_doc import init_doc
from common.response.result import Result
from common.util.cache_util import get_cache
from smartdoc import settings
from smartdoc.conf import PROJECT_DIR
from smartdoc.const import CONFIG
from setting.views.config_views import generate_frontend_config

def root_redirect(request):
    """
    根路径重定向到配置的前端路径
    """
    frontend_prefix = CONFIG.get("FRONTEND_PATH_PREFIX", "/ui/").rstrip("/")
    return HttpResponseRedirect(f"{frontend_prefix}/")


backend_api_prefix = CONFIG.get("BACKEND_API_PREFIX", "")
# 移除开头的斜杠，但保留路径结构
if backend_api_prefix.startswith("/"):
    backend_api_prefix = backend_api_prefix[1:]
if backend_api_prefix.endswith("/"):
    backend_api_prefix = backend_api_prefix[:-1]
    
if len(backend_api_prefix) > 0 and not backend_api_prefix.endswith('/'):
    backend_api_prefix += '/'
urlpatterns = [
    path("", root_redirect, name="root_redirect"),  # 根路径重定向
    path(backend_api_prefix + "config.js", generate_frontend_config, name="frontend_config"),  # 动态前端配置
    path(backend_api_prefix + "api/", include("users.urls")),
    path(backend_api_prefix + "api/", include("dataset.urls")),
    path(backend_api_prefix + "api/", include("setting.urls")),
    path(backend_api_prefix + "api/", include("application.urls")),
    path(backend_api_prefix + "api/", include("function_lib.urls")),
    path(backend_api_prefix + "api/", include("schedule.urls")),
]

def custom_static_serve(request, path, document_root=None, show_indexes=False):
    """
    自定义静态文件服务，正确设置MIME类型并动态替换路径
    """
    # 如果请求的是config.js，重定向到动态生成接口
    if path == 'config.js':
        return generate_frontend_config(request)
    
    try:
        # 构建完整的文件路径
        full_path = os.path.join(document_root, path)
        
        # 对于JavaScript和CSS文件，应用动态路径替换
        if path.endswith('.js') or path.endswith('.css'):
            content = get_static_file_content(full_path)
            if content is not None:
                # 确定正确的MIME类型
                if path.endswith('.js') or path.endswith('.mjs'):
                    content_type = 'application/javascript'
                elif path.endswith('.css'):
                    content_type = 'text/css'
                else:
                    content_type, _ = mimetypes.guess_type(path)
                    if content_type is None:
                        content_type = 'text/plain'
                
                # 返回处理后的内容
                response = HttpResponse(content, content_type=content_type)
                return response
        
        # 对于其他文件类型，使用Django的默认静态文件服务
        response = static.serve(request, path, document_root, show_indexes)
        
        # 设置正确的MIME类型
        if path.endswith('.js'):
            content_type, _ = mimetypes.guess_type(path)
            if content_type is None:
                content_type = 'application/javascript'
            response['Content-Type'] = content_type
        elif path.endswith('.mjs'):
            response['Content-Type'] = 'application/javascript'
        elif path.endswith('.css'):
            response['Content-Type'] = 'text/css'
        elif path.endswith('.json'):
            response['Content-Type'] = 'application/json'
        
        return response
    except Exception as e:
        raise Http404("Static file not found.")


def replace_frontend_paths(html_content):
    """
    动态替换HTML内容中的前端和后端路径前缀
    """
    frontend_prefix = CONFIG.get("FRONTEND_PATH_PREFIX", "/ui/")
    backend_api_prefix = CONFIG.get("BACKEND_API_PREFIX", "").strip("/")

    # 确保前端前缀格式正确（以/开头和结尾）
    if not frontend_prefix.startswith("/"):
        frontend_prefix = "/" + frontend_prefix
    if not frontend_prefix.endswith("/"):
        frontend_prefix = frontend_prefix + "/"

    # 替换前端路径
    if frontend_prefix != "/ui/":
        # 替换各种形式的 /ui/ 路径
        frontend_patterns = [
            (r'href="/ui/', f'href="{frontend_prefix}'),
            (r'src="/ui/', f'src="{frontend_prefix}'),
            (r'crossorigin href="/ui/', f'crossorigin href="{frontend_prefix}'),
            (r'crossorigin src="/ui/', f'crossorigin src="{frontend_prefix}'),
        ]

        for pattern, replacement in frontend_patterns:
            html_content = re.sub(pattern, replacement, html_content)

    # 替换API路径
    if backend_api_prefix:
        # 确保API前缀格式正确
        if not backend_api_prefix.startswith("/"):
            backend_api_prefix = "/" + backend_api_prefix

        # 替换各种形式的 /api/ 路径
        api_patterns = [
            (r'"/api/', f'"{backend_api_prefix}/api/'),
            (r"'/api/", f"'{backend_api_prefix}/api/"),
            (r'url\("/api/', f'url("{backend_api_prefix}/api/'),
            (r"url\('/api/", f"url('{backend_api_prefix}/api/"),
        ]

        for pattern, replacement in api_patterns:
            html_content = re.sub(pattern, replacement, html_content)

    return html_content


def pro():
    # 暴露静态主要是swagger资源
    urlpatterns.append(
        re_path(
            r"^static/(?P<path>.*)$",
            custom_static_serve,
            {"document_root": settings.STATIC_ROOT},
            name="static",
        ),
    )
    # 暴露ui静态资源 - 使用可配置的前端路径前缀
    frontend_prefix = CONFIG.get("FRONTEND_PATH_PREFIX", "/ui/")
    # 移除开头的斜杠，但保留路径结构用于正则表达式
    if frontend_prefix.startswith("/"):
        frontend_prefix = frontend_prefix[1:]
    if frontend_prefix.endswith("/"):
        frontend_prefix = frontend_prefix[:-1]
    
    if frontend_prefix:
        urlpatterns.append(
            re_path(
                rf"^{frontend_prefix}/(?P<path>.*)$",
                custom_static_serve,
                {"document_root": os.path.join(settings.STATIC_ROOT, "ui")},
                name="ui",
            ),
        )
    
    # 添加对原始/ui/路径的兼容性支持，确保静态资源能正确加载
    urlpatterns.append(
        re_path(
            r"^ui/(?P<path>.*)$",
            custom_static_serve,
            {"document_root": os.path.join(settings.STATIC_ROOT, "ui")},
            name="ui_compat",
        ),
    )


if not settings.DEBUG:
    pro()


def page_not_found(request, exception):
    """
    页面不存在处理
    """
    # 检查是否是API请求
    backend_api_prefix = CONFIG.get("BACKEND_API_PREFIX", "").strip("/")
    if request.path.startswith("/api/") or (backend_api_prefix and request.path.startswith(f"/{backend_api_prefix}/api/")):
        return Result(
            response_status=status.HTTP_404_NOT_FOUND, code=404, message="找不到接口"
        )
    
    # 获取配置的前端路径前缀
    frontend_prefix = CONFIG.get("FRONTEND_PATH_PREFIX", "/ui/").rstrip("/")
    
    # 检查请求路径是否匹配配置的前端路径前缀
    if request.path.startswith(f"{frontend_prefix}/"):
        # 这是前端路由请求，返回index.html
        index_path = os.path.join(PROJECT_DIR, "apps", "static", "ui", "index.html")
        if not os.path.exists(index_path):
            return HttpResponse("页面不存在", status=404)
        content = get_index_html(index_path)

        # 动态替换HTML中的前端路径前缀
        content = replace_frontend_paths(content)

        # 对于聊天页面，返回正常状态
        if request.path.startswith(f"{frontend_prefix}/chat/"):
            return HttpResponse(content, status=200)
        return HttpResponse(content, status=200, headers={"X-Frame-Options": "DENY"})
    
    # 其他路径返回404
    return HttpResponse("页面不存在", status=404)


handler404 = page_not_found
init_doc(urlpatterns, application_urlpatterns)
