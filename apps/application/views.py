from setting.models.group import Group, GroupDetails

class ApplicationViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # 管理员可以看到所有应用
        if user.is_superuser:
            return queryset
            
        # 获取用户所属的分组及其子分组
        user_groups = Group.objects.filter(
            Q(groupmember__user=user) |  # 用户所属分组
            Q(parent__groupmember__user=user)  # 父分组的子分组
        ).values_list('id', flat=True)
        
        # 获取分组内的应用ID
        app_ids = GroupDetails.objects.filter(
            group_id__in=user_groups,
            target_type='APPLICATION'
        ).values_list('target_id', flat=True)
        
        return queryset.filter(
            Q(id__in=app_ids) |  # 分组内的应用
            Q(user=user)  # 用户自己创建的应用
        ) 