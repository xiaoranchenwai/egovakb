from django.urls import path
from . import views

app_name = "schedule"

urlpatterns = [
    path('schedule', views.ScheduleTaskView.as_view()),
    path('schedule/<str:task_id>', views.ScheduleTaskView.Operate.as_view()),
    path('schedule/<int:current_page>/<int:page_size>', 
         views.ScheduleTaskView.Page.as_view(), 
         name="schedule_page"),
    
    # 添加新的URL
    path('schedule/records/<str:task_id>', views.ScheduleTaskRecordView.as_view()),
    path('schedule/records/<str:task_id>/<int:current_page>/<int:page_size>',
         views.ScheduleTaskRecordView.Page.as_view()),
    path('schedule/status/<str:task_id>', views.ScheduleTaskStatusView.as_view()),
    path('schedule/execute/<str:task_id>', views.ScheduleTaskExecuteView.as_view()),
] 