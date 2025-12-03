# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： tools.py
    @date：2024/7/22 11:18
    @desc:
"""
import time
from django.db import connection
from django.db.models import QuerySet
from django.db.utils import InterfaceError, OperationalError

from common.config.embedding_config import ModelManage
from setting.models import Model
from setting.models_provider import get_model
from django.utils.translation import gettext_lazy as _


def get_model_by_id(_id, user_id, max_retries=3):
    """
    获取模型数据，带重试机制处理连接异常
    """
    for attempt in range(max_retries):
        try:
            model = QuerySet(Model).filter(id=_id).first()
            # 手动关闭数据库连接
            connection.close()
            if model is None:
                raise Exception(_('Model does not exist'))
            if (model.permission_type == 'PRIVATE' and
                    str(model.user_id) != str(user_id)):
                raise Exception(_('No permission to use this model') +
                                f"{model.name}")
            return model
        except (InterfaceError, OperationalError) as e:
            if attempt == max_retries - 1:
                raise e
            # 等待一段时间后重试
            time.sleep(0.1 * (attempt + 1))
            # 强制关闭并重新建立连接
            connection.close()


def get_model_instance_by_model_user_id(model_id, user_id, **kwargs):
    """
    获取模型实例,根据模型相关数据
    @param model_id:  模型id（支持多个模型ID，以逗号分隔，默认使用第一个）
    @param user_id:   用户id
    @return:          模型实例
    """    
    model = get_model_by_id(model_id, user_id)
    return ModelManage.get_model(model_id,
                                 lambda _id: get_model(model, **kwargs))
