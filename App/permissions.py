from rest_framework.permissions import BasePermission

from App.models import Customer

#判断请求是否有权限，如是否带有token,或token值是否有效
class RequireLoginPermission(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user,Customer)