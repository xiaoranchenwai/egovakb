from django.db.models import Q
from setting.models.group import Group, GroupMember

def get_user_accessible_groups(user_id):
    """获取用户可访问的所有分组ID（包括所属分组及其所有子分组）"""
    # 查找用户所属的分组
    user_group_member = GroupMember.objects.filter(user_id=user_id).first()
    
    if not user_group_member:
        return []
    
    user_group_id = user_group_member.group_id
    
    # 获取该分组及其所有子分组
    accessible_groups = [user_group_id]
    
    def get_child_groups(parent_id):
        children = Group.objects.filter(parent_id=parent_id).values_list('id', flat=True)
        for child_id in children:
            accessible_groups.append(child_id)
            get_child_groups(child_id)
    
    get_child_groups(user_group_id)
    
    return accessible_groups

def filter_by_user_groups(queryset, user_id, group_field='group_id'):
    """根据用户所属分组过滤查询集"""
    accessible_groups = get_user_accessible_groups(user_id)
    
    if not accessible_groups:
        return queryset.none()
    
    filter_kwargs = {f'{group_field}__in': accessible_groups}
    return queryset.filter(**filter_kwargs) 