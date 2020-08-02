from rest_framework import serializers, status
from rest_framework.response import Response

from App.models import Customer, Goods, Cart, Address


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Customer
        fields=('id','c_name','c_email','c_is_super')

class GoodsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Goods
        fields=('id','g_name','g_price','g_num')


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Address
        fields=('id','a_addr')

class CartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Cart
        fields=('id','c_goods_id','c_user_id','c_goods_num','c_is_select')

