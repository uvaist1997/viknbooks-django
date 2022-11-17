from django.conf.urls import url, include
from api.v3.salesOrders import views


urlpatterns = [
    url(r'^create-salesOrder/$', views.create_salesOrder, name='create_salesOrder'),
    url(r'^edit/salesOrder/(?P<pk>.*)/$',
        views.edit_salesOrder, name='edit_salesOrder'),
    url(r'^list/salesOrderMaster/$', views.list_salesOrderMaster,
        name='list_salesOrderMaster'),
    url(r'^view/salesOrderMaster/(?P<pk>.*)/$',
        views.salesOrderMaster, name='salesOrderMaster'),
    url(r'^delete/salesOrderMaster/(?P<pk>.*)/$',
        views.delete_salesOrderMaster, name='delete_salesOrderMaster'),

    url(r'^salesOrder-pagination/$', views.salesOrder_pagination, name='salesOrder_pagination'),
]
