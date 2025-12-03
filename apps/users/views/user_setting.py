from rest_framework.views import APIView, Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.translation import gettext_lazy as _
from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.response import result
from users.models.user import UserSetting
from users.serializers.user_setting_serializers import UserSettingSerializer
from smartdoc.const import CONFIG

class UserSettingView(APIView):
    authentication_classes = [TokenAuth]

    @swagger_auto_schema(
        operation_summary=_("Get user settings list"),
        operation_id=_("Get user settings list"),
        manual_parameters=[
            openapi.Parameter(
                name='settingType',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description=_("Setting Type")
            ),
            openapi.Parameter(
                name='name',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description=_("Name")
            ),
            openapi.Parameter(
                name='current_page',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description=_("Current Page")
            ),
            openapi.Parameter(
                name='page_size',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description=_("Page Size")
            )
        ],
        responses={
            200: openapi.Response(
                description=_("Success"),
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'records': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=UserSettingSerializer.get_response_body_api()
                        )
                    }
                )
            )
        },
        tags=[_("User Settings")]
    )
    @has_permissions(PermissionConstants.USER_READ)
    def get(self, request: Request):
        query = UserSettingSerializer.Query(data=request.query_params)
        query.is_valid(raise_exception=True)
        
        # 创建基础查询
        filter_kwargs = {'user_id': request.user.id}
        
        # 只在参数存在且不为空时添加过滤条件
        setting_type = request.query_params.get('settingType')
        if setting_type:
            filter_kwargs['settingType'] = setting_type
            
        name = request.query_params.get('name')
        if name:
            filter_kwargs['name__icontains'] = name

        setting = UserSetting.objects.filter(**filter_kwargs).first()
        # 使用序列化器处理数据后再返回
        data = UserSettingSerializer(setting).data if setting else None
        return result.success(data)

    @swagger_auto_schema(
        operation_summary=_("Create user setting"),
        operation_id=_("Create user setting"),
        request_body=UserSettingSerializer.Create.get_request_body_api(),
        responses=result.get_api_response(
            UserSettingSerializer.get_response_body_api()),
        tags=[_("User Settings")]
    )
    @has_permissions(PermissionConstants.USER_READ)
    def post(self, request: Request):
        serializer = UserSettingSerializer.Create(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 检查是否已存在相同类型的设置
        setting = UserSetting.objects.filter(
            user_id=request.user.id,
            setting_type=serializer.validated_data.get('setting_type'),
            name=serializer.validated_data.get('name'),
        ).first()

        if setting:
            # 如果存在，更新现有设置
            for attr, value in serializer.validated_data.items():
                setattr(setting, attr, value)
            setting.save()
        else:
            # 如果不存在，创建新设置
            setting = UserSetting.objects.create(
                user_id=request.user.id,
                **serializer.validated_data
            )
        
        return result.success(UserSettingSerializer(setting).data)

    @swagger_auto_schema(
        operation_summary=_("Update user setting"),
        operation_id=_("Update user setting"),
        request_body=UserSettingSerializer.Update.get_request_body_api(),
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="Setting ID"
            )
        ],
        responses=result.get_api_response(
            UserSettingSerializer.get_response_body_api()),
        tags=[_("User Settings")]
    )
    @has_permissions(PermissionConstants.USER_READ)
    def put(self, request: Request, id: str):
        setting = UserSetting.objects.filter(
            id=id, user_id=request.user.id).first()
        if not setting:
            return result.error(_("Setting not found"))

        serializer = UserSettingSerializer.Update(data=request.data)
        serializer.is_valid(raise_exception=True)

        for attr, value in serializer.validated_data.items():
            setattr(setting, attr, value)
        setting.save()

        return result.success(UserSettingSerializer(setting).data)

    @swagger_auto_schema(
        operation_summary=_("Delete user setting"),
        operation_id=_("Delete user setting"),
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                required=True,
                description="Setting ID"
            )
        ],
        responses=result.get_default_response(),
        tags=[_("User Settings")]
    )
    @has_permissions(PermissionConstants.USER_READ)
    def delete(self, request: Request, id: str):
        result = UserSetting.objects.filter(
            id=id, user_id=request.user.id).delete()
        return result.success(result[0] > 0)
