import uuid

from django.db import models

from application.models import Application
from common.mixins.app_model_mixin import AppModelMixin
from django.contrib.postgres.fields import ArrayField


class ApplicationSetting(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="应用id")
    show_history = models.BooleanField(default=True, verbose_name="是否显示历史记录")
    draggable = models.BooleanField(default=True, verbose_name="是否可拖拽")
    show_guide = models.BooleanField(default=True, verbose_name="是否显示引导")
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="AI头像")
    avatar_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="AI头像URL")
    float_icon = models.CharField(max_length=255, null=True, blank=True, verbose_name="悬浮图标")
    float_icon_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="悬浮图标URL")
    user_avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="用户头像")
    user_avatar_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="用户头像URL")
    disclaimer = models.BooleanField(default=False, verbose_name="是否显示免责声明")
    disclaimer_value = models.CharField(max_length=128, null=True, blank=True, verbose_name="免责声明内容")
    custom_theme = models.JSONField(default=dict, verbose_name="自定义主题")
    float_location = models.JSONField(default=dict, verbose_name="悬浮位置")
    authentication = models.BooleanField(default=False, verbose_name="是否鉴权")
    authentication_value = models.JSONField(default=dict, verbose_name="鉴权内容")
    access_token = models.CharField(max_length=128, verbose_name="用户公开访问 认证token", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="是否开启公开访问")
    access_num = models.IntegerField(default=100, verbose_name="访问次数")
    white_active = models.BooleanField(default=False, verbose_name="是否开启白名单")
    white_list = ArrayField(verbose_name="白名单列表",
                            base_field=models.CharField(max_length=128, blank=True)
                            , default=list)
    show_source = models.BooleanField(default=False, verbose_name="是否显示知识来源")

    language = models.CharField(max_length=10, verbose_name="语言", default=None, null=True)
    show_avatar = models.BooleanField(default=True, verbose_name="是否显示头像")
    show_user_avatar = models.BooleanField(default=True, verbose_name="是否显示用户头像")
    
    class Meta:
        db_table = "application_setting"