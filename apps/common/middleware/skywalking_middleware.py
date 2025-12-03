# coding=utf-8
"""
    @project: MaxKB
    @Author：MaxKB
    @file： skywalking_middleware.py
    @desc: SkyWalking middleware to add custom tags
"""
from skywalking.trace.context import get_context
from skywalking.trace.tags import Tag


class NewTag(Tag):
    def __init__(self, key, val):
        self.key = key
        super().__init__(val)


class SkyWalkingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.add_tags(request)
        return response

    def add_tags(self, request):
        """
        Add custom tags to SkyWalking span
        :param request:
        :return:
        """
        try:
            # Check if user is authenticated
            # Handle cases where User object might not have is_authenticated attribute
            user = getattr(request, 'user', None)
            # If user object exists and (has is_authenticated=True OR doesn't have is_authenticated attribute at all)
            if user and getattr(user, 'is_authenticated', True):
                context = get_context()
                if context:
                    span = context.active_span
                    if span:
                        # filter-use-name: Prefer username, then nick_name
                        username = getattr(user, 'nick_name', None) or getattr(user, 'username', None)
                        if username:
                            span.tag(NewTag('filter-use-name', str(username)))
                        
                        # filter-use-phone
                        phone = getattr(user, 'phone', None)
                        if phone:
                            span.tag(NewTag('filter-use-phone', str(phone)))
        except Exception as e:
            print(f"Error adding tags to SkyWalking span: {e}")            
            # Ignore any errors during tagging to prevent impacting the request
            pass




