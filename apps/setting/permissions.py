from rest_framework import permissions

class GroupPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # 管理员可以访问所有分组
        if user.is_superuser:
            return True
            
        # 用户可以访问自己创建的分组
        if obj.user == user:
            return True
            
        # 用户可以访问所属分组
        if obj.groupmember_set.filter(user=user).exists():
            return True
            
        # 用户可以访问父分组的子分组
        if obj.parent and obj.parent.groupmember_set.filter(user=user).exists():
            return True
            
        return False 