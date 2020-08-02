import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import exceptions, status, viewsets
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from App.auth import LoginAuthencation
from App.models import Customer, Goods, Cart, Address
from App.permissions import RequireLoginPermission
from App.serializers import CustomerSerializer, GoodsSerializer, AddressSerializer, CartSerializer
from App.tasks import send_email
from DjangoSum.settings import SUPER_USER


class CustomersView(CreateAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    #重写post方法同时实现登陆和注册
    #实现登陆密码校验
    def post(self, request, *args, **kwargs):
        action=request.query_params.get('action')
        if action=='login':#登陆
            c_name=request.POST.get('c_name')
            c_password=request.POST.get('c_password')
            print(c_name,c_password)
            try:
                customer=Customer.objects.get(c_name=c_name)
                checkpwd=check_password(c_password,customer.c_password)#使用系统自带的check_password方法验证密码
                print(checkpwd,customer.c_password)
                if checkpwd:
                    token=uuid.uuid4().hex #生成token
                    print(customer.id,token)
                    cache.set(token,customer.id,timeout=60*60*2)#设置缓存,key,value的格式
                    data={
                        'status':200,
                        'msg':'login success',
                        'token':token
                    }
                    return JsonResponse(data=data)
            except:
                raise exceptions.NotFound
        elif action=='register':#注册
            return self.create(request, *args, **kwargs)
        else:
            raise exceptions.ParseError

    #重写create方法
    # 实现密码编码
    # 注册成功后发送激活邮件
    # 注册时判断是否设置为管理员
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data=serializer.data
        print(data)
        id=data.get('id')
        c_name=data.get('c_name')
        c_password = request.POST.get('c_password')#密码没有在data中返回，所以从request中获取
        customer = Customer.objects.get(pk=id)
        c_password=make_password(c_password)#使用系统加密方法进行密码加密
        customer.c_password=c_password
        if c_name in SUPER_USER:#创建管理员用户
            customer.c_is_super=True
            data.update({'c_is_super': True})#修改返回的data数据
        customer.save()
        #注册成功发送激活邮件
        c_token=uuid.uuid4().hex#生成激活邮件中的token
        cache.set(c_token,id,timeout=60*60*2)
        c_email=request.POST.get('c_email')
        send_result=send_email.delay(c_name,c_email,c_token)
        print(send_result)
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class CustomerView(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

# 用户激活
def active(request):
    c_token=request.GET.get('token')
    c_id=cache.get(c_token)
    if c_id:
        cache.delete(c_token) # 使激活码只能用一次
        costomer=Customer.objects.get(pk=c_id)
        costomer.c_is_active=True
        costomer.save()
        data={
            'status':200,
            'msg':'激活成功',
        }
        return JsonResponse(data=data)
    data={
            'status': 801,
            'msg': '激活失败或激活码已过期，请重新申请激活',
        }
    return JsonResponse(data=data)

#实现商品列表的展示和添加商品
class GoodsView(ListCreateAPIView):
    #post方法实现添加商品,get方法实现获取商品列表
    # 增加身份认证，未登陆（请求中无token）用户无法查看商品列表,非管理员用户无法添加商品
    serializer_class = GoodsSerializer
    queryset = Goods.objects.all()
    authentication_classes = (LoginAuthencation,)
    permission_classes = (RequireLoginPermission,)

    def post(self, request, *args, **kwargs):
        try:
            if request.user:
                if request.user.c_name in SUPER_USER:
                    return self.create(request, *args, **kwargs)
                else:
                    raise exceptions.NotFound
        except:
            raise exceptions.NotFound


# #实现购物车中商品数量的增加和减少
# @csrf_exempt
# def cart(request):
#     token = request.GET.get('token')  # 获取post请求中的url参数时使用GET方法
#     customerid = cache.get(token)
#     if not customerid:
#         raise exceptions.AuthenticationFailed
#     goodid=request.POST.get('good_id')
#     carts=Cart.objects.filter(c_user_id=customerid).filter(c_goods_id=goodid)
#     action=request.GET.get('action')
#     if carts.exists():
#         cart_obj = carts.first()
#         if action=='add':
#             cart_obj.c_goods_num = cart_obj.c_goods_num + 1
#         elif action=='sub' and cart_obj.c_goods_num>0:
#             cart_obj.c_goods_num = cart_obj.c_goods_num -1
#         elif cart_obj.c_goods_num==0:
#             print('不能再少了')
#         else:
#             raise exceptions.ParseError
#     else:
#         cart_obj = Cart()
#         cart_obj.c_user_id = customerid
#         cart_obj.c_goods_id = goodid
#         if action=='sub':
#             cart_obj.c_goods_num=0
#     cart_obj.save()
#     data={
#         'status':200,
#         'msg':'success',
#         'goods_num':cart_obj.c_goods_num
#     }
#     return JsonResponse(data=data)

class CartView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = (LoginAuthencation,)
    permission_classes = (RequireLoginPermission,)

    #重写create方法，实现加减购物车商品功能
    def create(self, request, *args, **kwargs):
        goodid=request.POST.get('c_goods_id')
        carts=Cart.objects.filter(c_user_id=request.user.id).filter(c_goods_id=goodid)
        action=request.GET.get('action')
        if carts.exists():
            cart_obj = carts.first()
            data = {
                'status': 200,
                'msg': 'success',
                'goods_num': cart_obj.c_goods_num
            }
            if action=='add':
                 cart_obj.c_goods_num = cart_obj.c_goods_num + 1
            elif action=='sub' and cart_obj.c_goods_num>0:
                cart_obj.c_goods_num = cart_obj.c_goods_num -1
            elif cart_obj.c_goods_num==0:
                data['goods_num']=0
            else:
                raise exceptions.ParseError
            data['goods_num']=cart_obj.c_goods_num
            cart_obj.save()
        else:
            data = {
                'status': 200,
                'msg': 'success',
            }
            if action=='sub':
                data['msg']='购物车无该商品'
            elif action=='add':
                cart_obj = Cart()
                cart_obj.c_user_id = request.user.id
                cart_obj.c_goods_id = goodid
                data['goods_num']=1
                cart_obj.save()
            else:
                raise exceptions.ParseError
        return JsonResponse(data=data)

    #重写list方法，实现每个用户只能查看自己的购物车商品数据
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset.filter(c_user_id=request.user.id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AddressView(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    authentication_classes = (LoginAuthencation,)
    permission_classes = (RequireLoginPermission,)#判断用户是否有权限，即请求中是否带有token,或token值是否存在

    # 实现地址和用户id的级联，重写ModelViewSet中CreateModelMixin中的create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        #将地址与用户id进行级联
        customer=request.user
        address_id=serializer.data.get('id')
        address=Address.objects.get(pk=address_id)
        address.a_customer_id=customer.id
        address.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 实现每个人仅能查看自己的地址，重写ModelViewSet中ListModelMixin的list方法
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset.filter(a_customer=request.user))#仅需改写此处的过滤条件

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

