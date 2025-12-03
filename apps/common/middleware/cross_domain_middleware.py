# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： cross_domain_middleware.py
    @date：2024/5/8 13:36
    @desc:
"""
import json

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from common.cache_data.application_api_key_cache import get_application_api_key
from smartdoc.const import CONFIG


class CrossDomainMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse(status=200,
                                headers={
                                    "Access-Control-Allow-Origin": "*",
                                    "Access-Control-Allow-Methods": "GET,POST,DELETE,PUT",
                                    "Access-Control-Allow-Headers": "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"})

    def process_response(self, request, response):
        # 如果response是application，且content是json，并且有字段是/api/image开头，同时BACKEND_API_PREFIX不为空，则加上BACKEND_API_PREFIX配置
        if (hasattr(response, 'headers') and response.headers.get('Content-Type') is not None and
            response.headers.get('Content-Type').startswith('application/json') and 
            len(CONFIG.get('BACKEND_API_PREFIX')) > 0):
            try:
                content = json.loads(response.content.decode('utf-8'))
                # 递归处理content中的所有字符串值
                modified_content = self._modify_image_urls(content, CONFIG.get('BACKEND_API_PREFIX'))
                if modified_content != content:
                    response.content = json.dumps(modified_content, ensure_ascii=False).encode('utf-8')
            except (json.JSONDecodeError, UnicodeDecodeError):
                # 如果解析失败，保持原样
                pass
        
        auth = request.META.get('HTTP_AUTHORIZATION')
        origin = request.META.get('HTTP_ORIGIN')
        if auth is not None and str(auth).startswith("application-") and origin is not None:
            application_api_key = get_application_api_key(str(auth), True)
            cross_domain_list = application_api_key.get('cross_domain_list', [])
            allow_cross_domain = application_api_key.get('allow_cross_domain', False)
            if allow_cross_domain:
                response['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
                response[
                    'Access-Control-Allow-Headers'] = "Origin,X-Requested-With,Content-Type,Accept,Authorization,token,app-id"
                if cross_domain_list is None or len(cross_domain_list) == 0:
                    response['Access-Control-Allow-Origin'] = "*"
                elif cross_domain_list.__contains__(origin):
                    response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = "*"
            response['Access-Control-Allow-Headers'] = "*"
        return response
    
    def _modify_image_urls(self, obj, prefix):
        """
        递归处理对象中的所有字符串值，如果以/api/image开头，则加上前缀
        """
        if isinstance(obj, dict):
            modified_obj = {}
            for key, value in obj.items():
                modified_obj[key] = self._modify_image_urls(value, prefix)
            return modified_obj
        elif isinstance(obj, list):
            return [self._modify_image_urls(item, prefix) for item in obj]
        elif isinstance(obj, str) and obj.startswith('/api/image'):
            data = prefix + obj
            if not data.startswith('/'):
                data = '/' + data
            data = data.replace('//api/image', '/api/image')
            return data
        else:
            return obj
