from django.db import models


class Customer(models.Model):
    c_name=models.CharField(max_length=32,unique=True)
    c_password=models.CharField(max_length=128)
    c_email=models.CharField(max_length=32,unique=True)
    # c_icon=models.ImageField(upload_to='icon/%Y/%m/%d')
    c_is_active=models.BooleanField(default=False)
    c_is_delete=models.BooleanField(default=False)
    c_is_super=models.BooleanField(default=False)

class Goods(models.Model):
    g_name=models.CharField(max_length=32)
    g_price=models.FloatField(default=1)
    g_num=models.IntegerField(default=99)


class Cart(models.Model):
    c_user=models.ForeignKey(Customer,null=True,blank=True)
    c_goods=models.ForeignKey(Goods,null=True,blank=True)
    c_goods_num=models.IntegerField(default=1)
    c_is_select=models.BooleanField(default=True)


class Address(models.Model):
    a_customer=models.ForeignKey(Customer,null=True,blank=True)#先将用户id设置为空，后面再进行级联操作
    a_addr=models.CharField(max_length=128)
