# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： static_resource_cache.py
    @date：2024/7/25 11:30
    @desc:
"""
import re
import os
from common.constants.cache_code_constants import CacheCodeConstants
from common.util.cache_util import get_cache
from smartdoc.const import CONFIG


def replace_frontend_paths(content):
    """
    替换内容中的硬编码前端路径为动态路径
    """
    # 获取当前配置的前端路径前缀
    frontend_path_prefix = CONFIG.get('FRONTEND_PATH_PREFIX', '/ui/')
    
    # 确保路径以/开头和结尾
    if not frontend_path_prefix.startswith('/'):
        frontend_path_prefix = '/' + frontend_path_prefix
    if not frontend_path_prefix.endswith('/'):
        frontend_path_prefix = frontend_path_prefix + '/'
    
    # 如果内容已经包含正确的前缀，则不需要替换
    if frontend_path_prefix in content and frontend_path_prefix != '/ui/':
        return content
    
    # 替换所有硬编码的路径为动态路径
    # 只替换特定的旧路径模式，避免重复替换
    old_path_patterns = [
        r'/egova/large-model/ui/',  # 旧的完整路径
        r'(?<!/my-test-app)/ui/'    # 只替换不在/my-test-app前面的/ui/
    ]
    
    for pattern in old_path_patterns:
        content = re.sub(pattern, frontend_path_prefix, content)
    
    return content


# @get_cache(cache_key=lambda index_path: index_path,
#            version=CacheCodeConstants.STATIC_RESOURCE_CACHE.value)
def get_index_html(index_path):
    """
    获取动态替换路径后的index.html内容
    """
    file = open(index_path, "r", encoding='utf-8')
    content = file.read()
    file.close()
    
    return replace_frontend_paths(content)


def get_static_file_content(file_path):
    """
    获取动态替换路径后的静态文件内容（JavaScript、CSS等）
    """
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            content = file.read()
        return replace_frontend_paths(content)
    except UnicodeDecodeError:
        # 如果是二进制文件（如图片），直接返回原始内容
        with open(file_path, "rb") as file:
            return file.read()
    except Exception as e:
        # 处理其他异常
        return None
