# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： py_lint.py
    @date：2024/9/30 15:35
    @desc:
"""
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from function_lib.serializers.py_lint_serializer import PyLintSerializer
from function_lib.swagger_api.py_lint_api import PyLintApi
from django.utils.translation import gettext_lazy as _


class PyLintView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary=_('Check code'),
                         operation_id=_('Check code'),
                         request_body=PyLintApi.get_request_body_api(),
                         tags=[_('Function')])
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request: Request):
        """
        运行 Pylint 静态检查并返回消息列表。
        - 成功与否均返回检查结果数组，其中包含 `type` 字段（如 error、warning）。
        - 当存在语法/解析错误时，消息中会体现具体错误信息，满足“检查报错返回报错信息”的要求。
        """
        messages = PyLintSerializer(data={'user_id': request.user.id}).pylint(request.data)
        for message in messages:
            if message['type'] == 'error':
                return result.error(message['message'])
        return result.success(messages)
