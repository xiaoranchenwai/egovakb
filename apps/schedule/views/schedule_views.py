from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from common.auth import TokenAuth, has_permissions
from common.constants.permission_constants import RoleConstants
from common.response import result
from schedule.serializers.schedule_serializer import (
    CreateScheduleTask,
    EditScheduleTask,
    ScheduleTaskSerializer
)
from schedule.serializers.record_serializer import ScheduleTaskRecordSerializer
from schedule.services.scheduler import SchedulerService
from django.utils.translation import gettext_lazy as _


class ScheduleTaskView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(
        operation_summary=_('Get schedule task list'),
        operation_id=_('Get schedule task list'),
        tags=[_('Schedule')]
    )
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request):
        return result.success(
            ScheduleTaskSerializer.Query(
                data={
                    'user_id': request.user.id,
                    'name': request.query_params.get('name'),
                    'select_user_id': request.query_params.get('select_user_id')
                }
            ).list()
        )

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(
        operation_summary=_('Create schedule task'),
        operation_id=_('Create schedule task'),
        request_body=CreateScheduleTask,
        tags=[_('Schedule')]
    )
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request):
        task_data = ScheduleTaskSerializer.Create(
            data={'user_id': request.user.id}
        ).create(request.data)
        
        # 如果任务是激活状态，添加到调度器
        if task_data.get('is_active'):
            from schedule.models import ScheduleTask
            task = ScheduleTask.objects.get(id=task_data.get('id'))
            scheduler = SchedulerService()
            scheduler.add_task(task)
            
        return result.success(task_data)

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @swagger_auto_schema(
            operation_summary=_('Update schedule task'),
            operation_id=_('Update schedule task'),
            request_body=EditScheduleTask,
            tags=[_('Schedule')]
        )
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def put(self, request, task_id):
            task_data = ScheduleTaskSerializer.Operate(
                data={'id': task_id, 'user_id': request.user.id}
            ).edit(request.data)
            
            # 更新调度器中的任务
            from schedule.models import ScheduleTask
            task = ScheduleTask.objects.get(id=task_id)
            scheduler = SchedulerService()
            
            if task.is_active:
                scheduler.add_task(task)
            else:
                scheduler.remove_task(task_id)
                
            return result.success(task_data)

        @swagger_auto_schema(
            operation_summary=_('Delete schedule task'),
            operation_id=_('Delete schedule task'),
            tags=[_('Schedule')]
        )
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def delete(self, request, task_id):
            # 验证并删除任务
            task_data = ScheduleTaskSerializer.Operate(
                data={'id': task_id, 'user_id': request.user.id}
            ).delete()
            
            # 从调度器中移除任务
            scheduler = SchedulerService()
            scheduler.remove_task(task_id)
            
            return result.success(task_data)

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @action(methods=['GET'], detail=False)
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request, current_page: int, page_size: int):
            return result.success(
                ScheduleTaskSerializer.Query(
                    data={
                        'user_id': request.user.id,
                        'name': request.query_params.get('name'),
                        'select_user_id': request.query_params.get('select_user_id'),
                        'role': request.user.role
                    }
                ).page(current_page, page_size)
            )


class ScheduleTaskRecordView(APIView):
    authentication_classes = [TokenAuth]
    
    @swagger_auto_schema(
        operation_summary=_('Get task execution records'),
        operation_id=_('Get task execution records'),
        tags=[_('Schedule')]
    )
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request, task_id):
        return result.success(
            ScheduleTaskRecordSerializer.Query(
                data={
                    'task_id': task_id,
                    'status': request.query_params.get('status')
                }
            ).list()
        )
    
    class Page(APIView):
        authentication_classes = [TokenAuth]
        
        @action(methods=['GET'], detail=False)
        @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
        def get(self, request, task_id, current_page: int, page_size: int):
            return result.success(
                ScheduleTaskRecordSerializer.Query(
                    data={
                        'task_id': task_id,
                        'status': request.query_params.get('status')
                    }
                ).page(current_page, page_size)
            )


class ScheduleTaskStatusView(APIView):
    authentication_classes = [TokenAuth]
    
    @swagger_auto_schema(
        operation_summary=_('Get task status'),
        operation_id=_('Get task status'),
        tags=[_('Schedule')]
    )
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def get(self, request, task_id):
        scheduler = SchedulerService()
        status = scheduler.get_job_status(task_id)
        
        # 获取最近一次执行记录
        from schedule.models import ScheduleTaskRecord
        last_record = ScheduleTaskRecord.objects.filter(
            task_id=task_id
        ).order_by('-start_time').first()
        
        if last_record:
            status['last_execution'] = {
                'id': last_record.id,
                'start_time': last_record.start_time,
                'end_time': last_record.end_time,
                'status': last_record.status
            }
            
        return result.success(status)


class ScheduleTaskExecuteView(APIView):
    authentication_classes = [TokenAuth]
    
    @swagger_auto_schema(
        operation_summary=_('Execute schedule task manually'),
        operation_id=_('Execute schedule task manually'),
        tags=[_('Schedule')]
    )
    @has_permissions(RoleConstants.ADMIN, RoleConstants.USER)
    def post(self, request, task_id):
        # 验证任务是否属于当前用户
        from schedule.models import ScheduleTask
        task = ScheduleTask.objects.filter(id=task_id, user_id=request.user.id).first()
        
        if not task:
            return result.error(_('Task not found or no permission'))
        
        # 执行任务
        scheduler = SchedulerService()
        success = scheduler.execute_task_manually(task_id)
        
        if success:
            return result.success({"message": _("Task execution started")})
        else:
            return result.error(_("Failed to execute task")) 