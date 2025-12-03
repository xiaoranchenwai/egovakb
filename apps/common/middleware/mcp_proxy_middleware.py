# coding=utf-8
"""
    @project: maxkb
    @file： mcp_proxy_middleware.py
    @date：2024/6/19
    @desc: MCP服务代理中间件，将/api/v1/mcp的请求转发到MCP服务
"""
import json
import logging
import urllib.parse
import requests
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.deprecation import MiddlewareMixin

from smartdoc.const import CONFIG

max_kb = logging.getLogger("max_kb")


class MCPProxyMiddleware(MiddlewareMixin):
    """
    MCP服务代理中间件
    将/api/v1/mcp的请求转发到MCP服务
    """
    def process_request(self, request):
        # 处理以/api/v1/mcp开头的请求 或者 /mcp-xxx/sse
        if (not request.path.startswith('/api/v1/mcp') and 
                not request.path.startswith('/mcp-')):
            return None
            
        # 获取MCP服务地址
        mcp_server = CONFIG.get('MCP_SSE_SERVER', '')
        if not mcp_server:
            max_kb.error("MCP_SSE_SERVER is not set")
            return HttpResponse(
                json.dumps({"message": "MCP服务未启用"}),
                content_type="application/json",
                status=404
            )
        if mcp_server.endswith('/'):
            mcp_server = mcp_server[:-1]
            
        # 构建转发URL
        forward_path = request.path
        if not forward_path.startswith('/'):
            forward_path = '/' + forward_path
            
        # 完整的转发URL
        forward_url = f"{mcp_server}{forward_path}"
        
        # 添加查询参数
        if request.GET:
            query_string = urllib.parse.urlencode(request.GET, doseq=True)
            forward_url = f"{forward_url}?{query_string}"
            
        method = request.method.lower()
        headers = {
            k: v for k, v in request.META.items() 
            if k.startswith('HTTP_')
        }
        
        # 转换Django特定的HTTP头到标准HTTP头
        headers_new = {}
        for key in headers:
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-')
                # 转换为首字母大写的标准格式
                header_name = '-'.join(
                    word.capitalize() for word in header_name.split('-')
                )
                headers_new[header_name] = headers[key]
            else:
                headers_new[key] = headers[key]
        
        headers = headers_new
                
        # 处理特殊的授权头，确保只有一个标准格式的Authorization头
        if 'HTTP_AUTHORIZATION' in request.META:
            headers['Authorization'] = request.META['HTTP_AUTHORIZATION']
        
        # 删除可能重复的授权头变体
        for key in list(headers.keys()):
            if key.lower() == 'authorization' and key != 'Authorization':
                headers['Authorization'] = headers.pop(key)
                
        # 保留部分原始头信息
        if 'CONTENT_TYPE' in request.META:
            headers['Content-Type'] = request.META['CONTENT_TYPE']

        # 获取请求体
        data = request.body
        
        # 设置正确的Content-Length
        if data:
            headers['Content-Length'] = str(len(data))
        elif 'Content-Length' in headers:
            # 如果没有请求体，确保Content-Length为0或移除它
            if headers['Content-Length'] == '':
                headers['Content-Length'] = '0'
        
        # 从MCP服务URL中提取Host信息并设置Host头
        parsed_url = urllib.parse.urlparse(mcp_server)
        new_host = parsed_url.netloc
        headers['Host'] = new_host
        
        # 移除不需要的头信息（但保留我们刚设置的Host）
        headers.pop('HOST', None)  # 移除可能的大写HOST
        
        try:
            # 发送请求到MCP服务
            max_kb.info(
                f"转发请求到MCP服务: {method.upper()} {forward_url}"
            )
            max_kb.info(f"转发前路径: {request.path}")
            max_kb.info(f"转发后路径: {forward_path}")
            max_kb.info(f"新Host头: {new_host}")
            max_kb.info(f"请求头: {headers}")
            max_kb.info(f"请求体长度: {len(data) if data else 0}")
            
            if method == 'get':
                max_kb.info("Executing GET request")
                response = requests.get(
                    forward_url, headers=headers, stream=True, timeout=30
                )
            elif method == 'post':
                max_kb.info("Executing POST request")
                response = requests.post(
                    forward_url, headers=headers, data=data, 
                    stream=True, timeout=30
                )
            elif method == 'put':
                max_kb.info("Executing PUT request")
                response = requests.put(
                    forward_url, headers=headers, data=data, 
                    stream=True, timeout=30
                )
            elif method == 'delete':
                max_kb.info("Executing DELETE request")
                response = requests.delete(
                    forward_url, headers=headers, data=data, 
                    stream=True, timeout=30
                )
            else:
                return HttpResponse(
                    json.dumps({"error": "Unsupported HTTP method"}),
                    content_type="application/json",
                    status=405
                )
                
            # 记录响应信息
            max_kb.info(f"Response status code: {response.status_code}")
            max_kb.info(f"Response headers: {response.headers}")
            
            # 尝试将响应内容解析为JSON
            try:
                response_data = response.json()  # 解析为JSON
            except ValueError:
                response_data = response.content  # 如果解析失败，保留原始内容
            
            # 根据响应类型选择合适的响应对象
            is_chunked = response.headers.get('Transfer-Encoding') == 'chunked'
            is_sse = response.headers.get('Content-Type', '').startswith(
                'text/event-stream'
            )
            
            if is_chunked or is_sse:
                # 处理流式响应
                max_kb.info("Returning streaming response")
                
                def generate():
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            yield chunk
                
                proxy_response = StreamingHttpResponse(
                    streaming_content=generate(),
                    status=response.status_code,
                    content_type=response.headers.get('Content-Type')
                )
            else:
                # 处理普通响应
                if (isinstance(response_data, dict) and 
                        response_data.get('code') == 0):
                    response_data['code'] = 200
                
                max_kb.info("Returning regular response")
                proxy_response = HttpResponse(
                    content=json.dumps(response_data),  # 确保内容为JSON格式
                    status=response.status_code,
                    content_type=response.headers.get(
                        'Content-Type', 'application/json'
                    )
                )
            
            # 复制所有响应头
            for header, value in response.headers.items():
                if header.lower() not in [
                    'content-length', 'content-encoding', 'transfer-encoding',
                    'connection', 'keep-alive', 'proxy-authenticate', 
                    'proxy-authorization', 'te', 'trailers', 'upgrade'
                ]:
                    proxy_response[header] = value
                    
            return proxy_response
            
        except Exception as e:
            max_kb.error(f"Error proxying request to MCP service: {e}")
            return HttpResponse(
                json.dumps({
                    "error": f"Failed to connect to MCP service: {str(e)}"
                }),
                content_type="application/json",
                status=502
            ) 