from django.conf.urls import url, include
from api.v5.purchaseOrders import views


urlpatterns = [
    url(r'^create-purchaseOrder/$', views.create_purchaseOrder,
        name='create_purchaseOrder'),
    url(r'^edit/purchaseOrder/(?P<pk>.*)/$',
        views.edit_purchaseOrder, name='edit_purchaseOrder'),
    url(r'^list/purchaseOrderMaster/$', views.list_purchaseOrderMaster,
        name='list_purchaseOrderMaster'),
    url(r'^view/purchaseOrderMaster/(?P<pk>.*)/$',
        views.purchaseOrderMaster, name='purchaseOrderMaster'),
    url(r'^delete/purchaseOrderMaster/(?P<pk>.*)/$',
        views.delete_purchaseOrderMaster, name='delete_purchaseOrderMaster'),
    url(r'^purchaseOrder-pagination/$', views.purchaseOrder_pagination,
        name='purchaseOrder_pagination'),
    url(r'^cancel/purchaseOrderMaster/(?P<pk>.*)/$',
        views.cancel_purchaseOrderMaster, name='cancel_purchaseOrderMaster'),

    url(r'^report/purchaseOrder/$', views.report_purchasesOrder,
        name='report_purchasesOrder'),
]
