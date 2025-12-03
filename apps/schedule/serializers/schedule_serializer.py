from rest_framework import serializers
from django.db.models import QuerySet, Q
from common.constants.permission_constants import RoleConstants
from schedule.models.schedule import ScheduleTask
from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _
from common.exception.app_exception import AppApiException
from common.db.search import page_search
from users.models.user import User, UserSetting


class ScheduleTaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleTask
        fields = [
            'id', 'name', 'desc', 'cron_expression',
            'function_lib_id', 'params', 'is_active',
            'user_id', 'create_time', 'update_time',
            'dataset_id', 'model_id', 'prompt',
            'retain_thinking', 'task_params'
        ]


class CreateScheduleTask(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        error_messages=ErrMessage.char(_('task name'))
    )
    desc = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    cron_expression = serializers.CharField(
        required=True,
        error_messages=ErrMessage.char(_('cron expression'))
    )
    function_lib_id = serializers.UUIDField(required=True)
    params = serializers.JSONField(required=False, default=dict)
    is_active = serializers.BooleanField(required=False, default=True)
    model_id = serializers.UUIDField(required=False, allow_null=True)
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class EditScheduleTask(serializers.Serializer):
    name = serializers.CharField(required=False)
    desc = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )
    cron_expression = serializers.CharField(required=False)
    function_lib_id = serializers.UUIDField(required=False)
    params = serializers.JSONField(required=False)
    is_active = serializers.BooleanField(required=False)
    model_id = serializers.UUIDField(required=False, allow_null=True)
    prompt = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ScheduleTaskSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        select_user_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        role = serializers.CharField(required=False, allow_null=True, allow_blank=True)

        def get_query_set(self):            
            if self.data.get('role') == RoleConstants.ADMIN.name:
                query_set = QuerySet(ScheduleTask)
            else:
                query_set = QuerySet(ScheduleTask).filter(user_id=self.data.get('user_id'))
            
            if self.data.get('name') is not None:
                query_set = query_set.filter(name__icontains=self.data.get('name'))
                
            if self.data.get('select_user_id') is not None:
                query_set = query_set.filter(user_id=self.data.get('select_user_id'))
                
            query_set = query_set.order_by("-create_time")
            return query_set
        
        @staticmethod
        def add_user_info(tasks):
            if not tasks:
                return tasks
                
            # 收集所有用户ID
            user_ids = []
            if isinstance(tasks, list):
                user_ids = [task.get('user_id') for task in tasks]
            else:
                user_ids = [task.get('user_id') for task in tasks.get('records', [])]
                
            # 批量查询用户信息
            users = {
                str(user.id): user 
                for user in User.objects.filter(id__in=user_ids)
            }
            
            # 批量查询用户设置（头像）
            user_settings = {
                str(setting.user_id): setting
                for setting in UserSetting.objects.filter(
                    user_id__in=user_ids,
                    setting_type='config',
                    name='avatar'
                )
            }
            
            # 为每个任务添加用户名和头像
            if isinstance(tasks, list):
                for task in tasks:
                    user_id = task.get('user_id')
                    if str(user_id) in users:
                        task['username'] = users[str(user_id)].username
                    if str(user_id) in user_settings:
                        task['user_avatar'] = user_settings[str(user_id)].value
            else:
                for task in tasks.get('records', []):
                    user_id = task.get('user_id')
                    if str(user_id) in users:
                        task['username'] = users[str(user_id)].username
                    if str(user_id) in user_settings:
                        task['user_avatar'] = user_settings[str(user_id)].value
                        
            return tasks

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tasks = [ScheduleTaskModelSerializer(item).data for item in self.get_query_set()]
            return self.add_user_info(tasks)

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tasks = page_search(
                current_page, 
                page_size, 
                self.get_query_set(),
                post_records_handler=lambda row: ScheduleTaskModelSerializer(row).data
            )
            return self.add_user_info(tasks)

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        def create(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                CreateScheduleTask(data=instance).is_valid(
                    raise_exception=True)
            if instance.get('user_id') is None:
                instance['user_id'] = self.data.get('user_id')
            if instance.get('username'):
                del instance['username']
            if instance.get('user_avatar'):
                del instance['user_avatar']
            if instance.get('value'):
                del instance['value']
            if instance.get('title_prompt'):
                del instance['title_prompt']
            task = ScheduleTask(
                **instance
            )
            task.save()
            return ScheduleTaskModelSerializer(task).data

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        user_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(ScheduleTask).filter(
                id=self.data.get('id'),
                user_id=self.data.get('user_id')
            ).exists():
                raise AppApiException(500, _('Task not found'))

        def edit(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                EditScheduleTask(data=instance).is_valid(raise_exception=True)

            task = QuerySet(ScheduleTask).filter(
                id=self.data.get('id')
            ).first()

            for key, value in instance.items():
                setattr(task, key, value)
            task.save()

            return ScheduleTaskModelSerializer(task).data

        def delete(self):
            """删除指定的计划任务"""
            self.is_valid(raise_exception=True)
            
            task = QuerySet(ScheduleTask).filter(
                id=self.data.get('id')
            ).first()
            
            if task:
                task.delete()
                return True
            return False 