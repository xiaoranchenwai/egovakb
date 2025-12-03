from django.db import models
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User
from function_lib.models.function import FunctionLib
import uuid
from dataset.models import DataSet
from setting.models import Model


class ScheduleTask(AppModelMixin):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid1,
        editable=False,
        verbose_name="主键id"
    )
    name = models.CharField(max_length=64, verbose_name="任务名称")
    desc = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="描述"
    )
    cron_expression = models.CharField(
        max_length=64,
        verbose_name="cron表达式"
    )
    function_lib = models.ForeignKey(
        FunctionLib,
        on_delete=models.CASCADE,
        verbose_name="关联函数"
    )
    params = models.JSONField(default=dict, verbose_name="函数参数")
    task_params = models.JSONField(
        default=dict, 
        verbose_name="任务参数", 
        help_text="任务配置参数，如标题提示词等"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="创建用户"
    )
    dataset = models.ForeignKey(
        DataSet,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name="关联知识库"
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="模型"
    )
    prompt = models.TextField(
        null=True,
        blank=True,
        verbose_name="提示词"
    )
    
    retain_thinking = models.BooleanField(
        verbose_name="保留思考内容",
        default=False,
        help_text="是否保留模型的思考过程") 

    class Meta:
        db_table = "schedule_task"
        app_label = "schedule"


class ScheduleTaskRecord(AppModelMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid1,
        editable=False,
        verbose_name="主键id"
    )
    task = models.ForeignKey(
        ScheduleTask,
        on_delete=models.CASCADE,
        verbose_name="关联任务"
    )
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    status = models.CharField(
        max_length=20,
        verbose_name="执行状态",
        choices=[
            ('SUCCESS', '成功'),
            ('FAILED', '失败'),
            ('RUNNING', '执行中')
        ]
    )
    result = models.TextField(null=True, blank=True, verbose_name="执行结果")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")

    class Meta:
        db_table = "schedule_task_record"
        app_label = "schedule" 