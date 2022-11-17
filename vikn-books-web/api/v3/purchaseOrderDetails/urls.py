from django.conf.urls import url, include
from api.v3.purchaseOrderDetails import views


urlpatterns = [
    url(r'^create-purchaseOrderDetails/$',
        views.create_purchaseOrderDetails, name='create_purchaseOrderDetails'),
    url(r'^list/purchaseOrderDetails/$', views.list_purchaseOrderDetails,
        name='list_purchaseOrderDetails'),
    url(r'^view/purchaseOrderDetails/(?P<pk>.*)/$',
        views.purchaseOrderDetails, name='purchaseOrderDetails'),
    url(r'^edit/purchaseOrderDetails/(?P<pk>.*)/$',
        views.edit_purchaseOrderDetails, name='edit_purchaseOrderDetails'),
    url(r'^delete/purchaseOrderDetails/(?P<pk>.*)/$',
        views.delete_purchaseOrderDetails, name='delete_purchaseOrderDetails'),

    url(r'^create-purchaseOrderDetailsDummy/$',
        views.create_purchaseOrderDetailsDummy, name='create_purchaseOrderDetailsDummy'),
    url(r'^list/purchaseOrderDetailsDummy/$',
        views.list_purchaseOrderDetailsDummy, name='list_purchaseOrderDetailsDummy'),
    url(r'^edit/purchaseOrderDetailsDummy/(?P<pk>.*)/$',
        views.edit_purchaseOrderDetailsDummy, name='edit_purchaseOrderDetailsDummy'),
    url(r'^delete/purchaseOrderDetailsDummy/(?P<pk>.*)/$',
        views.delete_purchaseOrderDetailsDummy, name='delete_purchaseOrderDetailsDummy'),

    url(r'^create-DummyforEditPurchaseOrder/$',
        views.create_DummyforEditPurchaseOrder, name='create_DummyforEditPurchaseOrder'),
]
