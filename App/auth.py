from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from App.models import Customer

#作用：返回一个元组，格式为user,token,后面的方法则可直接用request.user来获取当前的用户
class LoginAuthencation(BaseAuthentication):
    def authenticate(self, request):
        token=request.query_params.get('token')
        try:
            customerid=cache.get(token)
            customer=Customer.objects.get(pk=customerid)
            print(token,customerid)
            return customer,token
        except:
            return
