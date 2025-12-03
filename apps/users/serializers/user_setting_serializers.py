from rest_framework import serializers
from users.models.user import UserSetting
from common.mixins.api_mixin import ApiMixin
from django.utils.translation import gettext_lazy as _
from common.util.field_message import ErrMessage
from drf_yasg import openapi

class UserSettingSerializer(ApiMixin, serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ['id', 'user_id', 'setting_type', 'name', 'value', 'description', 'remark', 'create_time', 'update_time']

    @staticmethod
    def get_response_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description=_("Setting ID")),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, description=_("User ID")),
                'setting_type': openapi.Schema(type=openapi.TYPE_STRING, description=_("Setting Type")),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description=_("Name")),
                'value': openapi.Schema(type=openapi.TYPE_STRING, description=_("Value")),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description=_("Description")),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description=_("Remark")),
                'create_time': openapi.Schema(type=openapi.TYPE_STRING, description=_("Create Time")),
                'update_time': openapi.Schema(type=openapi.TYPE_STRING, description=_("Update Time"))
            }
        )

    class Query(ApiMixin, serializers.Serializer):
        setting_type = serializers.CharField(required=False, allow_null=True, 
                                          error_messages=ErrMessage.char(_("Setting Type")))
        name = serializers.CharField(required=False, allow_null=True,
                                   error_messages=ErrMessage.char(_("Name")))

    class Create(ApiMixin, serializers.Serializer):
        setting_type = serializers.CharField(required=False, max_length=50,
                                          error_messages=ErrMessage.char(_("Setting Type")))
        name = serializers.CharField(required=True, max_length=100,
                                   error_messages=ErrMessage.char(_("Name")))
        value = serializers.CharField(required=True, max_length=150,
                                    error_messages=ErrMessage.char(_("Value")))
        description = serializers.CharField(required=False, max_length=50, allow_blank=True,
                                         error_messages=ErrMessage.char(_("Description")))
        remark = serializers.CharField(required=False, max_length=50, allow_blank=True,
                                     error_messages=ErrMessage.char(_("Remark")))

    class Update(ApiMixin, serializers.Serializer):
        setting_type = serializers.CharField(required=False, max_length=50,
                                          error_messages=ErrMessage.char(_("Setting Type")))
        name = serializers.CharField(required=False, max_length=100,
                                   error_messages=ErrMessage.char(_("Name")))
        value = serializers.CharField(required=False, max_length=150,
                                    error_messages=ErrMessage.char(_("Value")))
        description = serializers.CharField(required=False, max_length=50, allow_blank=True,
                                         error_messages=ErrMessage.char(_("Description")))
        remark = serializers.CharField(required=False, max_length=50, allow_blank=True,
                                     error_messages=ErrMessage.char(_("Remark"))) 