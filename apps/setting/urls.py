import os

from django.urls import path
from . import views
from .views import config_views

app_name = "team"

urlpatterns = [
    path('team/member', views.TeamMember.as_view(), name="team"),
    path('team/member/_batch', views.TeamMember.Batch.as_view()),
    path('team/member/<str:member_id>', views.TeamMember.Operate.as_view(), name='member'),
    path('provider/<str:provider>/<str:method>', views.Provide.Exec.as_view(), name='provide_exec'),
    path('provider', views.Provide.as_view(), name='provide'),
    path('provider/model_type_list', views.Provide.ModelTypeList.as_view(), 
         name="provider/model_type_list"),
    path('provider/model_list', views.Provide.ModelList.as_view(),
         name="provider/model_name_list"),
    path('provider/model_params_form', views.Provide.ModelParamsForm.as_view(),
         name="provider/model_params_form"),
    path('provider/model_form', views.Provide.ModelForm.as_view(),
         name="provider/model_form"),
    path('model', views.Model.as_view(), name='model'),
    path('model/<str:model_id>/model_params_form', views.Model.ModelParamsForm.as_view(),
         name='model/model_params_form'),
    path('model/<str:model_id>/http_headers', views.Model.ModelHttpHeaders.as_view(),
         name='model/http_headers'),
    path('model/<str:model_id>', views.Model.Operate.as_view(), name='model/operate'),
    path('model/<str:model_id>/pause_download', views.Model.PauseDownload.as_view(), 
         name='model/operate'),
    path('model/<str:model_id>/meta', views.Model.ModelMeta.as_view(), 
         name='model/operate/meta'),
    path('email_setting', views.SystemSetting.Email.as_view(), name='email_setting'),
    path('valid/<str:valid_type>/<int:valid_count>', views.Valid.as_view()),
    path('statistics', views.Statistics.as_view(), name='statistics'),
    path('statistics/detail', views.Statistics.Detail.as_view(), name='statistics_detail'),
    path('group', views.Group.as_view(), name='group'),
    path('group/tree', views.Group.Tree.as_view(), name='group_tree'),
    path('group/<str:group_id>', views.Group.Operate.as_view(), name='group_operate'),
    
    # 分组成员相关接口
    path('group/<str:group_id>/members', views.Group.Members.as_view(), name='group_members'),
    path('group/<str:group_id>/member', views.Group.AddMember.as_view(), name='group_add_member'),
    path('group/<str:group_id>/member/<str:user_id>', views.Group.RemoveMember.as_view(), name='group_remove_member'),
    path('group/<str:group_id>/available_users', views.Group.AvailableUsers.as_view(), name='group_available_users'),

    # GroupDetails 相关接口
    path('group-details', views.GroupDetails.as_view(), name='group_details'),
    path('group-details/batch-create', views.GroupDetails.BatchCreate.as_view(), name='group_details_batch_create'),
    path('group-details/batch-delete', views.GroupDetails.BatchDelete.as_view(), name='group_details_batch_delete'),
    path('group-details/by-group', views.GroupDetails.ByGroup.as_view(), name='group_details_by_group'),
    path('group-details/tree', views.GroupDetails.GroupDetailsTree.as_view(), name='group_details_tree'),
    path('group-details/<str:detail_id>', views.GroupDetails.Operate.as_view(), name='group_details_operate'),
    
    # 操作日志相关接口
    path('operate_log/<str:current_page>/<str:page_size>', views.OperateLog.as_view(), name='operate_log'),
    path('operate_log/menu_operate_option/', views.MenuOperateOption.as_view(), name='menu_operate_option'),
    path('operate_log/export/', views.ExportOperateLog.as_view(), name='export_operate_log'),
    
    # 动态前端配置生成接口
    path('config.js', config_views.generate_frontend_config, name='frontend_config'),
]
if os.environ.get('SERVER_NAME', 'web') == 'local_model':
    urlpatterns += [
        path('model/<str:model_id>/embed_documents', views.ModelApply.EmbedDocuments.as_view(),
             name='model/embed_documents'),
        path('model/<str:model_id>/embed_query', views.ModelApply.EmbedQuery.as_view(),
             name='model/embed_query'),
        path('model/<str:model_id>/compress_documents', views.ModelApply.CompressDocuments.as_view(),
             name='model/embed_query'),
    ]
