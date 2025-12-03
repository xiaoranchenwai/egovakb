import uuid
from django.db import models
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Group(AppModelMixin):
    id = models.UUIDField(
        primary_key=True, 
        max_length=128,
        default=uuid.uuid1, 
        editable=False, 
        verbose_name="主键id"
    )
    name = models.CharField(max_length=128, verbose_name="分组名称")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        verbose_name="上级目录id"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="用户id"
    )
    
    class Meta:
        db_table = "group"


class GroupMember(AppModelMixin):
    id = models.UUIDField(
        primary_key=True, 
        max_length=128,
        default=uuid.uuid1, 
        editable=False, 
        verbose_name="主键id"
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        verbose_name="分组id"
    )
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="用户id"
    )
    
    class Meta:
        db_table = "group_member"
        unique_together = ['user']


class GroupDetails(AppModelMixin):
    """
    分组详情表，用于关联应用和数据集
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False, verbose_name="主键id")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="分组id")
    target_type = models.CharField(
        max_length=20,
        choices=[('APPLICATION', '应用'), ('DATASET', '数据集')],
        verbose_name="目标类型"
    )
    target_id = models.UUIDField(verbose_name="目标id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")

    class Meta:
        db_table = "group_details"
        unique_together = ['target_type', 'target_id']
