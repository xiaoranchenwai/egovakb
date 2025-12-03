from django.contrib import admin
from setting.models.group import Group, GroupMember, GroupDetails
from setting.models.model_management import Model
from setting.models.system_management import SystemSetting
from setting.models.team_management import Team, TeamMember, TeamMemberPermission

# Register your models here.
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupDetails)
admin.site.register(Model)
admin.site.register(SystemSetting)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(TeamMemberPermission)
