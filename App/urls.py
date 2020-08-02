from django.conf.urls import url

from App import views
from App.views import CustomerView, CustomersView, GoodsView, AddressView

urlpatterns=[
    url(r'^customers/$',CustomersView.as_view()),
    url(r'^customer/(?P<pk>\d+)/$',CustomerView.as_view(
        {
            'get':'list',
        }
    ),name="customer-detail"),
    url(r'^active/',views.active),#用户访问激活链接激活用户
    url(r'^goods/',GoodsView.as_view()),
    # url(r'^cart/',views.cart),
    url(r'^carts/',views.CartView.as_view(
        {
            'post':'create',
            'get':'list',
        }
    )),
    url(r'^address/',views.AddressView.as_view(
        {
            'get':'list',
            'post':'create',
        }
    )),
]