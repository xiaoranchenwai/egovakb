from rest_framework import serializers
from django.db.models import QuerySet
from schedule.models.schedule import ScheduleTaskRecord
from common.db.search import page_search


class ScheduleTaskRecordModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleTaskRecord
        fields = [
            'id', 'task_id', 'start_time', 'end_time',
            'status', 'result', 'error_message', 'create_time'
        ]


class ScheduleTaskRecordSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        task_id = serializers.UUIDField(required=True)
        status = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        
        def get_query_set(self):
            query_set = QuerySet(ScheduleTaskRecord).filter(task_id=self.data.get('task_id'))
            
            if self.data.get('status') is not None:
                query_set = query_set.filter(status=self.data.get('status'))
                
            query_set = query_set.order_by("-start_time")
            return query_set
        
        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [ScheduleTaskRecordModelSerializer(item).data for item in self.get_query_set()]
        
        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return page_search(
                current_page, 
                page_size, 
                self.get_query_set(),
                post_records_handler=lambda row: ScheduleTaskRecordModelSerializer(row).data
            ) 